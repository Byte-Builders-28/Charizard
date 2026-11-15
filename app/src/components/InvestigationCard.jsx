import React from 'react'
import { Link } from 'react-router-dom'
import { ExternalLink, FlaskConical, Layers } from 'lucide-react'

const SAFETY_COLORS = {
  prevention: 'bg-purple-900 text-purple-300',
  detection: 'bg-blue-900 text-blue-300',
  suppression: 'bg-red-900 text-red-300',
}

const FUEL_COLORS = {
  solid: 'bg-amber-900 text-amber-300',
  liquid: 'bg-cyan-900 text-cyan-300',
  gas: 'bg-green-900 text-green-300',
}

export default function InvestigationCard({ investigation }) {
  const inv = investigation
  const cats = Array.isArray(inv.safety_category) ? inv.safety_category : [inv.safety_category]

  return (
    <Link to={`/investigation/${inv.investigation_id}`} className="block group">
      <div className="bg-space-800 border border-space-700 rounded-xl p-5 hover:border-flame-500/50 transition-all duration-200 group-hover:shadow-lg group-hover:shadow-flame-500/10 h-full flex flex-col">
        {/* Header */}
        <div className="flex items-start justify-between gap-2 mb-3">
          <span className="bg-flame-500/20 text-flame-400 text-xs font-bold px-2 py-1 rounded font-mono">
            {inv.acronym || inv.investigation_id}
          </span>
          <span className={`text-xs px-2 py-0.5 rounded font-medium ${FUEL_COLORS[inv.fuel_state] || 'bg-gray-800 text-gray-400'}`}>
            {inv.fuel_state}
          </span>
        </div>

        {/* Title */}
        <h3 className="text-white font-semibold text-sm leading-snug mb-2 flex-1 group-hover:text-flame-400 transition-colors">
          {inv.title}
        </h3>

        {/* ID */}
        <p className="text-gray-500 text-xs mb-3">{inv.investigation_id}</p>

        {/* Meta row */}
        <div className="space-y-1.5">
          {inv.hardware && (
            <div className="flex items-center gap-1.5 text-xs text-gray-400">
              <Layers size={12} className="text-gray-500 flex-shrink-0" />
              <span className="truncate">{inv.hardware}</span>
            </div>
          )}
          {inv.oxygen_percent_min != null && (
            <div className="flex items-center gap-1.5 text-xs text-gray-400">
              <FlaskConical size={12} className="text-gray-500 flex-shrink-0" />
              <span>O₂: {inv.oxygen_percent_min}–{inv.oxygen_percent_max}%</span>
            </div>
          )}
        </div>

        {/* Safety categories */}
        <div className="flex flex-wrap gap-1 mt-3">
          {cats.filter(Boolean).map(cat => (
            <span key={cat} className={`text-xs px-1.5 py-0.5 rounded ${SAFETY_COLORS[cat] || 'bg-gray-800 text-gray-400'}`}>
              {cat}
            </span>
          ))}
          {inv.has_telemetry && (
            <span className="text-xs px-1.5 py-0.5 rounded bg-space-700 text-gray-300 font-mono">
              {inv.telemetry_rows || inv.telemetry_row_count || 0} rows
            </span>
          )}
        </div>

        {/* DOI */}
        {inv.doi && (
          <div className="mt-3 pt-3 border-t border-space-700">
            <span
              className="text-xs text-flame-500/70 hover:text-flame-400 flex items-center gap-1"
              onClick={e => { e.preventDefault(); window.open(`https://doi.org/${inv.doi}`, '_blank') }}
            >
              <ExternalLink size={10} />
              DOI: {inv.doi.substring(0, 30)}{inv.doi.length > 30 ? '…' : ''}
            </span>
          </div>
        )}
      </div>
    </Link>
  )
}

