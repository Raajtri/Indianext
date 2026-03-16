'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Mail, Send } from 'lucide-react'
import type { EmailScanRequest, ScanResult } from '@/types'
import { scanEmail } from '@/lib/api'

interface EmailScannerProps {
  onScan: (result: ScanResult) => void
  setIsLoading: (loading: boolean) => void
}

export function EmailScanner({ onScan, setIsLoading }: EmailScannerProps) {
  const { register, handleSubmit, formState: { errors } } = useForm<EmailScanRequest>()
  const [emailText, setEmailText] = useState('')

  const onSubmit = async (data: EmailScanRequest) => {
    setIsLoading(true)
    try {
      const result = await scanEmail(data)
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
          Paste Email Content
        </label>
        <textarea
          {...register('emailText', { required: 'Email content is required' })}
          rows={8}
          className="w-full px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Paste the email content here..."
          value={emailText}
          onChange={(e) => setEmailText(e.target.value)}
        />
        {errors.emailText && (
          <p className="text-sm text-red-600 dark:text-red-400">{errors.emailText.message}</p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Sender (Optional)
          </label>
          <input
            {...register('sender')}
            type="email"
            className="w-full px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white"
            placeholder="sender@email.com"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Subject (Optional)
          </label>
          <input
            {...register('subject')}
            type="text"
            className="w-full px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-900 dark:text-white"
            placeholder="Email subject"
          />
        </div>
      </div>

      <Button 
        type="submit" 
        variant="default" 
        size="lg"
        className="w-full"
        disabled={emailText.trim() === ''}
      >
        Scan Email
      </Button>

      {/* Example Templates */}
      <div className="mt-4">
        <p className="text-sm text-slate-500 dark:text-slate-400 mb-2">Try an example:</p>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setEmailText(`Dear Valued Customer,

Your account has been temporarily suspended due to unusual activity. To restore access, please verify your information immediately:

Click here: http://fake-bank-verify.com

Failure to verify within 24 hours will result in permanent account closure.

Sincerely,
Security Team`)}
            className="text-xs px-3 py-1 bg-slate-100 dark:bg-slate-700 rounded-full text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600"
          >
            Phishing Example
          </button>
          <button
            type="button"
            onClick={() => setEmailText(`Hi Team,

Attached is the Q4 report we discussed in yesterday's meeting. Please review and provide feedback by Friday.

Best regards,
John`)}
            className="text-xs px-3 py-1 bg-slate-100 dark:bg-slate-700 rounded-full text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600"
          >
            Safe Example
          </button>
        </div>
      </div>
    </form>
  )
}