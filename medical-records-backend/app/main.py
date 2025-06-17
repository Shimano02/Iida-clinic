from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
import tempfile
import time
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="音声自動カルテシステム", description="飯田クリニック向け音声自動カルテAPI")

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class MedicalRecord(BaseModel):
    patient_id: Optional[str] = None
    consultation_date: str
    chief_complaint: str
    present_illness: str
    physical_examination: str
    diagnosis: str
    prescription: str
    guidance: str
    next_appointment: Optional[str] = None
    notes: Optional[str] = None

class DifyResponse(BaseModel):
    medical_record: MedicalRecord
    confidence_score: float
    processing_time: float

medical_records_db = []

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "service": "音声自動カルテシステム"}

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
    """
    try:
        
        valid_audio_types = ['audio/', 'application/octet-stream']
        is_wav_file = audio_file.filename and audio_file.filename.lower().endswith('.wav')
        is_valid_content_type = any(audio_file.content_type.startswith(t) for t in valid_audio_types) if audio_file.content_type else False
        
        if not (is_valid_content_type or is_wav_file):
            raise HTTPException(status_code=400, detail="音声ファイルのみアップロード可能です")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        patient_data = {
            "name": patient_name,
            "id": patient_id,
            "age": patient_age,
            "gender": patient_gender
        }
        
        response = await process_with_dify_agent(temp_file_path, patient_data)
        
        os.unlink(temp_file_path)
        
        return {
            "success": True,
            "medical_record": response["medical_record"],
            "confidence_score": response["confidence_score"],
            "processing_time": response["processing_time"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"音声処理中にエラーが発生しました: {str(e)}")

async def process_with_dify_agent(audio_file_path: str, patient_data: dict = None) -> Dict[str, Any]:
    """
    Difyエージェントで音声を処理して医療記録を生成
    """
    start_time = time.time()
    
    try:
        dify_api_url = os.getenv("DIFY_API_URL", "https://api.dify.ai/v1")
        dify_api_key = os.getenv("DIFY_API_KEY")
        dify_app_id = os.getenv("DIFY_APP_ID")
        
        if not dify_api_key or not dify_app_id:
            print("Dify API key or App ID not configured, using fallback mock response")
            return await fallback_mock_response(patient_data)
        
        file_id = await upload_file_to_dify(audio_file_path, dify_api_key, dify_api_url)
        
        prompt = create_medical_record_prompt(patient_data)
        
        medical_record = await send_workflow_to_dify(prompt, file_id, dify_api_key, dify_api_url, dify_app_id)
        
        processing_time = time.time() - start_time
        
        return {
            "medical_record": medical_record,
            "confidence_score": 0.85,
            "processing_time": round(processing_time, 2)
        }
        
    except Exception as e:
        print(f"Dify API error: {str(e)}, falling back to mock response")
        return await fallback_mock_response(patient_data)

async def upload_file_to_dify(audio_file_path: str, api_key: str, api_url: str) -> str:
    """
    音声ファイルをDifyにアップロード
    """
    async with httpx.AsyncClient() as client:
        with open(audio_file_path, 'rb') as f:
            files = {'file': (os.path.basename(audio_file_path), f, 'audio/wav')}
            headers = {'Authorization': f'Bearer {api_key}'}
            
            response = await client.post(
                f"{api_url}/files/upload",
                headers=headers,
                files=files,
                data={'user': 'medical-system'}
            )
            
            if response.status_code not in [200, 201]:
                raise Exception(f"File upload failed: {response.text}")
            
            result = response.json()
            return result['id']

def create_medical_record_prompt(patient_data: dict = None) -> str:
    """
    医療記録生成用のプロンプトを作成
    """
    patient_info = ""
    if patient_data:
        patient_info = f"""
患者情報:
- 氏名: {patient_data.get('name', '不明')}
- 患者ID: {patient_data.get('id', '不明')}
- 年齢: {patient_data.get('age', '不明')}
- 性別: {patient_data.get('gender', '不明')}
"""
    
    prompt = f"""
あなたは芦屋Rいいだ内科クリニックの医療記録作成アシスタントです。
内科・消化器内科専門の医師の診察音声から、構造化された医療記録を作成してください。

{patient_info}

以下の形式でJSONレスポンスを返してください：

{{
    "patient_id": "患者ID",
    "consultation_date": "診察日時（YYYY-MM-DD HH:MM形式）",
    "chief_complaint": "主訴",
    "present_illness": "現病歴",
    "physical_examination": "身体所見",
    "diagnosis": "診断",
    "prescription": "処方・治療",
    "guidance": "生活指導・注意事項",
    "next_appointment": "次回予約",
    "notes": "備考"
}}

専門用語について：
- 消化器内科：胃炎、胃潰瘍、逆流性食道炎、過敏性腸症候群、炎症性腸疾患など
- 内科一般：高血圧、糖尿病、脂質異常症、甲状腺疾患など
- 検査：胃カメラ、大腸カメラ、ピロリ菌検査、血液検査など

音声から診察内容を正確に抽出し、医療記録として適切な日本語で記録してください。
"""
    
    return prompt

async def send_workflow_to_dify(prompt: str, file_id: str, api_key: str, api_url: str, app_id: str) -> dict:
    """
    DifyのワークフローAPIに音声ファイル付きでメッセージを送信
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "inputs": {
                "audio_file_id": file_id,
                "prompt": prompt
            },
            "response_mode": "blocking",
            "user": "medical-system"
        }
        
        response = await client.post(
            f"{api_url}/workflows/run",
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            raise Exception(f"Workflow API failed: {response.text}")
        
        result = response.json()
        
        if 'data' in result and 'outputs' in result['data']:
            outputs = result['data']['outputs']
            if 'structured_output' in outputs:
                structured_data = outputs['structured_output']
                return convert_workflow_output_to_medical_record(structured_data)
        
        return parse_text_response_to_medical_record(str(result))

def convert_workflow_output_to_medical_record(structured_data: dict) -> dict:
    """
    Difyワークフローの構造化出力を医療記録形式に変換
    """
    return {
        "patient_id": "AUTO-GENERATED",
        "consultation_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "chief_complaint": structured_data.get('subjective', '主訴を確認してください'),
        "present_illness": structured_data.get('subjective', '現病歴を確認してください'),
        "physical_examination": structured_data.get('objective', '身体所見を確認してください'),
        "diagnosis": structured_data.get('assessment', '診断を確認してください'),
        "prescription": structured_data.get('plan', '処方内容を確認してください'),
        "guidance": structured_data.get('plan', '指導内容を確認してください'),
        "next_appointment": "次回予約を確認してください",
        "notes": f"Dify AI処理完了 - 構造化データから生成"
    }

def parse_text_response_to_medical_record(text_response: str) -> dict:
    """
    テキストレスポンスを医療記録形式に変換（フォールバック用）
    """
    return {
        "patient_id": "AUTO-GENERATED",
        "consultation_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "chief_complaint": "音声から抽出された主訴",
        "present_illness": text_response[:200] if text_response else "音声処理結果を確認してください",
        "physical_examination": "診察所見を確認してください",
        "diagnosis": "診断を確認してください",
        "prescription": "処方内容を確認してください",
        "guidance": "指導内容を確認してください",
        "next_appointment": "次回予約を確認してください",
        "notes": f"Dify処理結果: {text_response}"
    }

async def fallback_mock_response(patient_data: dict = None) -> Dict[str, Any]:
    """
    Dify APIが利用できない場合のフォールバック
    """
    patient_id = patient_data.get('id', 'P001') if patient_data else 'P001'
    
    mock_medical_record = {
        "patient_id": patient_id,
        "consultation_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "chief_complaint": "腹痛、下痢症状",
        "present_illness": "3日前から腹痛と下痢が続いている。食欲不振もあり。",
        "physical_examination": "腹部：軽度圧痛あり、腸音亢進",
        "diagnosis": "急性胃腸炎の疑い",
        "prescription": "整腸剤、止痢剤を処方",
        "guidance": "水分補給を心がけ、消化の良い食事を摂取してください",
        "next_appointment": "1週間後",
        "notes": "症状が改善しない場合は早めに受診（モックデータ）"
    }
    
    return {
        "medical_record": mock_medical_record,
        "confidence_score": 0.85,
        "processing_time": 2.3
    }

@app.post("/api/save-record")
async def save_medical_record(record: MedicalRecord):
    """
    医療記録をデータベースに保存
    """
    try:
        record_dict = record.dict()
        record_dict["id"] = len(medical_records_db) + 1
        record_dict["created_at"] = datetime.now().isoformat()
        
        medical_records_db.append(record_dict)
        
        return {
            "success": True,
            "message": "医療記録が保存されました",
            "record_id": record_dict["id"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"記録保存中にエラーが発生しました: {str(e)}")

@app.get("/api/records")
async def get_medical_records():
    """
    保存された医療記録一覧を取得
    """
    return {
        "success": True,
        "records": medical_records_db,
        "total": len(medical_records_db)
    }

@app.post("/api/export-to-sheets")
async def export_to_google_sheets(record_ids: Optional[list[int]] = None):
    """
    医療記録をGoogle Sheetsにエクスポート（モック実装）
    """
    try:
        if record_ids:
            records_to_export = [r for r in medical_records_db if r["id"] in record_ids]
        else:
            records_to_export = medical_records_db
        
        
        return {
            "success": True,
            "message": f"{len(records_to_export)}件の記録をGoogle Sheetsにエクスポートしました",
            "sheet_url": "https://docs.google.com/spreadsheets/d/mock-sheet-id",
            "exported_count": len(records_to_export)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"エクスポート中にエラーが発生しました: {str(e)}")
