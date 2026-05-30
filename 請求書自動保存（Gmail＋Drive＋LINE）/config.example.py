DRIVE_FOLDER_ID = 'YOUR_DRIVE_FOLDER_ID'
LINE_CHANNEL_ACCESS_TOKEN = 'YOUR_LINE_TOKEN'
LINE_USER_ID = 'YOUR_LINE_USER_ID'

KNOWN_SENDERS = {
    'notify@mail.notion.so': 'Notion',
    'invoice+statements@mail.anthropic.com': 'Anthropic',
}
INVOICE_KEYWORDS = [
    'invoice', 'receipt', 'subscription', 'billing', 'payment',
    '請求書', '領収書', 'お支払い', 'サブスクリプション', '請求',
]
GMAIL_QUERY = (
    'has:attachment filename:pdf newer_than:30d '
    '-label:請求書/保存済み -label:請求書/要確認'
)
PROCESSED_LABEL = '請求書/保存済み'
CHECK_PENDING_LABEL = '請求書/要確認'