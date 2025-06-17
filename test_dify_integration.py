#!/usr/bin/env python3
"""
Test script for Dify integration
Tests the /api/process-audio endpoint with sample data
"""

import requests
import json
import io
import wave
import struct
import os

def create_sample_audio_file():
    """Create a simple WAV file for testing"""
    sample_rate = 44100
    duration = 2  # seconds
    frequency = 440  # Hz (A note)
    
    frames = []
    for i in range(int(duration * sample_rate)):
        value = int(32767 * 0.3 * (i % (sample_rate // frequency)) / (sample_rate // frequency))
        frames.append(struct.pack('<h', value))
    
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(frames))
    
    wav_buffer.seek(0)
    return wav_buffer.getvalue()

def test_dify_integration():
    """Test the Dify integration endpoint"""
    print("🧪 Testing Dify Integration...")
    
    audio_data = create_sample_audio_file()
    
    files = {
        'audio_file': ('test_audio.wav', audio_data, 'audio/wav')
    }
    
    data = {
        'patient_name': '田中太郎',
        'patient_id': 'P-2025-001',
        'patient_age': '45',
        'patient_gender': '男性'
    }
    
    try:
        print("📤 Sending request to backend...")
        response = requests.post(
            'http://localhost:8000/api/process-audio',
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Dify integration working.")
            print(f"📋 Medical Record Generated:")
            print(json.dumps(result.get('medical_record', {}), indent=2, ensure_ascii=False))
            print(f"🎯 Confidence Score: {result.get('confidence_score', 'N/A')}")
            print(f"⏱️ Processing Time: {result.get('processing_time', 'N/A')}s")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get('http://localhost:8000/healthz', timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print(f"⚠️ Backend health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend not accessible: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Dify Integration Test")
    print("=" * 50)
    
    if not test_backend_health():
        print("❌ Backend is not running. Please start the backend first.")
        exit(1)
    
    success = test_dify_integration()
    
    print("=" * 50)
    if success:
        print("🎉 All tests passed! Dify integration is working.")
    else:
        print("💥 Tests failed. Check the backend logs for more details.")
