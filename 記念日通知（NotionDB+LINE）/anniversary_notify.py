"""
Notion記念日DB → 逆算判定 → LINE通知
毎朝実行され、該当する記念日があればLINEに通知を送る
"""
import os
from datetime import date
from notion_client import Client
import requests
from dotenv import load_dotenv

# 環境変数読み込み（ローカルは.env、GitHub ActionsではSecrets）
load_dotenv()
NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["NOTION_DATABASE_ID"]
LINE_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]

# 通知タイミングの文字列 → 逆算日数
TIMING_MAP = {
    "90日前": 90,
    "60日前": 60,
    "30日前": 30,
    "7日前": 7,
    "3日前": 3,
    "前日": 1,
    "当日": 0,
}


def shift_to_this_year(anniv_date: date, today: date) -> date:
    """記念日の年を今年に置き換える（2/29は平年なら全て2/28に読み替え）"""
    try:
        return anniv_date.replace(year=today.year)
    except ValueError:
        return date(today.year, 2, 28)


def query_anniversaries(notion: Client):
    """記念日DBの全件を取得する（Notion API 2025-09-03以降の data_sources 対応）"""
    # まずDBから data_source_id を取得（1つのDBは1つ以上の data_source を持つ構造）
    db = notion.databases.retrieve(database_id=DATABASE_ID)
    data_source_id = db["data_sources"][0]["id"]

    results = []
    cursor = None
    while True:
        response = notion.data_sources.query(
            data_source_id=data_source_id,
            start_cursor=cursor,
        ) if cursor else notion.data_sources.query(data_source_id=data_source_id)
        results.extend(response["results"])
        if not response.get("has_more"):
            break
        cursor = response["next_cursor"]
    return results


def extract_text(prop, key="title"):
    """title / rich_text プロパティからテキストを取り出す"""
    items = prop.get(key, [])
    return "".join([i.get("plain_text", "") for i in items])


def build_notifications(pages, today: date):
    """各レコードを逆算し、今日通知すべきメッセージを組み立てる"""
    notifications = []
    for page in pages:
        props = page["properties"]
        name = extract_text(props.get("名前", {}), "title")
        date_prop = props.get("日付", {}).get("date")
        if not date_prop or not date_prop.get("start"):
            continue
        anniv = date.fromisoformat(date_prop["start"][:10])
        this_year_anniv = shift_to_this_year(anniv, today)

        timings = [t["name"] for t in props.get("通知タイミング", {}).get("multi_select", [])]
        memo = extract_text(props.get("備考", {}), "rich_text")

        for t in timings:
            days = TIMING_MAP.get(t)
            if days is None:
                continue
            target_date = this_year_anniv.fromordinal(this_year_anniv.toordinal() - days)
            if target_date == today:
                if days == 0:
                    line = f"・{name}は今日！🎉 おめでとうございます！"
                else:
                    line = f"・{name}まであと{days}日"
                if memo:
                    line += f"\n  📝 {memo}"
                notifications.append(line)
    return notifications


def send_line(text: str):
    """LINEにブロードキャストで送信"""
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"messages": [{"type": "text", "text": text}]}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()


def main():
    print("✨ 記念日通知処理を開始します...")
    today = date.today()
    print(f"  今日の日付: {today}")

    notion = Client(auth=NOTION_TOKEN)
    pages = query_anniversaries(notion)
    print(f"  DB取得件数: {len(pages)}件")

    notifications = build_notifications(pages, today)
    if not notifications:
        print("ℹ️  今日通知する記念日はありません")
        return

    message = "🌷 もうすぐ記念日のお知らせ\n\n" + "\n".join(notifications)
    send_line(message)
    print(f"🎉 LINE通知送信完了（{len(notifications)}件）")


if __name__ == "__main__":
    main()