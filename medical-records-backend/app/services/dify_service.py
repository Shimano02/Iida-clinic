from typing import Dict, Any
import httpx
import json
import os
import time
from datetime import datetime


class DifyService:
    """Dify ワークフロー統合サービス"""
    
    def __init__(self):
        self.api_url = os.getenv("DIFY_API_URL", "https://api.dify.ai/v1")
        self.api_key = os.getenv("DIFY_API_KEY")
        self.app_id = os.getenv("DIFY_APP_ID")
    
    async def process_with_workflow(self, audio_file_path: str, patient_data: dict = None) -> Dict[str, Any]:
        """Difyワークフローで音声を処理して医療記録を生成"""
        start_time = time.time()
        
        try:
            if not self.api_key or not self.app_id:
                raise Exception("Dify API credentials not configured")
            
            file_id = await self.upload_file(audio_file_path)
            prompt = self.create_medical_record_prompt(patient_data)
            medical_record = await self.send_workflow_request(prompt, file_id)
            
            processing_time = time.time() - start_time
            
            return {
                "medical_record": medical_record,
                "confidence_score": 0.85,
                "processing_time": round(processing_time, 2)
            }
            
        except Exception as e:
            return await self.fallback_mock_response()
    
    async def upload_file(self, audio_file_path: str) -> str:
        """音声ファイルをDifyにアップロード"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                with open(audio_file_path, 'rb') as f:
                    files = {'file': (os.path.basename(audio_file_path), f, 'audio/wav')}
                    headers = {'Authorization': f'Bearer {self.api_key}'}
                    
                    response = await client.post(
                        f"{self.api_url}/files/upload",
                        headers=headers,
                        files=files,
                        data={'user': 'medical-system'}
                    )
                    
                    if response.status_code not in [200, 201]:
                        raise Exception(f"File upload failed: {response.text}")
                    
                    result = response.json()
                    return result['id']
            except Exception as e:
                raise Exception(f"File upload to Dify failed: {str(e)}")
    
    async def send_workflow_request(self, prompt: str, file_id: str) -> dict:
        """Difyワークフローに音声ファイル付きでリクエストを送信"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
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
                f"{self.api_url}/workflows/run",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                raise Exception(f"Workflow API failed: {response.text}")
            
            result = response.json()
            
            if 'data' in result and 'outputs' in result['data']:
                outputs = result['data']['outputs']
                if 'structured_output' in outputs:
                    return self.convert_workflow_output_to_medical_record(outputs['structured_output'])
            
            return self.parse_text_response_to_medical_record(str(result))
    
    def create_medical_record_prompt(self, patient_data: dict = None) -> str:
        """医療記録生成用のプロンプトを作成"""
        base_prompt = """
        以下の診察音声を解析し、構造化された医療記録を生成してください。

        【出力形式】
        以下のJSON形式で出力してください：
        {
            "patient_id": "患者ID",
            "consultation_date": "診察日時 (YYYY-MM-DD HH:MM)",
            "chief_complaint": "主訴",
            "present_illness": "現病歴",
            "physical_examination": "身体所見",
            "diagnosis": "診断",
            "prescription": "処方",
            "guidance": "指導内容",
            "next_appointment": "次回予約",
            "notes": "備考"
        }

        【重要な指示】
        - 消化器内科・内科一般の専門用語を正確に使用
        - 音声で言及されていない情報は推測しない
        - 診断は症状と所見に基づいて論理的に記載
        - 処方は一般名で記載し、用法用量を明記
        """
        
        if patient_data:
            patient_info = f"""
        【患者情報】
        - 患者名: {patient_data.get('name', '不明')}
        - 患者ID: {patient_data.get('id', 'AUTO-GENERATED')}
        - 年齢: {patient_data.get('age', '不明')}
        - 性別: {patient_data.get('gender', '不明')}
        """
            base_prompt = patient_info + base_prompt
        
        return base_prompt
    
    def convert_workflow_output_to_medical_record(self, structured_data: dict) -> dict:
        """Difyワークフローの構造化出力を医療記録形式に変換"""
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
    
    def parse_text_response_to_medical_record(self, text_response: str) -> dict:
        """テキストレスポンスを医療記録形式に変換（フォールバック用）"""
        return {
            "patient_id": "AUTO-GENERATED",
            "consultation_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "chief_complaint": "音声解析により症状を確認中",
            "present_illness": "詳細な病歴を確認してください",
            "physical_examination": "身体所見を記録してください",
            "diagnosis": "診断を確認してください",
            "prescription": "処方内容を確認してください",
            "guidance": "生活指導を記録してください",
            "next_appointment": "次回予約を設定してください",
            "notes": f"Dify AI処理結果: {text_response[:200]}..."
        }
    
    async def fallback_mock_response(self) -> Dict[str, Any]:
        """Dify API障害時のフォールバック応答"""
        return {
            "medical_record": {
                "patient_id": "AUTO-GENERATED",
                "consultation_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "chief_complaint": "システム処理中のため、手動で入力してください",
                "present_illness": "詳細な症状経過を記録してください",
                "physical_examination": "身体所見を記録してください",
                "diagnosis": "診断を記録してください",
                "prescription": "処方内容を記録してください",
                "guidance": "患者指導内容を記録してください",
                "next_appointment": "次回予約を設定してください",
                "notes": "Dify API接続エラーのため、フォールバック応答を使用"
            },
            "confidence_score": 0.0,
            "processing_time": 0.1
        }
