'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Button } from '@/components/ui/button'
import { Video, Mic, Upload, File, X, AlertCircle, CheckCircle } from 'lucide-react'
import type { ScanResult } from '@/types'
import { mockScanDeepfake } from '@/lib/api'

interface DeepfakeUploadProps {
  onScan: (result: ScanResult) => void
  setIsLoading: (loading: boolean) => void
}

export function DeepfakeUpload({ onScan, setIsLoading }: DeepfakeUploadProps) {
  const [file, setFile] = useState<File | null>(null)
  const [mediaType, setMediaType] = useState<'video' | 'audio' | null>(null)
  const [preview, setPreview] = useState<string | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      setFile(file)
      
      // Determine media type
      if (file.type.startsWith('video/')) {
        setMediaType('video')
      } else if (file.type.startsWith('audio/')) {
        setMediaType('audio')
      }

      // Create preview URL
      const previewUrl = URL.createObjectURL(file)
      setPreview(previewUrl)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv'],
      'audio/*': ['.mp3', '.wav', '.m4a', '.ogg']
    },
    maxFiles: 1,
    maxSize: 100 * 1024 * 1024, // 100MB
  })

  const removeFile = () => {
    if (preview) {
      URL.revokeObjectURL(preview)
    }
    setFile(null)
    setMediaType(null)
    setPreview(null)
  }

  const handleScan = async () => {
    if (!file) return

    setIsLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('mediaType', mediaType || 'video')
      
      // Use mock for now, replace with actual API call
      const result = await mockScanDeepfake(formData)
      onScan(result)
    } catch (error) {
      console.error('Scan failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Media Type Selector */}
      <div className="flex gap-4 justify-center">
        <button
          type="button"
          onClick={() => setMediaType('video')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
            mediaType === 'video'
              ? 'bg-blue-600 text-white'
              : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
          }`}
        >
          <Video className="h-4 w-4" />
          Video
        </button>
        <button
          type="button"
          onClick={() => setMediaType('audio')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
            mediaType === 'audio'
              ? 'bg-blue-600 text-white'
              : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
          }`}
        >
          <Mic className="h-4 w-4" />
          Audio
        </button>
      </div>

      {/* Dropzone */}
      {!file ? (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all
            ${isDragActive 
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' 
              : 'border-slate-300 dark:border-slate-600 hover:border-blue-400 dark:hover:border-blue-500'
            }`}
        >
          <input {...getInputProps()} />
          <Upload className="h-12 w-12 mx-auto text-slate-400 mb-4" />
          {isDragActive ? (
            <p className="text-blue-600 dark:text-blue-400">Drop the file here...</p>
          ) : (
            <div>
              <p className="text-slate-600 dark:text-slate-300 mb-2">
                Drag & drop or click to upload
              </p>
              <p className="text-sm text-slate-400">
                Supports: MP4, AVI, MOV (Video) | MP3, WAV, M4A (Audio)
              </p>
              <p className="text-xs text-slate-400 mt-2">
                Max size: 100MB
              </p>
            </div>
          )}
        </div>
      ) : (
        // File Preview
        <div className="bg-slate-50 dark:bg-slate-700/50 rounded-xl p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              {mediaType === 'video' ? (
                <Video className="h-8 w-8 text-blue-600" />
              ) : (
                <Mic className="h-8 w-8 text-purple-600" />
              )}
              <div>
                <p className="font-medium text-slate-900 dark:text-white">{file.name}</p>
                <p className="text-sm text-slate-500">
                  {(file.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              </div>
            </div>
            <button
              onClick={removeFile}
              className="p-1 hover:bg-slate-200 dark:hover:bg-slate-600 rounded-full"
            >
              <X className="h-5 w-5 text-slate-500" />
            </button>
          </div>

          {/* Media Preview */}
          {preview && (
            <div className="mt-4 rounded-lg overflow-hidden bg-black/5">
              {mediaType === 'video' ? (
                <video src={preview} controls className="w-full max-h-64" />
              ) : (
                <audio src={preview} controls className="w-full" />
              )}
            </div>
          )}

          {/* Scan Button */}
          <Button
            onClick={handleScan}
            variant="default"
            size="lg"
            className="w-full mt-4"
          >
            Analyze for Deepfake
          </Button>
        </div>
      )}

      {/* Deepfake Examples */}
      <div className="mt-6">
        <p className="text-sm text-slate-500 dark:text-slate-400 mb-2">Example cases:</p>
        <div className="grid grid-cols-2 gap-2">
          <div className="p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <AlertCircle className="h-4 w-4 text-red-500" />
              <span className="text-sm font-medium">Deepfake Video</span>
            </div>
            <p className="text-xs text-slate-500">CEO fraud video call scam</p>
          </div>
          <div className="p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <AlertCircle className="h-4 w-4 text-red-500" />
              <span className="text-sm font-medium">Voice Cloning</span>
            </div>
            <p className="text-xs text-slate-500">Fake audio impersonation</p>
          </div>
        </div>
      </div>

      {/* Warning Message */}
      <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-medium text-yellow-800 dark:text-yellow-300 mb-1">
              Important Note
            </h4>
            <p className="text-xs text-yellow-700 dark:text-yellow-400">
              Deepfake detection analyzes visual artifacts, facial movements, and audio patterns. 
              Results are probabilistic and should be used as part of your verification process.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}