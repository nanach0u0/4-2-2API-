import os
import uuid
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Calendar APIのスコープ（イベント作成＋Meetリンク発行に必要）
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

EVENT_TITLE = "課題1-3. Google Meet API テスト会議"
EVENT_DESCRIPTION = "1-3. Google Meet APIの課題用ミーティングです。"
TIMEZONE = "Asia/Tokyo"

def get_credentials():
    creds = None
    if os.path.exists("token_meet.json"):
        creds = Credentials.from_authorized_user_file("token_meet.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token_meet.json", "w") as token:
            token.write(creds.to_json())
    return creds

def create_meet_event(title, description):
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    # 1時間後スタート、1時間の会議として作成
    start = datetime.now() + timedelta(hours=1)
    end = start + timedelta(hours=1)

    event = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start.isoformat(), "timeZone": TIMEZONE},
        "end": {"dateTime": end.isoformat(), "timeZone": TIMEZONE},
        "conferenceData": {
            "createRequest": {
                "requestId": str(uuid.uuid4()),  # Meet作成のリクエスト識別子（適当でOK）
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
    }

    created = service.events().insert(
        calendarId="primary",        # 自分のメインカレンダー
        body=event,
        conferenceDataVersion=1,     # ← これを忘れるとMeetリンクが付かない！
    ).execute()

    print("✅ Google Meet 会議作成完了")
    print(f"  タイトル   : {created.get('summary')}")
    print(f"  開始       : {created['start']['dateTime']}")
    print(f"  終了       : {created['end']['dateTime']}")
    print(f"  Meetリンク : {created.get('hangoutLink')}")
    print(f"  会議ID     : {created.get('conferenceData', {}).get('conferenceId')}")
    print(f"  カレンダー : {created.get('htmlLink')}")

if __name__ == "__main__":
    create_meet_event(EVENT_TITLE, EVENT_DESCRIPTION)