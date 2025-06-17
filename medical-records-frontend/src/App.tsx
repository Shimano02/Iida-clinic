import { useState, useRef, useEffect } from 'react'
import { Mic, User, Clock, FileText, Save } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { WaveformVisualizer } from '@/components/WaveformVisualizer'
import { RealtimeTranscription } from '@/components/RealtimeTranscription'
import './App.css'

interface MedicalRecord {
  patient_id?: string
  consultation_date: string
  chief_complaint: string
  present_illness: string
  physical_examination: string
  diagnosis: string
  prescription: string
  guidance: string
  next_appointment?: string
  notes?: string
}

interface PatientInfo {
  name: string
  patient_id: string
  age: string
  gender: string
}

function App() {
  const [isRecording, setIsRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [medicalRecord, setMedicalRecord] = useState<MedicalRecord | null>(null)
  const [message, setMessage] = useState<string>('')
  const [messageType, setMessageType] = useState<'success' | 'error' | 'info'>('info')
  const [recordingTime, setRecordingTime] = useState(0)
  const [patientInfo, setPatientInfo] = useState<PatientInfo>({
    name: '田中太郎',
    patient_id: 'P-2025-001',
    age: '45',
    gender: '男性'
  })
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const audioStreamRef = useRef<MediaStream | null>(null)
  
  const [realtimeTranscript, setRealtimeTranscript] = useState('')

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }, [])

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      audioStreamRef.current = stream
      
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' })
        setAudioBlob(audioBlob)
        
        if (audioStreamRef.current) {
          audioStreamRef.current.getTracks().forEach(track => track.stop())
          audioStreamRef.current = null
        }
      }

      mediaRecorder.start()
      setIsRecording(true)
      setRecordingTime(0)
      setRealtimeTranscript('')
      setMessage('録音を開始しました')
      setMessageType('info')
      
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)
    } catch (error) {
      setMessage('マイクへのアクセスが拒否されました')
      setMessageType('error')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      setMessage('録音を停止しました')
      setMessageType('success')
      
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }
  }

  const processAudio = async () => {
    if (!audioBlob) {
      setMessage('音声データがありません')
      setMessageType('error')
      return
    }

    setIsProcessing(true)
    setMessage('音声を処理中...')
    setMessageType('info')

    try {
      const formData = new FormData()
      formData.append('audio_file', audioBlob, 'recording.wav')
      formData.append('patient_name', patientInfo.name)
      formData.append('patient_id', patientInfo.patient_id)
      formData.append('patient_age', patientInfo.age)
      formData.append('patient_gender', patientInfo.gender)

      const response = await fetch('http://localhost:8000/api/process-audio', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('音声処理に失敗しました')
      }

      const result = await response.json()
      setMedicalRecord(result.medical_record)
      setMessage(`音声処理が完了しました（信頼度: ${(result.confidence_score * 100).toFixed(1)}%）`)
      setMessageType('success')
    } catch (error) {
      setMessage('音声処理中にエラーが発生しました')
      setMessageType('error')
    } finally {
      setIsProcessing(false)
    }
  }

  const saveMedicalRecord = async () => {
    if (!medicalRecord) {
      setMessage('保存する医療記録がありません')
      setMessageType('error')
      return
    }

    try {
      const response = await fetch('http://localhost:8000/api/save-record', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(medicalRecord),
      })

      if (!response.ok) {
        throw new Error('記録の保存に失敗しました')
      }

      await response.json()
      setMessage('医療記録が保存されました')
      setMessageType('success')
    } catch (error) {
      setMessage('記録保存中にエラーが発生しました')
      setMessageType('error')
    }
  }

  const exportToExcel = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/export-to-excel', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.style.display = 'none'
        a.href = url
        a.download = `medical_records_${new Date().toISOString().slice(0, 10)}.xlsx`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        document.body.removeChild(a)
        
        setMessage('Excelファイルをダウンロードしました')
        setMessageType('success')
      } else {
        throw new Error('エクスポートに失敗しました')
      }
    } catch (error) {
      setMessage('エクスポート中にエラーが発生しました')
      setMessageType('error')
    }
  }

  const updateMedicalRecord = (field: keyof MedicalRecord, value: string) => {
    if (medicalRecord) {
      setMedicalRecord({
        ...medicalRecord,
        [field]: value
      })
    }
  }

  const updatePatientInfo = (field: keyof PatientInfo, value: string) => {
    setPatientInfo({
      ...patientInfo,
      [field]: value
    })
  }

  const getCurrentDate = () => {
    const now = new Date()
    return `${now.getFullYear()}/${(now.getMonth() + 1).toString().padStart(2, '0')}/${now.getDate().toString().padStart(2, '0')}`
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* ヘッダー */}
        <Card className="bg-white shadow-lg border-0">
          <CardHeader className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-t-lg">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                  <Mic className="h-6 w-6" />
                </div>
                <div>
                  <CardTitle className="text-2xl font-bold">
                    音声カルテ自動生成システム
                  </CardTitle>
                  <p className="text-blue-100 text-sm">AI音声認識による診察記録システム</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-blue-100">診察日</p>
                <p className="text-lg font-semibold">{getCurrentDate()}</p>
              </div>
            </div>
          </CardHeader>
        </Card>

        {/* メッセージ表示 */}
        {message && (
          <Alert className={`${messageType === 'error' ? 'border-red-500 bg-red-50' : messageType === 'success' ? 'border-green-500 bg-green-50' : 'border-blue-500 bg-blue-50'} shadow-md`}>
            <AlertDescription className="font-medium">{message}</AlertDescription>
          </Alert>
        )}

        {/* 患者情報 */}
        <Card className="bg-white shadow-lg border-0">
          <CardHeader className="bg-gray-50 border-b">
            <CardTitle className="flex items-center gap-2 text-gray-800">
              <User className="h-5 w-5" />
              患者情報
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div>
                <Label className="text-sm font-medium text-gray-600">患者名</Label>
                <Input
                  value={patientInfo.name}
                  onChange={(e) => updatePatientInfo('name', e.target.value)}
                  className="mt-1 font-semibold text-lg"
                />
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-600">患者ID</Label>
                <Input
                  value={patientInfo.patient_id}
                  onChange={(e) => updatePatientInfo('patient_id', e.target.value)}
                  className="mt-1 font-semibold text-lg"
                />
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-600">年齢</Label>
                <Input
                  value={patientInfo.age}
                  onChange={(e) => updatePatientInfo('age', e.target.value)}
                  className="mt-1 font-semibold text-lg"
                />
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-600">性別</Label>
                <Input
                  value={patientInfo.gender}
                  onChange={(e) => updatePatientInfo('gender', e.target.value)}
                  className="mt-1 font-semibold text-lg"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 音声録音セクション */}
        <Card className="bg-white shadow-lg border-0">
          <CardContent className="p-8">
            <div className="flex flex-col items-center space-y-6">
              {/* 円形マイクボタン */}
              <div className="relative">
                <div className={`w-32 h-32 rounded-full flex items-center justify-center transition-all duration-300 ${
                  isRecording 
                    ? 'bg-gradient-to-br from-red-400 to-red-600 shadow-lg shadow-red-200 animate-pulse' 
                    : 'bg-gradient-to-br from-blue-400 to-blue-600 shadow-lg shadow-blue-200'
                }`}>
                  <Mic className="h-12 w-12 text-white" />
                </div>
                {isRecording && (
                  <div className="absolute -inset-4 rounded-full border-4 border-red-300 animate-ping"></div>
                )}
              </div>

              {/* タイマー表示 */}
              <div className="flex items-center gap-2 text-2xl font-mono font-bold text-gray-700">
                <Clock className="h-6 w-6" />
                {formatTime(recordingTime)}
              </div>

              {/* ステータス表示 */}
              <div className="text-center">
                <p className="text-lg font-medium text-gray-600">
                  {isRecording ? '録音中' : isProcessing ? '処理中' : '待機中'}
                </p>
              </div>

              {/* 制御ボタン */}
              <div className="flex gap-4">
                <Button
                  onClick={startRecording}
                  disabled={isRecording || isProcessing}
                  size="lg"
                  className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 text-lg font-semibold shadow-lg"
                >
                  診察開始
                </Button>
                
                <Button
                  onClick={stopRecording}
                  disabled={!isRecording}
                  size="lg"
                  variant="destructive"
                  className="bg-red-600 hover:bg-red-700 text-white px-8 py-3 text-lg font-semibold shadow-lg"
                >
                  診察終了
                </Button>
              </div>

              {/* Real-time Audio Display */}
              {isRecording && (
                <div className="space-y-4 w-full">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <div>
                      <h3 className="text-sm font-medium text-gray-700 mb-2">音声波形</h3>
                      <WaveformVisualizer 
                        audioStream={audioStreamRef.current}
                        isRecording={isRecording}
                        width={400}
                        height={100}
                      />
                    </div>
                    <div>
                      <RealtimeTranscription 
                        isRecording={isRecording}
                        onTranscriptUpdate={setRealtimeTranscript}
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* 音声処理ボタン */}
              {audioBlob && !isRecording && (
                <Button
                  onClick={processAudio}
                  disabled={isProcessing}
                  size="lg"
                  variant="outline"
                  className="border-2 border-blue-600 text-blue-600 hover:bg-blue-50 px-8 py-3 text-lg font-semibold"
                >
                  {isProcessing ? '処理中...' : 'カルテ生成'}
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* 生成カルテ */}
        <Card className="bg-white shadow-lg border-0">
          <CardHeader className="bg-gray-50 border-b">
            <CardTitle className="flex items-center gap-2 text-gray-800">
              <FileText className="h-5 w-5" />
              生成カルテ
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            {medicalRecord ? (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm font-medium text-gray-600">患者ID</Label>
                    <Input
                      value={medicalRecord.patient_id || ''}
                      onChange={(e) => updateMedicalRecord('patient_id', e.target.value)}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-600">診察日時</Label>
                    <Input
                      value={medicalRecord.consultation_date}
                      onChange={(e) => updateMedicalRecord('consultation_date', e.target.value)}
                      className="mt-1"
                    />
                  </div>
                </div>

                <div>
                  <Label className="text-sm font-medium text-gray-600">主訴</Label>
                  <Textarea
                    value={medicalRecord.chief_complaint}
                    onChange={(e) => updateMedicalRecord('chief_complaint', e.target.value)}
                    rows={2}
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label className="text-sm font-medium text-gray-600">現病歴</Label>
                  <Textarea
                    value={medicalRecord.present_illness}
                    onChange={(e) => updateMedicalRecord('present_illness', e.target.value)}
                    rows={3}
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label className="text-sm font-medium text-gray-600">身体所見</Label>
                  <Textarea
                    value={medicalRecord.physical_examination}
                    onChange={(e) => updateMedicalRecord('physical_examination', e.target.value)}
                    rows={2}
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label className="text-sm font-medium text-gray-600">診断</Label>
                  <Textarea
                    value={medicalRecord.diagnosis}
                    onChange={(e) => updateMedicalRecord('diagnosis', e.target.value)}
                    rows={2}
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label className="text-sm font-medium text-gray-600">処方</Label>
                  <Textarea
                    value={medicalRecord.prescription}
                    onChange={(e) => updateMedicalRecord('prescription', e.target.value)}
                    rows={2}
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label className="text-sm font-medium text-gray-600">指導内容</Label>
                  <Textarea
                    value={medicalRecord.guidance}
                    onChange={(e) => updateMedicalRecord('guidance', e.target.value)}
                    rows={2}
                    className="mt-1"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm font-medium text-gray-600">次回予約</Label>
                    <Input
                      value={medicalRecord.next_appointment || ''}
                      onChange={(e) => updateMedicalRecord('next_appointment', e.target.value)}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label className="text-sm font-medium text-gray-600">備考</Label>
                    <Input
                      value={medicalRecord.notes || ''}
                      onChange={(e) => updateMedicalRecord('notes', e.target.value)}
                      className="mt-1"
                    />
                  </div>
                </div>

                <div className="flex gap-4 justify-center pt-6 border-t">
                  <Button
                    onClick={saveMedicalRecord}
                    className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 font-semibold shadow-md"
                  >
                    <Save className="h-4 w-4 mr-2" />
                    記録保存
                  </Button>
                  
                  <Button
                    onClick={exportToExcel}
                    variant="outline"
                    className="border-2 border-green-600 text-green-600 hover:bg-green-50 px-6 py-2 font-semibold"
                  >
                    <FileText className="h-4 w-4 mr-2" />
                    Excel出力
                  </Button>
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <FileText className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-lg">診察を開始してカルテを生成してください</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default App
