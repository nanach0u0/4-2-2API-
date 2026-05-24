import os
import requests
from dotenv import load_dotenv

# .envからトークンを読み込み
load_dotenv()
ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

MESSAGE = "課題7. LINE Messaging API テスト送信です🌷"

def send_broadcast(text):
    """友だち全員にメッセージを送る（broadcast）"""
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messages": [
            {"type": "text", "text": text}
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    print("✅ LINE通知の送信完了")
    print(f"  本文: {text}")
    print(f"  ステータスコード: {response.status_code}")

if __name__ == "__main__":
    send_broadcast(MESSAGE)