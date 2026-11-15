import React from 'react'
import { Flame } from 'lucide-react'

export default function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4">
      <div className="relative">
        <div className="w-12 h-12 border-4 border-space-700 border-t-flame-500 rounded-full animate-spin" />
      </div>
      <p className="text-gray-400 text-sm">{message}</p>
    </div>
  )
}

