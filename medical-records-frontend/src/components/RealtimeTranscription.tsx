import React, { useEffect, useRef, useState } from 'react';

interface RealtimeTranscriptionProps {
  isRecording: boolean;
  onTranscriptUpdate?: (transcript: string) => void;
}

export const RealtimeTranscription: React.FC<RealtimeTranscriptionProps> = ({
  isRecording,
  onTranscriptUpdate
}) => {
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [isSupported, setIsSupported] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || (window as any).webkitSpeechRecognition;
    setIsSupported(!!SpeechRecognition);

    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      setupRecognition();
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  useEffect(() => {
    if (!recognitionRef.current || !isSupported) return;

    if (isRecording) {
      startRecognition();
    } else {
      stopRecognition();
    }
  }, [isRecording, isSupported]);

  const setupRecognition = () => {
    if (!recognitionRef.current) return;

    recognitionRef.current.continuous = true;
    recognitionRef.current.interimResults = true;
    recognitionRef.current.lang = 'ja-JP';

    recognitionRef.current.onresult = (event: SpeechRecognitionEvent) => {
      let finalTranscript = '';
      let interimTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalTranscript += result[0].transcript;
        } else {
          interimTranscript += result[0].transcript;
        }
      }

      if (finalTranscript) {
        setTranscript(prev => prev + finalTranscript);
        onTranscriptUpdate?.(transcript + finalTranscript);
      }
      setInterimTranscript(interimTranscript);
    };

    recognitionRef.current.onerror = (event: SpeechRecognitionErrorEvent) => {
      console.error('Speech recognition error:', event.error);
    };

    recognitionRef.current.onend = () => {
      if (isRecording) {
        setTimeout(() => startRecognition(), 100);
      }
    };
  };

  const startRecognition = () => {
    try {
      recognitionRef.current?.start();
    } catch (error) {
      console.error('Error starting speech recognition:', error);
    }
  };

  const stopRecognition = () => {
    try {
      recognitionRef.current?.stop();
    } catch (error) {
      console.error('Error stopping speech recognition:', error);
    }
  };

  if (!isSupported) {
    return (
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-yellow-800">音声認識はこのブラウザではサポートされていません。</p>
      </div>
    );
  }

  return (
    <div className="p-4 bg-white border border-gray-200 rounded-lg min-h-[120px]">
      <h3 className="text-sm font-medium text-gray-700 mb-2">リアルタイム音声認識</h3>
      <div className="text-sm text-gray-900">
        <span>{transcript}</span>
        <span className="text-gray-500 italic">{interimTranscript}</span>
        {isRecording && <span className="animate-pulse">|</span>}
      </div>
    </div>
  );
};
