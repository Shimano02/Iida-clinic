# セットアップ・運用手順書 - 音声自動カルテシステム

## 目次
1. [システム要件](#システム要件)
2. [初期セットアップ](#初期セットアップ)
3. [環境設定](#環境設定)
4. [アプリケーション起動](#アプリケーション起動)
5. [使用方法](#使用方法)
6. [トラブルシューティング](#トラブルシューティング)
7. [メンテナンス](#メンテナンス)
8. [本番環境デプロイ](#本番環境デプロイ)

## システム要件

### 必要なソフトウェア
- **Node.js**: v18.0.0 以上
- **Python**: 3.12 以上
- **Poetry**: Python依存関係管理ツール
- **Git**: バージョン管理
- **ブラウザ**: Chrome, Firefox, Safari (最新版)

### システム要件
- **OS**: Windows 10/11, macOS 10.15+, Ubuntu 20.04+
- **RAM**: 最小 4GB, 推奨 8GB
- **ストレージ**: 最小 2GB の空き容量
- **ネットワーク**: インターネット接続必須 (Dify API使用)

## 初期セットアップ

### 1. プロジェクトのクローン
```bash
# GitHubからクローン (リポジトリが存在する場合)
git clone https://github.com/your-org/voice-medical-records.git
cd voice-medical-records

# または、プロジェクトファイルを直接配置
# プロジェクトディレクトリに移動
cd voice-medical-records
```

### 2. Node.js のインストール確認
```bash
# Node.js バージョン確認
node --version  # v18.0.0 以上であることを確認

# npm バージョン確認
npm --version

# Node.js がインストールされていない場合
# https://nodejs.org/ からダウンロードしてインストール
```

### 3. Python のインストール確認
```bash
# Python バージョン確認
python3 --version  # 3.12 以上であることを確認

# Python がインストールされていない場合
# https://www.python.org/ からダウンロードしてインストール
```

### 4. Poetry のインストール
```bash
# Poetry インストール (Linux/macOS)
curl -sSL https://install.python-poetry.org | python3 -

# Poetry インストール (Windows PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# インストール確認
poetry --version
```

## 環境設定

### 1. バックエンド環境設定

#### 依存関係のインストール
```bash
cd medical-records-backend

# Poetry を使用して依存関係をインストール
poetry install

# 仮想環境の確認
poetry env info
```

#### 環境変数の設定
```bash
# .env ファイルを作成
cp .env.example .env  # または手動で作成

# .env ファイルを編集
nano .env  # または任意のエディタで編集
```

**.env ファイルの内容:**
```env
# Dify API設定
DIFY_API_URL=https://api.dify.ai/v1
DIFY_API_KEY=app-xxxxxxxxxxxxxxxxxxxxxxxxxx
DIFY_APP_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# Google Sheets API設定 (オプション)
GOOGLE_SHEETS_CREDENTIALS_PATH=path/to/credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here

# 開発環境設定
DEBUG=true
LOG_LEVEL=info
```

### 2. フロントエンド環境設定

#### 依存関係のインストール
```bash
cd ../medical-records-frontend

# npm を使用して依存関係をインストール
npm install

# または yarn を使用する場合
# yarn install
```

#### 環境変数の設定
```bash
# .env ファイルを作成
touch .env

# .env ファイルを編集
nano .env
```

**.env ファイルの内容:**
```env
# バックエンドAPI URL
VITE_API_URL=http://localhost:8000

# 開発環境設定
VITE_NODE_ENV=development
```

## アプリケーション起動

### 1. バックエンドサーバーの起動

```bash
# バックエンドディレクトリに移動
cd medical-records-backend

# 開発サーバーを起動
poetry run fastapi dev app/main.py

# 成功時の出力例:
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process [xxxxx] using WatchFiles
# INFO:     Started server process [xxxxx]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

### 2. フロントエンドサーバーの起動

```bash
# 新しいターミナルを開いて、フロントエンドディレクトリに移動
cd medical-records-frontend

# 開発サーバーを起動
npm run dev

# 成功時の出力例:
# VITE v5.0.8  ready in 500 ms
# ➜  Local:   http://localhost:5173/
# ➜  Network: use --host to expose
# ➜  press h to show help
```

### 3. アプリケーションへのアクセス

1. ブラウザで `http://localhost:5173` にアクセス
2. 音声カルテ自動生成システムの画面が表示されることを確認
3. バックエンドAPI (`http://localhost:8000`) が正常に動作していることを確認

## 使用方法

### 1. 基本的な使用フロー

#### ステップ1: 患者情報の入力
1. 「患者情報」セクションで以下を入力:
   - **患者名**: 患者のフルネーム (例: 田中太郎)
   - **患者ID**: 形式 P-YYYY-XXX (例: P-2025-001)
   - **年齢**: 数値で入力 (例: 45)
   - **性別**: 男性/女性を選択

#### ステップ2: 音声録音
1. 「診察開始」ボタンをクリック
2. ブラウザからマイクアクセス許可を求められた場合は「許可」をクリック
3. 診察会話を録音 (最大10分)
4. 「診察終了」ボタンで録音を停止

#### ステップ3: カルテ生成
1. 録音完了後、「カルテ生成」ボタンをクリック
2. システムがDify AIで音声を処理 (通常30秒以内)
3. 生成されたカルテが「生成カルテ」セクションに表示

#### ステップ4: カルテの確認・保存
1. 生成されたカルテ内容を確認
2. 必要に応じて内容を編集
3. 「記録保存」ボタンで保存
4. 「スプレッドシート出力」でGoogle Sheetsにエクスポート (設定済みの場合)

### 2. 生成されるカルテの項目

- **診察日時**: 自動生成
- **患者ID**: 入力された患者ID
- **主訴**: 患者の主な訴え
- **現病歴**: 現在の病気の経過
- **身体所見**: 診察で確認された所見
- **診断**: 医師の診断
- **処方**: 処方された薬剤
- **指導内容**: 患者への指導
- **次回予約**: フォローアップの予定
- **備考**: その他の重要事項

### 3. 操作のコツ

#### 音声録音時の注意点
- **静かな環境**: 背景ノイズを最小限に
- **明瞭な発話**: はっきりと話す
- **適切な距離**: マイクから30cm程度
- **録音時間**: 長すぎる録音は避ける (推奨: 5分以内)

#### カルテ生成の最適化
- **患者情報の正確性**: 事前に正確な患者情報を入力
- **専門用語の使用**: 医学用語を適切に使用
- **構造化された会話**: 主訴→現病歴→診察→診断の順序で進行

## トラブルシューティング

### 1. よくある問題と解決方法

#### バックエンドが起動しない
```bash
# エラー: ModuleNotFoundError
# 解決: 依存関係を再インストール
cd medical-records-backend
poetry install

# エラー: Port already in use
# 解決: ポートを変更するか、既存プロセスを終了
lsof -ti:8000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :8000   # Windows
```

#### フロントエンドが起動しない
```bash
# エラー: npm ERR! missing script
# 解決: package.json を確認し、依存関係を再インストール
cd medical-records-frontend
rm -rf node_modules package-lock.json
npm install

# エラー: EADDRINUSE
# 解決: ポート5173が使用中の場合
npm run dev -- --port 3000
```

#### マイクアクセスが拒否される
1. **ブラウザ設定を確認**:
   - Chrome: 設定 > プライバシーとセキュリティ > サイトの設定 > マイク
   - Firefox: 設定 > プライバシーとセキュリティ > 許可設定 > マイク

2. **HTTPS接続の確認**:
   - 本番環境ではHTTPS必須
   - 開発環境ではlocalhostで動作

#### Dify API エラー
```bash
# エラー: 401 Unauthorized
# 解決: API キーを確認
# .env ファイルのDIFY_API_KEYが正しいことを確認

# エラー: 429 Too Many Requests
# 解決: API制限に達した場合は時間をおいて再試行

# エラー: 500 Internal Server Error
# 解決: Dify サービスの状態を確認、フォールバック機能が動作
```

### 2. ログの確認方法

#### バックエンドログ
```bash
# FastAPI サーバーのログを確認
# ターミナルに直接出力される

# 詳細なログが必要な場合
poetry run fastapi dev app/main.py --log-level debug
```

#### フロントエンドログ
```bash
# ブラウザの開発者ツールでコンソールを確認
# F12 キー → Console タブ

# Vite 開発サーバーのログ
# ターミナルに出力される
```

### 3. パフォーマンス問題

#### 音声処理が遅い
- **ファイルサイズ確認**: 10MB以下に制限
- **録音時間短縮**: 5分以内を推奨
- **ネットワーク確認**: インターネット接続速度

#### UI応答が遅い
- **ブラウザキャッシュクリア**: Ctrl+F5 (Windows) / Cmd+Shift+R (Mac)
- **メモリ使用量確認**: 他のアプリケーションを終了
- **ブラウザ更新**: 最新版を使用

## メンテナンス

### 1. 定期メンテナンス

#### 依存関係の更新
```bash
# バックエンド依存関係更新
cd medical-records-backend
poetry update

# フロントエンド依存関係更新
cd medical-records-frontend
npm update
```

#### ログファイルの管理
```bash
# ログファイルのローテーション (本番環境)
# logrotate 設定を使用

# 開発環境でのログクリア
# 必要に応じてログファイルを削除
```

### 2. バックアップ

#### 設定ファイルのバックアップ
```bash
# 重要な設定ファイルをバックアップ
cp medical-records-backend/.env medical-records-backend/.env.backup
cp medical-records-frontend/.env medical-records-frontend/.env.backup
```

#### データベースバックアップ (本番環境)
```bash
# 本番環境でデータベースを使用する場合
# 定期的なバックアップスクリプトを設定
```

### 3. セキュリティ更新

#### 脆弱性チェック
```bash
# Python パッケージの脆弱性チェック
cd medical-records-backend
poetry audit

# Node.js パッケージの脆弱性チェック
cd medical-records-frontend
npm audit
npm audit fix  # 自動修正可能な場合
```

## 本番環境デプロイ

### 1. 環境準備

#### 本番環境要件
- **サーバー**: Ubuntu 20.04+ または CentOS 8+
- **リバースプロキシ**: Nginx または Apache
- **SSL証明書**: Let's Encrypt または商用証明書
- **ドメイン**: 独自ドメインの設定

#### 必要なサービス
```bash
# システムパッケージ更新
sudo apt update && sudo apt upgrade -y

# 必要なシステムパッケージ
sudo apt install -y nginx postgresql redis-server supervisor

# SSL証明書 (Let's Encrypt)
sudo apt install -y certbot python3-certbot-nginx
```

### 2. アプリケーションデプロイ

#### バックエンドデプロイ
```bash
# 本番用設定ファイル作成
cp medical-records-backend/.env medical-records-backend/.env.production

# 本番環境変数設定
nano medical-records-backend/.env.production
```

**本番環境 .env.production:**
```env
# Dify API設定
DIFY_API_URL=https://api.dify.ai/v1
DIFY_API_KEY=app-your-production-api-key
DIFY_APP_ID=your-production-app-id

# データベース設定
DATABASE_URL=postgresql://user:password@localhost/medical_records

# セキュリティ設定
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# ログ設定
LOG_LEVEL=warning
LOG_FILE=/var/log/medical-records/app.log
```

#### フロントエンドビルド
```bash
cd medical-records-frontend

# 本番用環境変数設定
echo "VITE_API_URL=https://yourdomain.com/api" > .env.production

# 本番ビルド
npm run build

# ビルド結果確認
ls -la dist/
```

#### Nginx設定
```bash
# Nginx設定ファイル作成
sudo nano /etc/nginx/sites-available/medical-records
```

**Nginx設定例:**
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # フロントエンド
    location / {
        root /var/www/medical-records/dist;
        try_files $uri $uri/ /index.html;
    }

    # バックエンドAPI
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # セキュリティヘッダー
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
}
```

#### サービス設定
```bash
# Systemd サービスファイル作成
sudo nano /etc/systemd/system/medical-records-backend.service
```

**Systemd サービス設定:**
```ini
[Unit]
Description=Medical Records Backend API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/medical-records/medical-records-backend
Environment=PATH=/var/www/medical-records/medical-records-backend/.venv/bin
ExecStart=/var/www/medical-records/medical-records-backend/.venv/bin/fastapi run app/main.py --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3. SSL証明書設定
```bash
# Let's Encrypt証明書取得
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 自動更新設定
sudo crontab -e
# 以下を追加:
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### 4. サービス起動
```bash
# Nginx設定有効化
sudo ln -s /etc/nginx/sites-available/medical-records /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# バックエンドサービス起動
sudo systemctl daemon-reload
sudo systemctl enable medical-records-backend
sudo systemctl start medical-records-backend

# サービス状態確認
sudo systemctl status medical-records-backend
sudo systemctl status nginx
```

## 運用監視

### 1. ログ監視
```bash
# アプリケーションログ
tail -f /var/log/medical-records/app.log

# Nginxログ
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# システムログ
journalctl -u medical-records-backend -f
```

### 2. パフォーマンス監視
```bash
# システムリソース監視
htop
iostat -x 1
netstat -tuln

# アプリケーション監視
curl -s http://localhost:8000/healthz
```

### 3. 自動化スクリプト

#### ヘルスチェックスクリプト
```bash
#!/bin/bash
# health-check.sh

API_URL="http://localhost:8000/healthz"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $API_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "$(date): API is healthy"
else
    echo "$(date): API is down (HTTP $RESPONSE)"
    # アラート送信やサービス再起動などの処理
    sudo systemctl restart medical-records-backend
fi
```

#### バックアップスクリプト
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/medical-records"
DATE=$(date +%Y%m%d_%H%M%S)

# 設定ファイルバックアップ
mkdir -p $BACKUP_DIR/$DATE
cp -r /var/www/medical-records/.env* $BACKUP_DIR/$DATE/

# データベースバックアップ (PostgreSQL使用時)
pg_dump medical_records > $BACKUP_DIR/$DATE/database.sql

# 古いバックアップ削除 (30日以上)
find $BACKUP_DIR -type d -mtime +30 -exec rm -rf {} \;
```

## セキュリティ対策

### 1. ファイアウォール設定
```bash
# UFW設定
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw status
```

### 2. 定期セキュリティ更新
```bash
# 自動セキュリティ更新設定
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 3. アクセス制御
```bash
# SSH設定強化
sudo nano /etc/ssh/sshd_config
# PasswordAuthentication no
# PermitRootLogin no

# fail2ban設定
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

## 付録

### A. よく使用するコマンド

#### 開発環境
```bash
# バックエンド起動
cd medical-records-backend && poetry run fastapi dev app/main.py

# フロントエンド起動
cd medical-records-frontend && npm run dev

# 依存関係更新
poetry update  # バックエンド
npm update     # フロントエンド

# テスト実行
python3 test_dify_integration.py
```

#### 本番環境
```bash
# サービス状態確認
sudo systemctl status medical-records-backend
sudo systemctl status nginx

# ログ確認
journalctl -u medical-records-backend --since "1 hour ago"
tail -f /var/log/nginx/error.log

# 設定再読み込み
sudo systemctl reload nginx
sudo systemctl restart medical-records-backend
```

### B. 環境変数一覧

#### 必須環境変数
- `DIFY_API_URL`: Dify APIのベースURL
- `DIFY_API_KEY`: Dify APIキー
- `DIFY_APP_ID`: DifyアプリケーションID

#### オプション環境変数
- `GOOGLE_SHEETS_CREDENTIALS_PATH`: Google Sheets認証ファイルパス
- `GOOGLE_SHEETS_SPREADSHEET_ID`: スプレッドシートID
- `LOG_LEVEL`: ログレベル (debug, info, warning, error)
- `DEBUG`: デバッグモード (true/false)

### C. API仕様書

#### エンドポイント一覧
- `GET /healthz`: ヘルスチェック
- `POST /api/process-audio`: 音声処理
- `POST /api/save-record`: 記録保存
- `GET /api/records`: 記録取得
- `POST /api/export-to-sheets`: スプレッドシート出力

#### レスポンス形式
```json
{
  "success": true,
  "data": {},
  "message": "処理が完了しました",
  "timestamp": "2025-06-12T02:41:32Z"
}
```

### D. トラブルシューティング FAQ

#### Q: 音声が録音できない
A: ブラウザのマイク許可設定を確認してください。HTTPS環境が必要な場合があります。

#### Q: Dify APIエラーが発生する
A: APIキーの有効性とネットワーク接続を確認してください。フォールバック機能により、モックデータで動作継続します。

#### Q: カルテ生成が遅い
A: 音声ファイルサイズ（10MB以下）と録音時間（5分以内）を確認してください。

#### Q: 本番環境でHTTPS接続できない
A: SSL証明書の有効性とNginx設定を確認してください。

---

**文書作成日**: 2025年6月12日  
**バージョン**: 1.0  
**作成者**: Devin AI  
**対象**: 飯田クリニック音声自動カルテシステム

## サポート情報

### 技術サポート
- **システム要件**: Node.js 18+, Python 3.12+
- **対応ブラウザ**: Chrome, Firefox, Safari最新版
- **推奨環境**: Ubuntu 20.04+, 8GB RAM

### 連絡先
- **開発者**: Devin AI
- **プロジェクト**: 飯田クリニック音声自動カルテシステム
- **バージョン**: 1.0
- **最終更新**: 2025年6月12日

このシステムにより、飯田クリニックの診察業務効率化と記録の正確性向上を実現できます。ご不明な点がございましたら、本手順書を参照の上、適切な手順に従って操作してください。
