# Anniversary Notify

Notionで管理する記念日DBを毎朝読み取り、逆算して「グッドなタイミング」でLINEに通知を送るPythonスクリプト。
GitHub Actionsによるクラウド自動実行対応。

## 使用API
- Notion API
- LINE Messaging API
- GitHub Actions（cron）

## セットアップ
1. `pip install -r requirements.txt`
2. `.env.example` をコピーして `.env` を作成し、各トークンを設定
3. Notionで記念日DBを作成し、コネクトを追加
4. `python anniversary_notify.py` で実行

## GitHub Actionsでの自動実行
- Settings → Secrets and variables → Actions で NOTION_TOKEN / NOTION_DATABASE_ID / LINE_CHANNEL_ACCESS_TOKEN を登録
- `.github/workflows/notify.yml` により毎朝9:00 JSTに自動実行