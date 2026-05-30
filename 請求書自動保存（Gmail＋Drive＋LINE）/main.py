"""
Gmail請求書 → Google Drive保存 → LINE通知
既知の送信元（KNOWN_SENDERS）は自動保存、それ以外で請求書っぽいメールは確認通知
"""
import os
import io
import base64
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import requests

import config

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/drive.file',
]


def get_google_services():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as f:
            f.write(creds.to_json())
    gmail = build('gmail', 'v1', credentials=creds)
    drive = build('drive', 'v3', credentials=creds)
    return gmail, drive


def get_or_create_label(gmail, label_name):
    labels = gmail.users().labels().list(userId='me').execute().get('labels', [])
    for label in labels:
        if label['name'] == label_name:
            return label['id']
    new_label = gmail.users().labels().create(
        userId='me',
        body={'name': label_name, 'labelListVisibility': 'labelShow', 'messageListVisibility': 'show'}
    ).execute()
    return new_label['id']


def add_label(gmail, message_id, label_id):
    gmail.users().messages().modify(
        userId='me', id=message_id, body={'addLabelIds': [label_id]}
    ).execute()


def extract_sender_address(from_header):
    """'Notion <notify@mail.notion.so>' → 'notify@mail.notion.so'"""
    if '<' in from_header and '>' in from_header:
        return from_header.split('<')[1].split('>')[0].strip().lower()
    return from_header.strip().lower()


def get_body_text(payload):
    """メール本文（テキスト）を抽出"""
    if 'parts' in payload:
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
            if 'parts' in part:
                sub = get_body_text(part)
                if sub:
                    return sub
    elif payload.get('body', {}).get('data'):
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
    return ''


def looks_like_invoice(subject, body):
    """件名 or 本文にキーワードが含まれていれば請求書っぽいと判定"""
    text = (subject + ' ' + body).lower()
    return any(kw.lower() in text for kw in config.INVOICE_KEYWORDS)


def find_pdf_attachments(payload):
    """PDF添付ファイルを再帰的に探す"""
    pdfs = []
    if 'parts' in payload:
        for part in payload['parts']:
            if part.get('filename', '').lower().endswith('.pdf') and part.get('body', {}).get('attachmentId'):
                pdfs.append(part)
            elif 'parts' in part:
                pdfs.extend(find_pdf_attachments(part))
    return pdfs


def fetch_pdf_data(gmail, message_id, attachment_id):
    att = gmail.users().messages().attachments().get(
        userId='me', messageId=message_id, id=attachment_id
    ).execute()
    return base64.urlsafe_b64decode(att['data'])


def save_to_drive(drive, filename, data):
    media = MediaIoBaseUpload(io.BytesIO(data), mimetype='application/pdf')
    file = drive.files().create(
        body={'name': filename, 'parents': [config.DRIVE_FOLDER_ID]},
        media_body=media,
        fields='id, webViewLink'
    ).execute()
    return file['webViewLink']


def notify_line(message):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Authorization': f'Bearer {config.LINE_CHANNEL_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
    }
    payload = {
        'to': config.LINE_USER_ID,
        'messages': [{'type': 'text', 'text': message}],
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()


def main():
    print('✨ 請求書自動保存を開始します...')
    gmail, drive = get_google_services()
    saved_label_id = get_or_create_label(gmail, config.PROCESSED_LABEL)
    check_label_id = get_or_create_label(gmail, config.CHECK_PENDING_LABEL)

    result = gmail.users().messages().list(userId='me', q=config.GMAIL_QUERY).execute()
    messages = result.get('messages', [])

    if not messages:
        print('ℹ️  新しい請求書はありません')
        return

    saved = []
    pending = []

    for msg_meta in messages:
        msg = gmail.users().messages().get(userId='me', id=msg_meta['id']).execute()
        headers = msg['payload']['headers']
        from_header = next((h['value'] for h in headers if h['name'] == 'From'), '')
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(件名なし)')
        sender = extract_sender_address(from_header)
        date = datetime.fromtimestamp(int(msg['internalDate']) / 1000)
        pdfs = find_pdf_attachments(msg['payload'])
        if not pdfs:
            continue

        if sender in config.KNOWN_SENDERS:
            # ✅ 既知の送信元 → 自動保存
            source = config.KNOWN_SENDERS[sender]
            for part in pdfs:
                data = fetch_pdf_data(gmail, msg_meta['id'], part['body']['attachmentId'])
                filename = f"{date.strftime('%Y%m%d')}_{source}_{part['filename']}"
                save_to_drive(drive, filename, data)
                saved.append(f"・{source}: {filename}")
                print(f'✅ 保存完了: {filename}')
            add_label(gmail, msg_meta['id'], saved_label_id)
        else:
            # 🔍 未知の送信元 → 請求書っぽければ確認通知
            body = get_body_text(msg['payload'])
            if looks_like_invoice(subject, body):
                pending.append({
                    'sender': sender,
                    'subject': subject,
                    'filenames': [p['filename'] for p in pdfs],
                })
                add_label(gmail, msg_meta['id'], check_label_id)
                print(f'🔍 確認通知対象: {sender} / {subject}')

    # LINE通知の組み立て
    notifications = []
    if saved:
        notifications.append(f"📩 請求書を{len(saved)}件保存しました\n" + "\n".join(saved))
    for p in pending:
        notifications.append(
            f"🔍 請求書かも？というメールを検出しました\n\n"
            f"送信元：{p['sender']}\n"
            f"件名：{p['subject']}\n"
            f"添付：{', '.join(p['filenames'])}\n\n"
            f"→ 請求書だったら config.py の\n"
            f"   KNOWN_SENDERS に追記してね"
        )

    if notifications:
        notify_line("\n\n―――\n\n".join(notifications))
        print('🎉 LINE通知送信完了')
    else:
        print('ℹ️  通知対象なし')


if __name__ == '__main__':
    main()