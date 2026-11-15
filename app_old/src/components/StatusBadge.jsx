import React from 'react'

const STATUS_STYLES = {
  verified: 'bg-green-900 text-green-300 border border-green-700',
  extracted: 'bg-blue-900 text-blue-300 border border-blue-700',
  inferred: 'bg-amber-900 text-amber-300 border border-amber-700',
  unavailable: 'bg-gray-800 text-gray-500 border border-gray-700',
}

export default function StatusBadge({ status }) {
  const s = status || 'unavailable'
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${STATUS_STYLES[s] || STATUS_STYLES.unavailable}`}>
      {s}
    </span>
  )
}

