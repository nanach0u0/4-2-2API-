# Invoice Saver

Gmailに届くサブスク請求書を自動でGoogle Driveに保存し、LINEで通知するPythonスクリプト。新サービスの請求書も検知して「これ請求書？」と確認通知が届くハイブリッド方式。

## 使用API
- Gmail API
- Google Drive API
- LINE Messaging API

## セットアップ
1. `pip install -r requirements.txt`
2. Google Cloud Console で `credentials.json` をDLしてルートに配置
3. `config.py` にDriveフォルダID / LINEトークン / User IDを記入
4. `python main.py` で実行