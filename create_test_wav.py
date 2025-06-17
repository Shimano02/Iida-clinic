#!/usr/bin/env python3
"""
Create a proper WAV file for testing Dify integration
"""

import wave
import struct
import math

def create_test_wav():
    """Create a simple sine wave WAV file"""
    sample_rate = 44100
    duration = 1  # 1 second
    frequency = 440  # A note

    with wave.open('proper_test.wav', 'wb') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        frames = []
        for i in range(int(duration * sample_rate)):
            value = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * i / sample_rate))
            frames.append(struct.pack('<h', value))
        
        wav_file.writeframes(b''.join(frames))

    print('✅ Created proper WAV file: proper_test.wav')

if __name__ == "__main__":
    create_test_wav()
