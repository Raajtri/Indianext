import type { EmailScanRequest, UrlScanRequest, DeepfakeScanRequest, ScanResult } from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api'
const USE_MOCK = true // Set to false when backend is ready

// ============================================
// REAL API CALLS (for when backend is ready)
// ============================================

export async function scanEmail(data: EmailScanRequest): Promise<ScanResult> {
  if (USE_MOCK) {
    return mockScanEmail(data)
  }

  const response = await fetch(`${API_BASE_URL}/phishing-scan`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  
  if (!response.ok) {
    throw new Error('Scan failed')
  }
  
  return response.json()
}

export async function scanUrl(data: UrlScanRequest): Promise<ScanResult> {
  if (USE_MOCK) {
    return mockScanUrl(data)
  }

  const response = await fetch(`${API_BASE_URL}/url-scan`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  
  if (!response.ok) {
    throw new Error('Scan failed')
  }
  
  return response.json()
}

export async function scanDeepfake(data: FormData): Promise<ScanResult> {
  if (USE_MOCK) {
    return mockScanDeepfake(data)
  }

  const response = await fetch(`${API_BASE_URL}/deepfake-scan`, {
    method: 'POST',
    body: data,
  })
  
  if (!response.ok) {
    throw new Error('Scan failed')
  }
  
  return response.json()
}

// ============================================
// MOCK API FUNCTIONS (for development)
// ============================================

// Mock Email Scan
export async function mockScanEmail(data: EmailScanRequest): Promise<ScanResult> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 2000))
  
  const text = data.emailText.toLowerCase()
  
  // Comprehensive phishing detection logic
  const phishingIndicators = {
    urgentKeywords: ['urgent', 'immediately', 'suspended', 'verify', 'click here', 'action required'],
    suspiciousLinks: text.match(/https?:\/\/[^\s]+/g) || [],
    threatPhrases: ['account', 'bank', 'paypal', 'password', 'credit card', 'social security'],
    grammaticalErrors: ['dear customer', 'kindly', 'verify now', 'click below'],
    spoofedDomains: ['secure-', 'verify-', 'account-', 'update-', 'login-', 'signin-']
  }

  // Calculate various risk factors
  const urgencyScore = phishingIndicators.urgentKeywords.filter(word => text.includes(word)).length * 10
  const linkScore = phishingIndicators.suspiciousLinks.length * 15
  const threatScore = phishingIndicators.threatPhrases.filter(phrase => text.includes(phrase)).length * 8
  const grammarScore = phishingIndicators.grammaticalErrors.filter(error => text.includes(error)).length * 12
  
  // Check for spoofed domains in links
  let spoofScore = 0
  phishingIndicators.suspiciousLinks.forEach(link => {
    if (phishingIndicators.spoofedDomains.some(domain => link.includes(domain))) {
      spoofScore += 20
    }
  })

  // Calculate total probability
  const totalScore = urgencyScore + linkScore + threatScore + grammarScore + spoofScore
  const probability = Math.min(totalScore / 100, 0.95)
  const riskScore = Math.round(probability * 100)
  const riskLevel = riskScore > 70 ? 'High' : riskScore > 40 ? 'Medium' : 'Low'

  // Generate explanations
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
  
  // Suspicious patterns with weighted scoring
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
  
  // Calculate weighted suspicious score
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
  
  // Calculate probability
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
  
  // Simulate analysis based on file properties
  const fileSize = file.size / (1024 * 1024) // MB
  const fileName = file.name.toLowerCase()
  const fileExtension = fileName.split('.').pop() || ''
  
  // Comprehensive deepfake indicators
  const suspiciousIndicators = [
    'ai', 'fake', 'generated', 'synthetic', 'deepfake', 
    'manipulated', 'edited', 'altered', 'synthesized'
  ]
  
  const suspiciousName = suspiciousIndicators.some(indicator => fileName.includes(indicator))
  const unusualSize = fileSize > 100 || fileSize < 0.1
  const commonVideoExtensions = ['mp4', 'avi', 'mov', 'mkv']
  const commonAudioExtensions = ['mp3', 'wav', 'm4a', 'ogg']
  
  // Check if extension matches claimed media type
  const extensionMismatch = mediaType === 'video' 
    ? !commonVideoExtensions.includes(fileExtension)
    : !commonAudioExtensions.includes(fileExtension)
  
  // Calculate probability
  let probability = 0.2 // base probability
  
  if (suspiciousName) probability += 0.25
  if (unusualSize) probability += 0.2
  if (extensionMismatch) probability += 0.15
  
  // Media-specific indicators
  if (mediaType === 'video') {
    probability += 0.1 // video deepfakes are more common
  }
  
  probability = Math.min(probability, 0.95)
  
  const riskScore = Math.round(probability * 100)
  const riskLevel = riskScore > 70 ? 'High' : riskScore > 40 ? 'Medium' : 'Low'
  
  const explanations = []
  if (suspiciousName) explanations.push('Filename suggests AI-generated or manipulated content')
  if (unusualSize) explanations.push(`File size (${fileSize.toFixed(1)}MB) is unusual for this media type`)
  if (extensionMismatch) explanations.push('File extension may not match actual content type')
  
  // Detailed explanations based on media type
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
    explanation: explanations.slice(0, 4), // Show top 4 explanations
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

// ============================================
// UTILITY FUNCTIONS
// ============================================

// Get threat statistics (for dashboard)
export async function getThreatStats(): Promise<{
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
  if (USE_MOCK) {
    // Return mock statistics
    return {
      totalScans: 1234,
      threatsDetected: 456,
      safeScans: 778,
      averageRiskScore: 42,
      threatBreakdown: {
        phishing: 234,
        maliciousUrl: 156,
        deepfake: 66
      }
    }
  }

  const response = await fetch(`${API_BASE_URL}/stats`)
  if (!response.ok) {
    throw new Error('Failed to fetch stats')
  }
  return response.json()
}

// Get scan history
export async function getScanHistory(limit: number = 10): Promise<ScanResult[]> {
  if (USE_MOCK) {
    // Return mock history
    return [
      {
        scanId: '1',
        threatType: 'phishing',
        probability: 0.89,
        riskScore: 89,
        riskLevel: 'High',
        explanation: ['Urgency language detected', 'Suspicious links found'],
        recommendedActions: ['Do not click links'],
        timestamp: new Date().toISOString()
      },
      {
        scanId: '2',
        threatType: 'malicious-url',
        probability: 0.76,
        riskScore: 76,
        riskLevel: 'High',
        explanation: ['Suspicious domain', 'No HTTPS'],
        recommendedActions: ['Block domain'],
        timestamp: new Date(Date.now() - 3600000).toISOString()
      },
      {
        scanId: '3',
        threatType: 'safe',
        probability: 0.12,
        riskScore: 12,
        riskLevel: 'Low',
        explanation: ['URL appears safe'],
        recommendedActions: ['Proceed with caution'],
        timestamp: new Date(Date.now() - 7200000).toISOString()
      }
    ]
  }

  const response = await fetch(`${API_BASE_URL}/history?limit=${limit}`)
  if (!response.ok) {
    throw new Error('Failed to fetch history')
  }
  return response.json()
}

// Toggle mock mode (useful for development)
export function setMockMode(enabled: boolean) {
  (global as any).USE_MOCK = enabled
}