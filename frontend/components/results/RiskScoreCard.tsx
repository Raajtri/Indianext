// components/results/RiskScoreCard.tsx
'use client'

import { AlertTriangle, Shield, AlertOctagon, CheckCircle } from 'lucide-react'
import type { ScanResult } from '@/types'

interface RiskScoreCardProps {
  result: ScanResult
}

export function RiskScoreCard({ result }: RiskScoreCardProps) {
  const getRiskColor = (level: string) => {
    switch(level.toLowerCase()) {
      case 'high': return 'text-red-600 dark:text-red-400'
      case 'medium': return 'text-yellow-600 dark:text-yellow-400'
      case 'low': return 'text-green-600 dark:text-green-400'
      default: return 'text-slate-600 dark:text-slate-400'
    }
  }

  const getRiskIcon = (level: string) => {
    switch(level.toLowerCase()) {
      case 'high': return <AlertOctagon className="h-8 w-8" />
      case 'medium': return <AlertTriangle className="h-8 w-8" />
      case 'low': return <CheckCircle className="h-8 w-8" />
      default: return <Shield className="h-8 w-8" />
    }
  }

  const getProgressColor = (score: number) => {
    if (score >= 70) return 'bg-red-600'
    if (score >= 40) return 'bg-yellow-600'
    return 'bg-green-600'
  }

  const getThreatTypeDisplay = (type: string) => {
    switch(type) {
      case 'phishing': return 'Phishing Email'
      case 'malicious-url': return 'Malicious URL'
      case 'deepfake': return 'Deepfake Media'
      case 'safe': return 'Safe Content'
      default: return type
    }
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg p-6 border border-slate-200 dark:border-slate-700">
      <div className="flex items-start justify-between mb-6">
        <div>
          <p className="text-sm text-slate-500 dark:text-slate-400">Threat Analysis Result</p>
          <h3 className="text-2xl font-bold text-slate-900 dark:text-white mt-1">
            {getThreatTypeDisplay(result.threatType)}
          </h3>
        </div>
        <div className={getRiskColor(result.riskLevel)}>
          {getRiskIcon(result.riskLevel)}
        </div>
      </div>

      {/* Risk Score Gauge */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
            Risk Score
          </span>
          <span className={`text-2xl font-bold ${getRiskColor(result.riskLevel)}`}>
            {result.riskScore}
          </span>
        </div>
        <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-3">
          <div 
            className={`${getProgressColor(result.riskScore)} h-3 rounded-full transition-all duration-500`}
            style={{ width: `${result.riskScore}%` }}
          ></div>
        </div>
        <div className="flex justify-between mt-1 text-xs text-slate-500 dark:text-slate-400">
          <span>Safe</span>
          <span>Suspicious</span>
          <span>Dangerous</span>
        </div>
      </div>

      {/* Confidence and Probability */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">AI Confidence</p>
          <p className="text-xl font-semibold text-slate-900 dark:text-white">
            {result.probability.toFixed(1)}%
          </p>
        </div>
        <div className="p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg">
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-1">Probability</p>
          <p className="text-xl font-semibold text-slate-900 dark:text-white">
            {(result.probability * 100).toFixed(1)}%
          </p>
        </div>
      </div>

      {/* Features (if available) */}
      {result.features && Object.keys(result.features).length > 0 && (
        <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <p className="text-xs font-medium text-blue-700 dark:text-blue-300 mb-2">Detection Features</p>
          <div className="grid grid-cols-2 gap-2 text-xs">
            {Object.entries(result.features).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="text-blue-600 dark:text-blue-400">{key.replace(/_/g, ' ')}:</span>
                <span className="font-medium text-blue-800 dark:text-blue-200">{String(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Risk Level Badge */}
      <div className={`mt-4 text-center p-3 rounded-lg font-medium
        ${result.riskLevel.toLowerCase() === 'high' ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300' : ''}
        ${result.riskLevel.toLowerCase() === 'medium' ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300' : ''}
        ${result.riskLevel.toLowerCase() === 'low' ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300' : ''}
      `}>
        {result.riskLevel} Risk Level
      </div>
    </div>
  )
}