'use client'

import { 
  AlertTriangle, 
  Shield, 
  AlertOctagon, 
  CheckCircle, 
  FileText, 
  Link as LinkIcon, 
  Video,
  HelpCircle 
} from 'lucide-react'

interface ThreatBadgeProps {
  type: 'phishing' | 'malicious-url' | 'deepfake' | 'safe' | 'unknown'
  size?: 'sm' | 'md' | 'lg'
  showIcon?: boolean
  showLabel?: boolean
  animate?: boolean
}

export function ThreatBadge({ 
  type, 
  size = 'md', 
  showIcon = true, 
  showLabel = true,
  animate = false 
}: ThreatBadgeProps) {
  
  const getBadgeConfig = () => {
    switch(type) {
      case 'phishing':
        return {
          icon: FileText,
          label: 'Phishing',
          color: 'orange',
          bg: 'bg-orange-100 dark:bg-orange-900/30',
          text: 'text-orange-700 dark:text-orange-300',
          border: 'border-orange-200 dark:border-orange-800'
        }
      case 'malicious-url':
        return {
          icon: LinkIcon,
          label: 'Malicious URL',
          color: 'red',
          bg: 'bg-red-100 dark:bg-red-900/30',
          text: 'text-red-700 dark:text-red-300',
          border: 'border-red-200 dark:border-red-800'
        }
      case 'deepfake':
        return {
          icon: Video,
          label: 'Deepfake',
          color: 'purple',
          bg: 'bg-purple-100 dark:bg-purple-900/30',
          text: 'text-purple-700 dark:text-purple-300',
          border: 'border-purple-200 dark:border-purple-800'
        }
      case 'safe':
        return {
          icon: CheckCircle,
          label: 'Safe',
          color: 'green',
          bg: 'bg-green-100 dark:bg-green-900/30',
          text: 'text-green-700 dark:text-green-300',
          border: 'border-green-200 dark:border-green-800'
        }
      default:
        return {
          icon: HelpCircle,
          label: 'Unknown',
          color: 'gray',
          bg: 'bg-gray-100 dark:bg-gray-800',
          text: 'text-gray-700 dark:text-gray-300',
          border: 'border-gray-200 dark:border-gray-700'
        }
    }
  }

  const config = getBadgeConfig()
  const Icon = config.icon

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base'
  }

  const iconSizes = {
    sm: 'h-3 w-3',
    md: 'h-4 w-4',
    lg: 'h-5 w-5'
  }

  return (
    <div className="inline-flex">
      <div className={`
        inline-flex items-center gap-1.5 rounded-full font-medium
        ${config.bg} ${config.text} ${config.border} border
        ${sizeClasses[size]}
        ${animate ? 'animate-pulse' : ''}
        transition-all duration-200 hover:shadow-md
      `}>
        {showIcon && <Icon className={iconSizes[size]} />}
        {showLabel && <span>{config.label}</span>}
      </div>
    </div>
  )
}

// Compact version for lists
export function CompactThreatBadge({ type }: { type: ThreatBadgeProps['type'] }) {
  return <ThreatBadge type={type} size="sm" showLabel={false} />
}

// Animated version for real-time scanning
export function AnimatedThreatBadge({ type }: { type: ThreatBadgeProps['type'] }) {
  return <ThreatBadge type={type} animate showLabel={false} />
}

// Score Badge (for risk scores)
export function ScoreBadge({ score }: { score: number }) {
  const getScoreConfig = () => {
    if (score >= 70) return { color: 'red', text: 'High Risk', bg: 'bg-red-100 dark:bg-red-900/30', textColor: 'text-red-700 dark:text-red-300' }
    if (score >= 40) return { color: 'yellow', text: 'Medium Risk', bg: 'bg-yellow-100 dark:bg-yellow-900/30', textColor: 'text-yellow-700 dark:text-yellow-300' }
    return { color: 'green', text: 'Low Risk', bg: 'bg-green-100 dark:bg-green-900/30', textColor: 'text-green-700 dark:text-green-300' }
  }

  const config = getScoreConfig()

  return (
    <div className={`
      inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-sm font-medium
      ${config.bg} ${config.textColor}
    `}>
      <AlertTriangle className="h-3 w-3" />
      <span>{config.text}</span>
      <span className="ml-1 font-bold">{score}</span>
    </div>
  )
}