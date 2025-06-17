# 音声自動カルテシステム - 飯田クリニック向け

## 概要
飯田クリニック向けの音声自動カルテシステムです。診察中の医師と患者の会話を自動的に医療記録として転記し、スプレッドシートに出力するシステムです。

## システム構成
- **フロントエンド**: React 18 + TypeScript + Vite + Tailwind CSS
- **バックエンド**: FastAPI + Python + Poetry
- **AI処理**: Dify API連携
- **データ出力**: Google Sheets API連携

## セットアップ

### 環境変数設定
バックエンドの `.env` ファイルに以下を設定してください：

```env
DIFY_API_URL=https://api.dify.ai/v1
DIFY_API_KEY=your_dify_api_key_here
DIFY_APP_ID=your_dify_app_id_here
```

### バックエンド起動
```bash
cd medical-records-backend
poetry install
poetry run fastapi dev app/main.py
```

### フロントエンド起動
```bash
cd medical-records-frontend
npm install
npm run dev
```

## 使用方法
1. ブラウザで http://localhost:5173/ にアクセス
2. 患者情報を入力
3. 「診察開始」ボタンで音声録音を開始
4. 「診察終了」で録音を停止
5. 「カルテ生成」でDifyエージェントによる医療記録生成
6. 生成された医療記録を確認・編集
7. 「記録保存」で保存、「スプレッドシート出力」でエクスポート

## API エンドポイント
- `POST /api/process-audio` - 音声ファイルと患者データの処理
- `POST /api/save-record` - 医療記録保存
- `GET /api/records` - 記録一覧取得
- `POST /api/export-to-sheets` - スプレッドシート出力

## Dify連携
システムはDify APIを使用して音声データを処理し、構造化された医療記録を生成します。Dify APIが利用できない場合は、自動的にモックデータにフォールバックします。

## 医療記録フォーマット
- 診察日時、患者ID、主訴、現病歴
- 身体所見、診断、処方、指導内容
- 次回予約、備考

## 飯田クリニック特化機能
- 消化器内科・内科専門用語対応
- 日本語医療記録フォーマット
- 胃カメラ・大腸カメラ等の検査対応
- 生活習慣病管理機能
