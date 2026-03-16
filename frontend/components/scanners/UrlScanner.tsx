'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Link, Globe, AlertCircle } from 'lucide-react'
import type { UrlScanRequest, ScanResult } from '@/types'
import { scanUrl } from '@/lib/api' // This will automatically use mock since USE_MOCK=true

interface UrlScannerProps {
  onScan: (result: ScanResult) => void
  setIsLoading: (loading: boolean) => void
}

export function UrlScanner({ onScan, setIsLoading }: UrlScannerProps) {
  const { register, handleSubmit, formState: { errors } } = useForm<UrlScanRequest>()
  const [url, setUrl] = useState('')
  const [urlPreview, setUrlPreview] = useState<{
    domain: string
    protocol: string
    suspicious: boolean
  } | null>(null)

  const parseUrl = (input: string) => {
    try {
      const urlObj = new URL(input)
      setUrlPreview({
        domain: urlObj.hostname,
        protocol: urlObj.protocol.replace(':', ''),
        suspicious: checkSuspiciousPatterns(input)
      })
    } catch {
      setUrlPreview(null)
    }
  }

  const checkSuspiciousPatterns = (url: string): boolean => {
    const suspiciousPatterns = [
      'login', 'verify', 'account', 'secure', 'update', 'bank', 'paypal',
      '.xyz', '.top', 'bit.ly', 'tinyurl'
    ]
    return suspiciousPatterns.some(pattern => url.toLowerCase().includes(pattern))
  }

  const onSubmit = async (data: UrlScanRequest) => {
    setIsLoading(true)
    try {
      // This will use the mock function automatically
      const result = await scanUrl(data)
      onScan(result)
    } catch (error) {
      console.error('Scan failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="space-y-2">
        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
          Enter URL to Scan
        </label>
        <div className="relative">
          <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-slate-400" />
          <input
            {...register('url', { 
              required: 'URL is required',
              pattern: {
                value: /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/,
                message: 'Please enter a valid URL'
              }
            })}
            type="url"
            className="w-full pl-10 pr-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="https://example.com"
            value={url}
            onChange={(e) => {
              setUrl(e.target.value)
              parseUrl(e.target.value)
            }}
          />
        </div>
        {errors.url && (
          <p className="text-sm text-red-600 dark:text-red-400">{errors.url.message}</p>
        )}
      </div>

      {/* URL Preview */}
      {urlPreview && (
        <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4 space-y-3">
          <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300">URL Analysis</h4>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <p className="text-slate-500 dark:text-slate-400">Domain</p>
              <p className="font-mono text-slate-900 dark:text-white">{urlPreview.domain}</p>
            </div>
            <div>
              <p className="text-slate-500 dark:text-slate-400">Protocol</p>
              <p className="font-mono text-slate-900 dark:text-white">{urlPreview.protocol}</p>
            </div>
          </div>
          
          {urlPreview.suspicious && (
            <div className="flex items-center gap-2 p-2 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg">
              <AlertCircle className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
              <span className="text-xs text-yellow-700 dark:text-yellow-300">
                Contains potentially suspicious patterns
              </span>
            </div>
          )}
        </div>
      )}

      <Button 
        type="submit" 
        variant="default" 
        size="lg"
        className="w-full"
        disabled={url.trim() === ''}
      >
        Scan URL
      </Button>

      {/* Example URLs */}
      <div className="mt-4">
        <p className="text-sm text-slate-500 dark:text-slate-400 mb-2">Try examples:</p>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setUrl('http://secure-paypal-login.xyz/verify-account')}
            className="text-xs px-3 py-1 bg-slate-100 dark:bg-slate-700 rounded-full text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600"
          >
            Suspicious URL
          </button>
          <button
            type="button"
            onClick={() => setUrl('https://github.com/features')}
            className="text-xs px-3 py-1 bg-slate-100 dark:bg-slate-700 rounded-full text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600"
          >
            Safe URL
          </button>
        </div>
      </div>
    </form>
  )
}