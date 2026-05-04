import os
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# スコープ：メール送信のみ
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

# 送信内容
TO_ADDRESS = "nanach1222@icloud.com"   # ← ここを書き換え
FROM_ADDRESS = "nanach1222@gmail.com"             # ← 自分のGmailアドレス
SUBJECT = "課題3. Gmail API テスト送信"
BODY = "Gmail API課題用のテストメールです。\n無事に届いていればOKです🌷"

def get_credentials():
    creds = None
    if os.path.exists("token_gmail.json"):
        creds = Credentials.from_authorized_user_file("token_gmail.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token_gmail.json", "w") as token:
            token.write(creds.to_json())
    return creds

def create_message(to, sender, subject, body):
    """MIMEメッセージを組み立てて、Base64urlにエンコード"""
    message = MIMEText(body, "plain", "utf-8")
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw}

def send_email(to, sender, subject, body):
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    message = create_message(to, sender, subject, body)
    sent = service.users().messages().send(userId="me", body=message).execute()

    print("✅ メール送信完了")
    print(f"  メッセージID: {sent.get('id')}")
    print(f"  宛先: {to}")
    print(f"  件名: {subject}")

if __name__ == "__main__":
    send_email(TO_ADDRESS, FROM_ADDRESS, SUBJECT, BODY)