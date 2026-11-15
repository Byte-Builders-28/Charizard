import React from 'react'
import { Search } from 'lucide-react'

export default function EmptyState({ title = 'No results found', message = 'Try adjusting your filters.', icon }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4 text-center">
      <div className="w-16 h-16 rounded-full bg-space-800 border border-space-700 flex items-center justify-center">
        {icon || <Search size={24} className="text-gray-500" />}
      </div>
      <div>
        <p className="text-white font-medium">{title}</p>
        <p className="text-gray-500 text-sm mt-1">{message}</p>
      </div>
    </div>
  )
}

