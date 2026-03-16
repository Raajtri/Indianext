'use client'

import Link from 'next/link'
import { Shield, Menu, X } from 'lucide-react'
import { useState } from 'react'
import { Button } from '@/components/ui/button'

export function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <nav className="bg-white dark:bg-slate-900 shadow-lg border-b border-slate-200 dark:border-slate-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2">
              <Shield className="h-8 w-8 text-blue-600 dark:text-blue-400" />
              <span className="font-bold text-xl text-slate-900 dark:text-white">
                ThreatLens AI
              </span>
            </Link>
          </div>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-4">
            <Link href="/dashboard" className="text-slate-700 dark:text-slate-200 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 rounded-md text-sm font-medium">
              Dashboard
            </Link>
            <Link href="/about" className="text-slate-700 dark:text-slate-200 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 rounded-md text-sm font-medium">
              About
            </Link>
            <Button variant="default" size="sm">
              Get Started
            </Button>
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-slate-700 dark:text-slate-200"
            >
              {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            <Link href="/dashboard" className="block text-slate-700 dark:text-slate-200 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 rounded-md text-base font-medium">
              Dashboard
            </Link>
            <Link href="/about" className="block text-slate-700 dark:text-slate-200 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 rounded-md text-base font-medium">
              About
            </Link>
          </div>
        </div>
      )}
    </nav>
  )
}