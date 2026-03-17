export type ThreatType = 'phishing' | 'malicious-url' | 'deepfake' | 'safe'
export type RiskLevel = 'Low' | 'Medium' | 'High'

export interface ScanResult {
  scanId: string
  threatType: ThreatType
  probability: number
  riskScore: number
  riskLevel: RiskLevel
  explanation: string[]
  recommendedActions: string[]
  timestamp: string
  features?: {
    urgency_count?: number
    suspicious_count?: number
    has_links?: boolean
    [key: string]: any
  }
}

export interface EmailScanRequest {
  email_text: string
  sender?: string
  subject?: string
}

export interface UrlScanRequest {
  url: string
}

export interface DeepfakeScanRequest {
  file: File
  mediaType: 'video' | 'audio'
}

// Auth types
export interface User {
  id: string
  email: string
  name?: string
}

export interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  error: string | null
}