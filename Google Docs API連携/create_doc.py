import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# スコープ：Docs編集 + Drive（指定フォルダに作成するため）
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.file",
]

DOC_TITLE = "課題1-2. Google ドキュメント API"
DOC_BODY = "1-2. Google ドキュメント APIの課題用です。"
# 保存先フォルダID（4-2-2 API連携実践課題）
FOLDER_ID = "1goJWLtQKDJl6Wjygis4mq3vUv6n3agYZ"

def get_credentials():
    creds = None
    if os.path.exists("token_docs.json"):
        creds = Credentials.from_authorized_user_file("token_docs.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token_docs.json", "w") as token:
            token.write(creds.to_json())
    return creds

def create_doc_in_folder(title, body_text, folder_id):
    creds = get_credentials()
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    # 1. 指定フォルダの中にGoogleドキュメントを作成
    file_metadata = {
        "name": title,
        "mimeType": "application/vnd.google-apps.document",
        "parents": [folder_id],
    }
    file = drive_service.files().create(body=file_metadata, fields="id").execute()
    document_id = file.get("id")

    # 2. 本文を挿入
    docs_service.documents().batchUpdate(
        documentId=document_id,
        body={"requests": [{"insertText": {"location": {"index": 1}, "text": body_text}}]},
    ).execute()

    print("✅ ドキュメント作成完了")
    print(f"  タイトル: {title}")
    print(f"  ドキュメントID: {document_id}")
    print(f"  URL: https://docs.google.com/document/d/{document_id}/edit")

if __name__ == "__main__":
    create_doc_in_folder(DOC_TITLE, DOC_BODY, FOLDER_ID)