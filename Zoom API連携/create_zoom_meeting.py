import os
import base64
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# .envから認証情報を読み込み
load_dotenv()
ACCOUNT_ID = os.getenv("ZOOM_ACCOUNT_ID")
CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")

MEETING_TOPIC = "課題2. Zoom API テスト会議"
MEETING_AGENDA = "Zoom API課題用のテスト会議です。"

def get_access_token():
    """Server-to-Server OAuthでアクセストークンを取得"""
    url = "https://zoom.us/oauth/token"
    # Client ID:Client Secret をBase64エンコード
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_b64 = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_b64}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "account_credentials",
        "account_id": ACCOUNT_ID,
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def create_meeting(topic, agenda):
    """Zoom会議を作成"""
    token = get_access_token()

    # 開始時刻：今から5分後 / 60分間
    start_time = (datetime.now(timezone.utc) + timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%S")

    url = "https://api.zoom.us/v2/users/me/meetings"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "topic": topic,
        "type": 2,  # 2 = スケジュール会議
        "start_time": start_time,
        "duration": 60,  # 分
        "timezone": "Asia/Tokyo",
        "agenda": agenda,
        "settings": {
            "host_video": True,
            "participant_video": True,
            "join_before_host": False,
            "mute_upon_entry": True,
            "waiting_room": True,
        },
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    meeting = response.json()

    print("✅ Zoom会議の作成完了")
    print(f"  トピック: {meeting.get('topic')}")
    print(f"  会議ID: {meeting.get('id')}")
    print(f"  パスワード: {meeting.get('password')}")
    print(f"  参加リンク: {meeting.get('join_url')}")
    print(f"  ホスト用リンク: {meeting.get('start_url')}")

if __name__ == "__main__":
    create_meeting(MEETING_TOPIC, MEETING_AGENDA)