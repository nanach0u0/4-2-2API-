import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

MESSAGE = "課題5. Slack APIから投稿テストです🌷"

def send_message(channel, text):
    client = WebClient(token=SLACK_BOT_TOKEN)
    try:
        response = client.chat_postMessage(channel=channel, text=text)
        print("✅ メッセージ送信完了")
        print(f"  チャンネル: {response['channel']}")
        print(f"  タイムスタンプ: {response['ts']}")
        print(f"  本文: {text}")
    except SlackApiError as e:
        print(f"❌ エラー: {e.response['error']}")

if __name__ == "__main__":
    send_message(CHANNEL_ID, MESSAGE)