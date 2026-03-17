import type { EmailScanRequest, UrlScanRequest, DeepfakeScanRequest, ScanResult } from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'
const USE_MOCK = false // Set to false to use real backend

// ============================================
// REAL API CALLS (connected to your FastAPI backend)
// ============================================

export async function scanEmail(data: EmailScanRequest): Promise<ScanResult> {
  if (USE_MOCK) {
    return mockScanEmail(data)
  }

  try {
    const response = await fetch(`${API_BASE_URL}/phishing/scan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email_text: data.email_text,
        sender: data.sender,
        subject: data.subject
      }),
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Scan failed')
    }
    
    const result = await response.json()
    
    // Transform backend response to match frontend ScanResult type
    return {
      scanId: result.scan_id,
      threatType: result.threat_type,
      probability: result.probability,
      riskScore: result.risk_score,
      riskLevel: result.risk_level,
      explanation: result.explanation,
      recommendedActions: result.recommendations,
      timestamp: result.timestamp
    }
  } catch (error) {
    console.error('Email scan error:', error)
    throw error
  }
}

export async function scanUrl(data: UrlScanRequest): Promise<ScanResult> {
  if (USE_MOCK) {
    return mockScanUrl(data)
  }

  try {
    const response = await fetch(`${API_BASE_URL}/url/scan`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        url: data.url
      }),
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Scan failed')
    }
    
    const result = await response.json()
    
    return {
      scanId: result.scan_id,
      threatType: result.threat_type,
      probability: result.probability,
      riskScore: result.risk_score,
      riskLevel: result.risk_level,
      explanation: result.explanation,
      recommendedActions: result.recommendations,
      timestamp: result.timestamp
    }
  } catch (error) {
    console.error('URL scan error:', error)
    throw error
  }
}

export async function scanDeepfake(data: FormData): Promise<ScanResult> {
  if (USE_MOCK) {
    return mockScanDeepfake(data)
  }

  try {
    const response = await fetch(`${API_BASE_URL}/deepfake/scan`, {
      method: 'POST',
      body: data, // FormData with file and media_type
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Scan failed')
    }
    
    const result = await response.json()
    
    return {
      scanId: result.scan_id,
      threatType: result.threat_type,
      probability: result.probability,
      riskScore: result.risk_score,
      riskLevel: result.risk_level,
      explanation: result.explanation,
      recommendedActions: result.recommendations,
      timestamp: result.timestamp
    }
  } catch (error) {
    console.error('Deepfake scan error:', error)
    throw error
  }
}

// ============================================
// AUTHENTICATION API CALLS
// ============================================

export interface LoginCredentials {
  email: string
  password: string
}

export interface SignupData {
  email: string
  password: string
  name?: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: {
    id: string
    email: string
  }
}

export async function login(credentials: LoginCredentials): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Login failed')
  }

  return response.json()
}

export async function signup(data: SignupData): Promise<AuthResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Signup failed')
  }

  return response.json()
}

// ============================================
// USER DATA API CALLS
// ============================================

export async function getUserScans(token: string, limit: number = 10): Promise<ScanResult[]> {
  const response = await fetch(`${API_BASE_URL}/scans?limit=${limit}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error('Failed to fetch scans')
  }

  const data = await response.json()
  
  // Transform backend scans to frontend format
  return data.scans.map((scan: any) => ({
    scanId: scan.id,
    threatType: scan.threat_type,
    probability: scan.probability,
    riskScore: scan.risk_score,
    riskLevel: scan.risk_level,
    explanation: scan.explanation,
    recommendedActions: scan.recommendations,
    timestamp: scan.created_at
  }))
}

export async function getThreatStats(token?: string): Promise<{
  totalScans: number
  threatsDetected: number
  safeScans: number
  averageRiskScore: number
  threatBreakdown: {
    phishing: number
    maliciousUrl: number
    deepfake: number
  }
}> {
  const headers: HeadersInit = {}
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(`${API_BASE_URL}/stats`, { headers })

  if (!response.ok) {
    throw new Error('Failed to fetch stats')
  }

  return response.json()
}

// ============================================
// HEALTH CHECK
// ============================================

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL.replace('/api', '')}/health`)
    return response.ok
  } catch {
    return false
  }
}

// ============================================
// MOCK API FUNCTIONS (keep these for development/fallback)
// ============================================

// Mock Email Scan
export async function mockScanEmail(data: EmailScanRequest): Promise<ScanResult> {
  await new Promise(resolve => setTimeout(resolve, 2000))

  const text = data.email_text.toLowerCase() // Changed from email_text to emailText

  const phishingIndicators = {
    urgentKeywords: ['urgent', 'immediately', 'suspended', 'verify', 'click here', 'action required'],
    suspiciousLinks: text.match(/https?:\/\/[^\s]+/g) || [],
    threatPhrases: ['account', 'bank', 'paypal', 'password', 'credit card', 'social security'],
    grammaticalErrors: ['dear customer', 'kindly', 'verify now', 'click below'],
    spoofedDomains: ['secure-', 'verify-', 'account-', 'update-', 'login-', 'signin-']
  }

  const urgencyScore = phishingIndicators.urgentKeywords.filter(word => text.includes(word)).length * 10
  const linkScore = phishingIndicators.suspiciousLinks.length * 15
  const threatScore = phishingIndicators.threatPhrases.filter(phrase => text.includes(phrase)).length * 8
  const grammarScore = phishingIndicators.grammaticalErrors.filter(error => text.includes(error)).length * 12
  
  let spoofScore = 0
  phishingIndicators.suspiciousLinks.forEach(link => {
    if (phishingIndicators.spoofedDomains.some(domain => link.includes(domain))) {
      spoofScore += 20
    }
  })

  const totalScore = urgencyScore + linkScore + threatScore + grammarScore + spoofScore
  const probability = Math.min(totalScore / 100, 0.95)
  const riskScore = Math.round(probability * 100)
  const riskLevel = riskScore > 70 ? 'High' : riskScore > 40 ? 'Medium' : 'Low'

  const explanations = []
  if (urgencyScore > 10) explanations.push('Contains urgency language to pressure quick action')
  if (linkScore > 15) explanations.push(`Contains ${phishingIndicators.suspiciousLinks.length} suspicious links`)
  if (threatScore > 16) explanations.push('Mentions sensitive information requests')
  if (grammarScore > 12) explanations.push('Unusual grammar patterns detected')
  if (spoofScore > 0) explanations.push('Links contain spoofed domain patterns')
  if (text.includes('@')) explanations.push('Contains @ symbol which can hide true destination')

  return {
    scanId: Math.random().toString(36).substr(2, 9),
    threatType: riskScore > 50 ? 'phishing' : 'safe',
    probability,
    riskScore,
    riskLevel,
    explanation: explanations.length > 0 ? explanations : ['Email appears to be legitimate'],
    recommendedActions: riskScore > 50 ? [
      'Do not click any links in this email',
      'Do not download any attachments',
      'Verify sender through official channels',
      'Report as phishing to your IT department'
    ] : [
      'Email appears safe',
      'Always verify unexpected requests',
      'Keep security awareness updated'
    ],
    timestamp: new Date().toISOString(),
  }
}

// Mock URL Scan
export async function mockScanUrl(data: UrlScanRequest): Promise<ScanResult> {
  await new Promise(resolve => setTimeout(resolve, 1500))
  
  const url = data.url.toLowerCase()
  
  const suspiciousPatterns = [
    { pattern: 'login', weight: 15 },
    { pattern: 'verify', weight: 15 },
    { pattern: 'account', weight: 12 },
    { pattern: 'secure', weight: 12 },
    { pattern: 'update', weight: 10 },
    { pattern: 'bank', weight: 20 },
    { pattern: 'paypal', weight: 20 },
    { pattern: '.xyz', weight: 25 },
    { pattern: '.top', weight: 20 },
    { pattern: '.ru', weight: 15 },
    { pattern: 'bit.ly', weight: 20 },
    { pattern: 'tinyurl', weight: 20 },
    { pattern: '192.168', weight: 30 },
    { pattern: '10.0.', weight: 30 }
  ]
  
  let suspiciousScore = 0
  suspiciousPatterns.forEach(({ pattern, weight }) => {
    if (url.includes(pattern)) {
      suspiciousScore += weight
    }
  })
  
  const hasHttps = url.startsWith('https')
  const hasIpAddress = /\d+\.\d+\.\d+\.\d+/.test(url)
  const hasMultipleSubdomains = (url.match(/\./g) || []).length > 3
  const hasSpecialChars = /[<>{}|\\^~\[\]`;@]/.test(url)
  
  let probability = suspiciousScore / 100
  if (!hasHttps) probability += 0.15
  if (hasIpAddress) probability += 0.3
  if (hasMultipleSubdomains) probability += 0.1
  if (hasSpecialChars) probability += 0.2
  if (url.includes('@')) probability += 0.25
  
  probability = Math.min(probability, 0.98)
  
  const riskScore = Math.round(probability * 100)
  const riskLevel = riskScore > 70 ? 'High' : riskScore > 40 ? 'Medium' : 'Low'
  
  const explanations = []
  if (suspiciousScore > 30) explanations.push(`Contains suspicious keywords (score: ${suspiciousScore})`)
  if (!hasHttps) explanations.push('No HTTPS encryption detected - data may be intercepted')
  if (hasIpAddress) explanations.push('Uses IP address instead of domain name (common in attacks)')
  if (hasMultipleSubdomains) explanations.push('Unusually high number of subdomains')
  if (hasSpecialChars) explanations.push('Contains special characters often used in obfuscation')
  if (url.includes('@')) explanations.push('Contains @ symbol - can hide real destination')
  
  return {
    scanId: Math.random().toString(36).substr(2, 9),
    threatType: riskScore > 50 ? 'malicious-url' : 'safe',
    probability,
    riskScore,
    riskLevel,
    explanation: explanations.length > 0 ? explanations : ['URL appears to be legitimate'],
    recommendedActions: riskScore > 50 ? [
      'Do not visit this website',
      'Block this domain immediately',
      'Report to security team',
      'Check for similar legitimate URLs'
    ] : [
      'URL appears safe to visit',
      'Verify HTTPS connection is valid',
      'Keep browser and security tools updated'
    ],
    timestamp: new Date().toISOString(),
  }
}

// Mock Deepfake Scan
export async function mockScanDeepfake(data: FormData): Promise<ScanResult> {
  await new Promise(resolve => setTimeout(resolve, 3000))
  
  const file = data.get('file') as File
  const mediaType = data.get('mediaType') as string
  
  const fileSize = file.size / (1024 * 1024)
  const fileName = file.name.toLowerCase()
  const fileExtension = fileName.split('.').pop() || ''
  
  const suspiciousIndicators = [
    'ai', 'fake', 'generated', 'synthetic', 'deepfake', 
    'manipulated', 'edited', 'altered', 'synthesized'
  ]
  
  const suspiciousName = suspiciousIndicators.some(indicator => fileName.includes(indicator))
  const unusualSize = fileSize > 100 || fileSize < 0.1
  const commonVideoExtensions = ['mp4', 'avi', 'mov', 'mkv']
  const commonAudioExtensions = ['mp3', 'wav', 'm4a', 'ogg']
  
  const extensionMismatch = mediaType === 'video' 
    ? !commonVideoExtensions.includes(fileExtension)
    : !commonAudioExtensions.includes(fileExtension)
  
  let probability = 0.2
  
  if (suspiciousName) probability += 0.25
  if (unusualSize) probability += 0.2
  if (extensionMismatch) probability += 0.15
  
  if (mediaType === 'video') {
    probability += 0.1
  }
  
  probability = Math.min(probability, 0.95)
  
  const riskScore = Math.round(probability * 100)
  const riskLevel = riskScore > 70 ? 'High' : riskScore > 40 ? 'Medium' : 'Low'
  
  const explanations = []
  if (suspiciousName) explanations.push('Filename suggests AI-generated or manipulated content')
  if (unusualSize) explanations.push(`File size (${fileSize.toFixed(1)}MB) is unusual for this media type`)
  if (extensionMismatch) explanations.push('File extension may not match actual content type')
  
  if (mediaType === 'video') {
    explanations.push('Analyzing facial landmarks and movement patterns...')
    explanations.push('Checking for unnatural blinking and lip sync issues')
    explanations.push('Examining frame consistency and compression artifacts')
  } else {
    explanations.push('Analyzing voice frequency patterns and spectrograms')
    explanations.push('Detecting synthetic voice characteristics')
    explanations.push('Checking for audio splicing artifacts')
  }
  
  return {
    scanId: Math.random().toString(36).substr(2, 9),
    threatType: riskScore > 50 ? 'deepfake' : 'safe',
    probability,
    riskScore,
    riskLevel,
    explanation: explanations.slice(0, 4),
    recommendedActions: riskScore > 50 ? [
      'Do not trust or share this media without verification',
      'Contact the person through alternative channels',
      'Check for original source of content',
      'Report to platform administrators if applicable'
    ] : [
      'Media appears authentic based on current analysis',
      'Always verify sensitive or unusual requests',
      'Stay updated on deepfake technology trends'
    ],
    timestamp: new Date().toISOString(),
  }
}

// Toggle mock mode
export function setMockMode(enabled: boolean) {
  (global as any).USE_MOCK = enabled
}