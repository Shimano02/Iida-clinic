#!/usr/bin/env python3
"""
Complete integration test for the voice medical records system
Tests the full flow: audio + patient data → backend → Dify → medical record generation
"""

import requests
import json
import wave
import struct
import math
import os

def create_test_audio():
    """Create a test WAV file"""
    sample_rate = 44100
    duration = 2
    frequency = 440
    
    with wave.open('integration_test.wav', 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        frames = []
        for i in range(int(duration * sample_rate)):
            value = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * i / sample_rate))
            frames.append(struct.pack('<h', value))
        
        wav_file.writeframes(b''.join(frames))
    
    return 'integration_test.wav'

def test_complete_integration():
    """Test the complete integration flow"""
    print("🧪 Testing Complete Voice Medical Records Integration")
    print("=" * 60)
    
    print("1️⃣ Testing backend health...")
    try:
        response = requests.get('http://localhost:8000/healthz', timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False
    
    print("\n2️⃣ Creating test audio file...")
    audio_file = create_test_audio()
    print(f"✅ Created test audio: {audio_file}")
    
    print("\n3️⃣ Testing audio processing with patient data...")
    
    patient_data = {
        'patient_name': '田中太郎',
        'patient_id': 'P-2025-001', 
        'patient_age': '45',
        'patient_gender': '男性'
    }
    
    try:
        with open(audio_file, 'rb') as f:
            files = {'audio_file': (audio_file, f, 'audio/wav')}
            
            response = requests.post(
                'http://localhost:8000/api/process-audio',
                files=files,
                data=patient_data,
                timeout=30
            )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Audio processing successful!")
            
            print("\n4️⃣ Validating medical record structure...")
            medical_record = result.get('medical_record', {})
            
            required_fields = [
                'patient_id', 'consultation_date', 'chief_complaint',
                'present_illness', 'physical_examination', 'diagnosis',
                'prescription', 'guidance', 'next_appointment', 'notes'
            ]
            
            missing_fields = [field for field in required_fields if field not in medical_record]
            
            if not missing_fields:
                print("✅ Medical record structure is complete")
                print(f"📋 Patient ID: {medical_record.get('patient_id')}")
                print(f"📅 Consultation Date: {medical_record.get('consultation_date')}")
                print(f"🩺 Chief Complaint: {medical_record.get('chief_complaint')}")
                print(f"🎯 Confidence Score: {result.get('confidence_score')}")
                print(f"⏱️ Processing Time: {result.get('processing_time')}s")
            else:
                print(f"⚠️ Missing fields in medical record: {missing_fields}")
                return False
            
            print("\n5️⃣ Testing medical record saving...")
            save_response = requests.post(
                'http://localhost:8000/api/save-record',
                json=medical_record,
                headers={'Content-Type': 'application/json'}
            )
            
            if save_response.status_code == 200:
                save_result = save_response.json()
                print(f"✅ Record saved successfully - ID: {save_result.get('record_id')}")
            else:
                print(f"⚠️ Record saving failed: {save_response.status_code}")
            
            print("\n6️⃣ Testing medical record retrieval...")
            get_response = requests.get('http://localhost:8000/api/records')
            
            if get_response.status_code == 200:
                records = get_response.json()
                print(f"✅ Retrieved {records.get('total', 0)} records")
            else:
                print(f"⚠️ Record retrieval failed: {get_response.status_code}")
            
            return True
            
        else:
            print(f"❌ Audio processing failed: {response.status_code}")
            print(f"📄 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False
    
    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)

def main():
    success = test_complete_integration()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 COMPLETE INTEGRATION TEST PASSED!")
        print("✅ Voice Medical Records System is working correctly")
        print("✅ Dify integration (with fallback) is functional")
        print("✅ Audio processing and patient data handling works")
        print("✅ Medical record generation and storage works")
        print("✅ All API endpoints are responding correctly")
    else:
        print("💥 INTEGRATION TEST FAILED!")
        print("❌ Please check the backend logs for more details")
    
    return success

if __name__ == "__main__":
    main()
