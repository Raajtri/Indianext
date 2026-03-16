export type ThreatType = 'phishing' | 'malicious-url' | 'deepfake' | 'safe';

export interface ScanResult {
  scanId: string;
  threatType: ThreatType;
  probability: number;
  riskScore: number;
  riskLevel: 'Low' | 'Medium' | 'High';
  explanation: string[];
  recommendedActions: string[];
  timestamp: string;
}

export interface EmailScanRequest {
  emailText: string;
  sender?: string;
  subject?: string;
}

export interface UrlScanRequest {
  url: string;
}

export interface DeepfakeScanRequest {
  file: File;
  mediaType: 'video' | 'audio';
}