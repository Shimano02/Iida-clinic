import tempfile
import os
from typing import Optional
from fastapi import UploadFile


class AudioService:
    """音声処理サービス"""
    
    @staticmethod
    async def save_uploaded_audio(audio_file: UploadFile) -> str:
        """アップロードされた音声ファイルを一時保存"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                content = await audio_file.read()
                temp_file.write(content)
                return temp_file.name
        except Exception as e:
            raise Exception(f"Failed to save audio file: {str(e)}")
    
    @staticmethod
    def cleanup_temp_file(file_path: str) -> None:
        """一時ファイルをクリーンアップ"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            pass
    
    @staticmethod
    def validate_audio_file(audio_file: UploadFile) -> bool:
        """音声ファイルの形式を検証"""
        if not audio_file.filename:
            return False
        
        allowed_extensions = ['.wav', '.mp3', '.m4a']
        file_extension = os.path.splitext(audio_file.filename)[1].lower()
        
        return file_extension in allowed_extensions
    
    @staticmethod
    def get_audio_info(file_path: str) -> dict:
        """音声ファイルの基本情報を取得"""
        try:
            file_size = os.path.getsize(file_path)
            return {
                "file_path": file_path,
                "file_size": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2)
            }
        except Exception as e:
            return {
                "file_path": file_path,
                "file_size": 0,
                "file_size_mb": 0.0,
                "error": str(e)
            }
