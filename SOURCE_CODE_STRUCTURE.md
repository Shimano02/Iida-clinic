# ソースコード構造 - 音声自動カルテシステム

## プロジェクト構造

```
voice-medical-records/
├── README.md                           # プロジェクト概要
├── PROJECT_SPECIFICATIONS.md          # 仕様書
├── SOURCE_CODE_STRUCTURE.md          # 本ファイル
├── SETUP_INSTRUCTIONS.md             # セットアップ手順書
├── requirements.md                    # 要件定義書
├── development-flow.md               # 開発フロー
├── system-summary.md                 # システム概要
│
├── medical-records-backend/          # バックエンドアプリケーション
│   ├── pyproject.toml               # Python依存関係定義
│   ├── .env                         # 環境変数設定
│   └── app/
│       ├── __init__.py
│       └── main.py                  # FastAPIメインアプリケーション
│
├── medical-records-frontend/         # フロントエンドアプリケーション
│   ├── package.json                 # Node.js依存関係定義
│   ├── vite.config.ts              # Vite設定
│   ├── tailwind.config.js          # Tailwind CSS設定
│   ├── tsconfig.json               # TypeScript設定
│   ├── index.html                  # HTMLエントリーポイント
│   ├── .env                        # 環境変数設定
│   └── src/
│       ├── main.tsx                # Reactエントリーポイント
│       ├── App.tsx                 # メインアプリケーションコンポーネント
│       ├── App.css                 # アプリケーションスタイル
│       ├── index.css               # グローバルスタイル
│       ├── vite-env.d.ts          # Vite型定義
│       └── components/
│           └── ui/                 # shadcn/ui コンポーネント
│
└── test-files/                      # テスト関連ファイル
    ├── test_dify_integration.py    # Dify統合テスト
    ├── test_complete_integration.py # 完全統合テスト
    ├── create_test_wav.py          # テスト音声ファイル生成
    └── *.wav                       # テスト音声ファイル
```

## バックエンド詳細 (medical-records-backend/)

### pyproject.toml
```toml
[tool.poetry]
name = "medical-records-backend"
version = "0.1.0"
description = "Voice Medical Records Backend API"
authors = ["Devin AI"]

[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.104.1"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
python-multipart = "^0.0.6"
httpx = "^0.25.2"
python-dotenv = "^1.0.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### .env
```env
# Dify API設定
DIFY_API_URL=https://api.dify.ai/v1
DIFY_API_KEY=your_dify_api_key_here
DIFY_APP_ID=your_dify_app_id_here

# Google Sheets API設定 (将来使用)
GOOGLE_SHEETS_CREDENTIALS_PATH=path/to/credentials.json
GOOGLE_SHEETS_SPREADSHEET_ID=your_spreadsheet_id_here
```

### app/main.py - 主要コンポーネント

#### 1. インポートとセットアップ
```python
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import tempfile
import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="Voice Medical Records API")

# CORS設定（フロントエンド連携用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 2. データモデル
```python
class MedicalRecord(BaseModel):
    patient_id: str
    consultation_date: str
    chief_complaint: str
    present_illness: str
    physical_examination: str
    diagnosis: str
    prescription: str
    guidance: str
    next_appointment: str
    notes: str

class DifyResponse(BaseModel):
    medical_record: Dict[str, Any]
    confidence_score: float
    processing_time: float
```

#### 3. メインAPIエンドポイント
```python
@app.post("/api/process-audio")
async def process_audio(
    audio_file: UploadFile = File(...),
    patient_name: str = Form(None),
    patient_id: str = Form(None),
    patient_age: str = Form(None),
    patient_gender: str = Form(None)
):
    """
    音声ファイルと患者データを受信してDifyエージェントで処理し、医療記録を生成
    
    Args:
        audio_file: WAV音声ファイル
        patient_name: 患者名
        patient_id: 患者ID
        patient_age: 患者年齢
        patient_gender: 患者性別
    
    Returns:
        Dict: 生成された医療記録、信頼度スコア、処理時間
    """
```

#### 4. Dify統合関数
```python
async def process_with_dify_agent(audio_file_path: str, patient_data: dict = None) -> Dict[str, Any]:
    """Difyエージェントで音声を処理して医療記録を生成"""

async def upload_file_to_dify(file_path: str, api_key: str) -> str:
    """Dify APIに音声ファイルをアップロード"""

async def send_chat_to_dify(prompt: str, file_id: str, api_key: str) -> Dict[str, Any]:
    """Dify APIにチャットメッセージを送信"""

def create_medical_record_prompt(patient_data: dict = None) -> str:
    """医療記録生成用のプロンプトを作成"""
```

#### 5. ユーティリティ関数
```python
def parse_text_response_to_medical_record(text_response: str) -> Dict[str, Any]:
    """テキストレスポンスを医療記録形式に変換"""

async def fallback_mock_response() -> Dict[str, Any]:
    """Dify API障害時のフォールバック応答"""
```

## フロントエンド詳細 (medical-records-frontend/)

### package.json
```json
{
  "name": "medical-records-frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "lucide-react": "^0.294.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@typescript-eslint/eslint-plugin": "^6.14.0",
    "@typescript-eslint/parser": "^6.14.0",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "eslint": "^8.55.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6",
    "typescript": "^5.2.2",
    "vite": "^5.0.8"
  }
}
```

### src/App.tsx - 主要コンポーネント

#### 1. 状態管理
```typescript
interface PatientInfo {
  name: string;
  id: string;
  age: string;
  gender: string;
}

interface MedicalRecord {
  patient_id: string;
  consultation_date: string;
  chief_complaint: string;
  present_illness: string;
  physical_examination: string;
  diagnosis: string;
  prescription: string;
  guidance: string;
  next_appointment: string;
  notes: string;
}

const [isRecording, setIsRecording] = useState(false);
const [recordingTime, setRecordingTime] = useState(0);
const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
const [patientInfo, setPatientInfo] = useState<PatientInfo>({
  name: '田中太郎',
  id: 'P-2025-001',
  age: '45',
  gender: '男性'
});
const [medicalRecord, setMedicalRecord] = useState<MedicalRecord | null>(null);
const [isProcessing, setIsProcessing] = useState(false);
```

#### 2. 音声録音機能
```typescript
const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    
    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        setAudioBlob(event.data);
      }
    };
    
    mediaRecorder.start();
    setIsRecording(true);
    
    // タイマー開始
    const timer = setInterval(() => {
      setRecordingTime(prev => prev + 1);
    }, 1000);
    
  } catch (error) {
    console.error('マイクアクセスエラー:', error);
  }
};
```

#### 3. 音声処理・Dify連携
```typescript
const processAudio = async () => {
  if (!audioBlob) return;
  
  setIsProcessing(true);
  
  try {
    const formData = new FormData();
    formData.append('audio_file', audioBlob, 'recording.wav');
    formData.append('patient_name', patientInfo.name);
    formData.append('patient_id', patientInfo.id);
    formData.append('patient_age', patientInfo.age);
    formData.append('patient_gender', patientInfo.gender);
    
    const response = await fetch('http://localhost:8000/api/process-audio', {
      method: 'POST',
      body: formData,
    });
    
    if (response.ok) {
      const result = await response.json();
      setMedicalRecord(result.medical_record);
    }
  } catch (error) {
    console.error('音声処理エラー:', error);
  } finally {
    setIsProcessing(false);
  }
};
```

#### 4. UIコンポーネント
```typescript
// ヘッダーセクション
<div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white p-6 rounded-lg mb-6">
  <div className="flex items-center justify-between">
    <div className="flex items-center space-x-3">
      <Mic className="w-8 h-8" />
      <h1 className="text-2xl font-bold">音声カルテ自動生成システム</h1>
    </div>
    <div className="text-right">
      <p className="text-sm opacity-90">診察日</p>
      <p className="text-lg font-semibold">2025/06/12</p>
    </div>
  </div>
</div>

// 患者情報セクション
<div className="bg-white rounded-lg shadow-md p-6 mb-6">
  <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
    <User className="w-5 h-5 mr-2" />
    患者情報
  </h2>
  {/* 患者情報入力フォーム */}
</div>

// 音声録音セクション
<div className="bg-white rounded-lg shadow-md p-8 mb-6">
  <div className="text-center">
    <div className="relative inline-block mb-6">
      <div className={`w-32 h-32 rounded-full flex items-center justify-center transition-all duration-300 ${
        isRecording ? 'bg-red-500 animate-pulse' : 'bg-blue-500 hover:bg-blue-600'
      }`}>
        <Mic className="w-12 h-12 text-white" />
      </div>
    </div>
    {/* 録音コントロール */}
  </div>
</div>

// 生成カルテセクション
<div className="bg-white rounded-lg shadow-md p-6">
  <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
    <FileText className="w-5 h-5 mr-2" />
    生成カルテ
  </h2>
  {/* 医療記録表示 */}
</div>
```

## テストファイル詳細

### test_dify_integration.py
```python
#!/usr/bin/env python3
"""
Dify統合テスト
- 音声ファイル作成
- API呼び出しテスト
- レスポンス検証
"""

def create_sample_audio_file():
    """テスト用WAVファイル生成"""

def test_dify_integration():
    """Dify統合テスト実行"""

def test_backend_health():
    """バックエンドヘルスチェック"""
```

### test_complete_integration.py
```python
#!/usr/bin/env python3
"""
完全統合テスト
- エンドツーエンドテスト
- 全APIエンドポイント検証
- データフロー確認
"""

def test_complete_integration():
    """完全統合テスト実行"""
    # 1. バックエンドヘルスチェック
    # 2. 音声ファイル作成
    # 3. 音声処理テスト
    # 4. 医療記録構造検証
    # 5. 記録保存テスト
    # 6. 記録取得テスト
```

## 設定ファイル詳細

### vite.config.ts
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    host: true
  }
})
```

### tailwind.config.js
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

## 主要機能の実装詳細

### 1. 音声録音 (Web Audio API)
- MediaRecorder APIを使用
- WAV形式での録音
- リアルタイムタイマー表示
- エラーハンドリング

### 2. Dify API統合
- ファイルアップロード機能
- チャットメッセージ送信
- 構造化プロンプト生成
- レスポンス解析

### 3. 医療記録生成
- 日本語医療用語対応
- 構造化データ出力
- 消化器内科特化
- 信頼度スコア算出

### 4. エラーハンドリング
- API障害時フォールバック
- ネットワークエラー対応
- ファイル形式検証
- ユーザーフレンドリーなエラーメッセージ

### 5. UI/UX設計
- 医療スタッフ向け最適化
- 直感的な操作性
- レスポンシブデザイン
- アクセシビリティ対応

---

**文書作成日**: 2025年6月12日  
**バージョン**: 1.0  
**作成者**: Devin AI  
**対象**: 飯田クリニック音声自動カルテシステム
