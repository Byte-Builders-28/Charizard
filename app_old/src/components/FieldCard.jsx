import React from 'react'
import StatusBadge from './StatusBadge.jsx'

export default function FieldCard({ fieldName, field }) {
  const displayName = fieldName
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase())

  const isUnavailable = field.status === 'unavailable' || field.value === null || field.value === undefined

  return (
    <div className="bg-space-900 border border-space-700 rounded-lg p-4">
      <div className="flex items-start justify-between gap-2 mb-1">
        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">{displayName}</span>
        <StatusBadge status={field.status} />
      </div>
      <div className="flex items-baseline gap-1 mt-1">
        {isUnavailable ? (
          <span className="text-gray-600 text-sm">—</span>
        ) : (
          <>
            <span className="text-white font-semibold text-sm">{String(field.value)}</span>
            {field.unit && <span className="text-gray-500 text-xs">{field.unit}</span>}
          </>
        )}
      </div>
      {field.evidence_quote && (
        <p className="text-gray-500 text-xs italic mt-2 leading-relaxed">
          "{field.evidence_quote}"
          {field.evidence_location && (
            <span className="text-gray-600 not-italic ml-1">— {field.evidence_location}</span>
          )}
        </p>
      )}
    </div>
  )
}

