import React from 'react'

export default function FilterChip({ label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all border ${
        active
          ? 'bg-flame-500 text-white border-flame-500'
          : 'bg-space-800 text-gray-400 border-space-700 hover:border-flame-500/50 hover:text-gray-200'
      }`}
    >
      {label}
    </button>
  )
}

