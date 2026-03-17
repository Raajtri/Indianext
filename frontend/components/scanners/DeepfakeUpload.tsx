'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Button } from '@/components/ui/button'
import { Video, Mic, Image, Upload, X, AlertCircle } from 'lucide-react'
import type { ScanResult } from '@/types'
import { scanDeepfake } from '@/lib/api' // Import real API, not mock

interface DeepfakeUploadProps {
  onScan: (result: ScanResult) => void
  setIsLoading: (loading: boolean) => void
}

export function DeepfakeUpload({ onScan, setIsLoading }: DeepfakeUploadProps) {
  const [file, setFile] = useState<File | null>(null)
  const [mediaType, setMediaType] = useState<'video' | 'audio' | 'image' | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setError(null)
    const file = acceptedFiles[0]
    if (file) {
      // Check file size (100MB limit)
      if (file.size > 100 * 1024 * 1024) {
        setError('File size exceeds 100MB limit')
        return
      }

      setFile(file)
      
      if (file.type.startsWith('image/')) {
    setMediaType('image')
  } else {
    setError('Only image files are allowed')
    return
}

      // Create preview URL
      const previewUrl = URL.createObjectURL(file)
      setPreview(previewUrl)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
  'image/*': ['.jpg', '.jpeg', '.png', '.webp']
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
    setError(null)
  }

  const handleScan = async () => {
    if (!file || !mediaType) return

    setIsLoading(true)
    setError(null)
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('media_type', 'image') // Changed to match backend expectation
      
      // Use real API call (not mock)
      const result = await scanDeepfake(formData)

// assuming backend returns probability (0 to 1)
    const isFake = result.probability > 0.5
      onScan(result)
    } catch (error) {
      console.error('Scan failed:', error)
      setError('Scan failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const getMediaIcon = () => {
    switch(mediaType) {
      case 'video': return <Video className="h-8 w-8 text-blue-600" />
      case 'audio': return <Mic className="h-8 w-8 text-purple-600" />
      case 'image': return <Image className="h-8 w-8 text-green-600" />
      default: return <Upload className="h-8 w-8 text-slate-400" />
    }
  }

  const getMediaTypeLabel = () => {
    switch(mediaType) {
      case 'video': return 'Video'
      case 'audio': return 'Audio'
      case 'image': return 'Image'
      default: return 'Media'
    }
  }

  return (
    <div className="space-y-6">
      {/* Media Type Selector */}
      <div className="flex gap-2 justify-center flex-wrap">
        <button
          type="button"
          onClick={() => setMediaType('image')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
            mediaType === 'image'
              ? 'bg-green-600 text-white'
              : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
          }`}
        >
          <Image className="h-4 w-4" />
          Image
        </button>
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
              ? 'bg-purple-600 text-white'
              : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
          }`}
        >
          <Mic className="h-4 w-4" />
          Audio
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-3 bg-red-100 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
        </div>
      )}

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
                Supports: Images (JPG, PNG, GIF), Videos (MP4, AVI, MOV), Audio (MP3, WAV, M4A)
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
              {getMediaIcon()}
              <div className="flex-1 min-w-0">
                <p className="font-medium text-slate-900 dark:text-white truncate">
                  {file.name}
                </p>
                <p className="text-sm text-slate-500">
                  {getMediaTypeLabel()} • {(file.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              </div>
            </div>
            <button
              onClick={removeFile}
              className="p-1 hover:bg-slate-200 dark:hover:bg-slate-600 rounded-full transition-colors"
            >
              <X className="h-5 w-5 text-slate-500" />
            </button>
          </div>

          {/* Media Preview */}
          {preview && (
            <div className="mt-4 rounded-lg overflow-hidden bg-black/5">
              {mediaType === 'video' ? (
                <video src={preview} controls className="w-full max-h-64" />
              ) : mediaType === 'audio' ? (
                <audio src={preview} controls className="w-full" />
              ) : (
                <img src={preview} alt="Preview" className="w-full max-h-64 object-contain" />
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

      {/* Example Cases */}
      <div className="mt-6">
        <p className="text-sm text-slate-500 dark:text-slate-400 mb-2">Example cases:</p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
          <div className="p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Image className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium">AI-Generated Face</span>
            </div>
            <p className="text-xs text-slate-500">Synthetic profile pictures</p>
          </div>
          <div className="p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Video className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium">Deepfake Video</span>
            </div>
            <p className="text-xs text-slate-500">CEO fraud video call scam</p>
          </div>
          <div className="p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
            <div className="flex items-center gap-2 mb-1">
              <Mic className="h-4 w-4 text-purple-600" />
              <span className="text-sm font-medium">Voice Cloning</span>
            </div>
            <p className="text-xs text-slate-500">Fake audio impersonation</p>
          </div>
        </div>
      </div>

      {/* Sample Images for Testing */}
      <div className="mt-4">
        <p className="text-sm text-slate-500 dark:text-slate-400 mb-2">Test samples (click to download):</p>
        <div className="flex flex-wrap gap-2">
          <a 
            href="https://thispersondoesnotexist.com/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-xs px-3 py-1 bg-slate-100 dark:bg-slate-700 rounded-full text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600"
          >
            AI Face (This Person Does Not Exist)
          </a>
          <a 
            href="https://www.kaggle.com/datasets" 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-xs px-3 py-1 bg-slate-100 dark:bg-slate-700 rounded-full text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600"
          >
            Deepfake Dataset
          </a>
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
              For images, we detect AI-generated faces and manipulated content.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}