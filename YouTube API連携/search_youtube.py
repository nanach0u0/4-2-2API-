import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

# .envからAPIキー読み込み
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

# 検索条件
SEARCH_KEYWORD = "Claude Code"   # ← ここを好きなキーワードに変更
MAX_RESULTS = 10                    # ← 取得件数（1〜50まで指定可）

def search_videos(keyword, max_results):
    # YouTube Data API クライアントを作成
    youtube = build("youtube", "v3", developerKey=API_KEY)

    # search.list で動画を検索
    request = youtube.search().list(
        part="snippet",          # タイトルや概要などの基本情報
        q=keyword,               # 検索キーワード
        type="video",            # 動画のみ（チャンネル/再生リストは除外）
        maxResults=max_results,  # 取得件数
        order="relevance",       # 関連度順（"date"にすると新着順）
    )
    response = request.execute()

    print(f"🔍 検索キーワード: {keyword}")
    print(f"📺 検索結果（{len(response['items'])}件）\n")

    for i, item in enumerate(response["items"], start=1):
        title = item["snippet"]["title"]
        video_id = item["id"]["videoId"]
        url = f"https://www.youtube.com/watch?v={video_id}"

        print(f"{i}. {title}")
        print(f"   {url}\n")

if __name__ == "__main__":
    search_videos(SEARCH_KEYWORD, MAX_RESULTS)