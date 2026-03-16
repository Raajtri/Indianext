'use client'

import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { EmailScanner } from '@/components/scanners/EmailScanner'
import { UrlScanner } from '@/components/scanners/UrlScanner'
import { DeepfakeUpload } from '@/components/scanners/DeepfakeUpload'
import { RiskScoreCard } from '@/components/results/RiskScoreCard'
import { ExplanationPanel } from '@/components/results/ExplanationPanel'
import type { ScanResult } from '@/types'

export default function DashboardPage() {
  const [scanResult, setScanResult] = useState<ScanResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-slate-900 dark:text-white">
          AI Threat Detection Dashboard
        </h1>
        <p className="text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto">
          Upload or paste content to analyze for phishing attempts, malicious URLs, and deepfake media
        </p>
      </div>

      {/* Main Scanner Interface */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column - Scanner Inputs */}
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 border border-slate-200 dark:border-slate-700">
          <Tabs defaultValue="email" className="w-full">
            <TabsList className="grid grid-cols-3 mb-8">
              <TabsTrigger value="email">Email Scan</TabsTrigger>
              <TabsTrigger value="url">URL Scan</TabsTrigger>
              <TabsTrigger value="deepfake">Deepfake Scan</TabsTrigger>
            </TabsList>
            
            <TabsContent value="email">
              <EmailScanner 
                onScan={setScanResult} 
                setIsLoading={setIsLoading}
              />
            </TabsContent>
            
            <TabsContent value="url">
              <UrlScanner 
                onScan={setScanResult} 
                setIsLoading={setIsLoading}
              />
            </TabsContent>
            
            <TabsContent value="deepfake">
              <DeepfakeUpload 
                onScan={setScanResult} 
                setIsLoading={setIsLoading}
              />
            </TabsContent>
          </Tabs>
        </div>

        {/* Right Column - Results */}
        <div className="space-y-6">
          {isLoading ? (
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-12 border border-slate-200 dark:border-slate-700 flex flex-col items-center justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
              <p className="mt-4 text-slate-600 dark:text-slate-300">Analyzing threat...</p>
            </div>
          ) : scanResult ? (
            <>
              <RiskScoreCard result={scanResult} />
              <ExplanationPanel explanation={scanResult.explanation} />
            </>
          ) : (
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-12 border border-slate-200 dark:border-slate-700 text-center">
              <p className="text-slate-500 dark:text-slate-400">
                Submit content above to see analysis results
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
  
}