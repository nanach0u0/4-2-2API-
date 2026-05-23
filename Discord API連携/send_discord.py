import os
import requests
from dotenv import load_dotenv

# .envから認証情報を読み込み
load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

MESSAGE = "課題6. Discord API テスト通知です🌷"

def send_discord_message(channel_id, content):
    """Discordチャンネルにメッセージを送信"""
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {
        "Authorization": f"Bot {BOT_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"content": content}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    print("✅ Discord通知の送信完了")
    print(f"  メッセージID: {data.get('id')}")
    print(f"  チャンネルID: {data.get('channel_id')}")
    print(f"  内容: {data.get('content')}")

if __name__ == "__main__":
    send_discord_message(CHANNEL_ID, MESSAGE)