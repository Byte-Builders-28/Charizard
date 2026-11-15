import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import Plot from 'react-plotly.js'
import { getInvestigation, getTelemetry } from '../api/client.js'
import FieldCard from '../components/FieldCard.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import { ExternalLink, ArrowLeft, Database, ChartScatter } from 'lucide-react'

const DARK_PLOT = { plot_bgcolor: '#111827', paper_bgcolor: '#111827' }

const SAFETY_COLORS = {
  prevention: 'bg-purple-900/60 text-purple-300 border-purple-700',
  detection: 'bg-blue-900/60 text-blue-300 border-blue-700',
  suppression: 'bg-red-900/60 text-red-300 border-red-700',
}

export default function InvestigationDetail() {
  const { id } = useParams()
  const [inv, setInv] = useState(null)
  const [telemetry, setTelemetry] = useState({ rows: [], columns: [] })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    document.title = `FlameScope | ${id}`
    setLoading(true)
    Promise.all([
      getInvestigation(id),
      getTelemetry(id).catch(() => ({ rows: [], columns: [] }))
    ])
      .then(([invData, telData]) => {
        setInv(invData)
        setTelemetry(telData)
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <LoadingSpinner message={`Loading ${id}...`} />
  if (error) return (
    <div className="text-center py-20">
      <p className="text-red-400">{error}</p>
      <Link to="/explorer" className="text-flame-400 mt-4 inline-block hover:underline">← Back to Explorer</Link>
    </div>
  )
  if (!inv) return null

  const cats = Array.isArray(inv.safety_category) ? inv.safety_category : [inv.safety_category]
  const fields = inv.fields || {}
  const fieldKeys = Object.keys(fields)

  // Scatter data
  const o2Values = telemetry.rows.map(r => r['O2 (%)'] || r['Percent O2'] || null).filter(v => v !== null && v !== 'N/A')
  const afValues = telemetry.rows.map(r => r['Airflow (cm/s)'] || null).filter(v => v !== null && v !== 'N/A')
  const hasChart = o2Values.length > 0 && afValues.length > 0 && o2Values.length === afValues.length

  // Column stats
  const numericCols = telemetry.columns ? telemetry.columns.filter(col => {
    const vals = telemetry.rows.map(r => parseFloat(r[col])).filter(v => !isNaN(v))
    return vals.length > 0
  }) : []

  function colStats(col) {
    const vals = telemetry.rows.map(r => parseFloat(r[col])).filter(v => !isNaN(v))
    if (!vals.length) return { min: '—', max: '—', mean: '—' }
    const min = Math.min(...vals).toFixed(2)
    const max = Math.max(...vals).toFixed(2)
    const mean = (vals.reduce((a, b) => a + b, 0) / vals.length).toFixed(2)
    return { min, max, mean }
  }

  return (
    <div className="space-y-8">
      {/* Breadcrumb */}
      <Link to="/explorer" className="flex items-center gap-2 text-gray-400 hover:text-white text-sm transition-colors w-fit">
        <ArrowLeft size={16} />
        Back to Explorer
      </Link>

      {/* Header */}
      <div className="bg-space-800 border border-space-700 rounded-xl p-6">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 flex-wrap mb-3">
              <span className="bg-flame-500/20 text-flame-400 font-bold px-3 py-1 rounded font-mono text-sm">
                {inv.acronym || inv.investigation_id}
              </span>
              <span className="text-gray-500 font-mono text-sm">{inv.investigation_id}</span>
              {cats.map(cat => (
                <span key={cat} className={`text-xs px-2 py-0.5 rounded border ${SAFETY_COLORS[cat] || 'bg-gray-800 text-gray-400 border-gray-700'}`}>
                  {cat}
                </span>
              ))}
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">{inv.title}</h1>
            {inv.objective && <p className="text-gray-400 text-sm leading-relaxed mb-3">{inv.objective}</p>}
            <div className="flex flex-wrap gap-4 text-sm text-gray-400">
              {inv.hardware && <span>🔧 {inv.hardware}</span>}
              {inv.flight_program && <span>🚀 {inv.flight_program}</span>}
              {inv.research_area && <span>🔬 {inv.research_area}</span>}
            </div>
          </div>
          <div className="flex flex-col gap-2">
            {inv.doi && (
              <a
                href={`https://doi.org/${inv.doi}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 bg-space-700 text-flame-400 hover:text-flame-300 px-3 py-2 rounded-lg text-sm transition-colors"
              >
                <ExternalLink size={14} />
                DOI
              </a>
            )}
            {inv.source_url && (
              <a
                href={inv.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 bg-space-700 text-gray-300 hover:text-white px-3 py-2 rounded-lg text-sm transition-colors"
              >
                <ExternalLink size={14} />
                PSI Source
              </a>
            )}
          </div>
        </div>
      </div>

      {/* Two column layout */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Fields */}
        <div>
          <h2 className="text-lg font-semibold text-white mb-4">Extracted Fields</h2>
          {fieldKeys.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {fieldKeys.map(key => (
                <FieldCard key={key} fieldName={key} field={fields[key]} />
              ))}
            </div>
          ) : (
            <div className="bg-space-800 border border-space-700 rounded-xl p-6 text-gray-500 text-sm">
              No extracted fields available
            </div>
          )}
        </div>

        {/* Telemetry */}
        <div className="space-y-6">
          {/* Table */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Database size={18} className="text-gray-400" />
              <h2 className="text-lg font-semibold text-white">Telemetry Data</h2>
              {telemetry.rows.length > 0 && (
                <span className="text-xs text-gray-500 ml-auto">{telemetry.rows.length} rows shown</span>
              )}
            </div>

            {telemetry.rows.length === 0 ? (
              <div className="bg-space-800 border border-space-700 rounded-xl p-6 text-gray-500 text-sm text-center">
                No telemetry data available for {id}
              </div>
            ) : (
              <div className="bg-space-800 border border-space-700 rounded-xl overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-space-700 bg-space-900">
                        {telemetry.columns.map(col => (
                          <th key={col} className="px-3 py-2 text-left text-gray-400 font-medium whitespace-nowrap">{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-space-700">
                      {telemetry.rows.slice(0, 20).map((row, i) => (
                        <tr key={i} className="hover:bg-space-700/40 transition-colors">
                          {telemetry.columns.map(col => (
                            <td key={col} className="px-3 py-2 text-gray-300 whitespace-nowrap">{row[col]}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Column stats */}
            {numericCols.length > 0 && (
              <div className="mt-4 bg-space-800 border border-space-700 rounded-xl overflow-hidden">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-space-700 bg-space-900">
                      <th className="px-3 py-2 text-left text-gray-400 font-medium">Column</th>
                      <th className="px-3 py-2 text-right text-gray-400 font-medium">Min</th>
                      <th className="px-3 py-2 text-right text-gray-400 font-medium">Max</th>
                      <th className="px-3 py-2 text-right text-gray-400 font-medium">Mean</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-space-700">
                    {numericCols.map(col => {
                      const stats = colStats(col)
                      return (
                        <tr key={col}>
                          <td className="px-3 py-2 text-gray-300 font-medium">{col}</td>
                          <td className="px-3 py-2 text-right text-gray-400">{stats.min}</td>
                          <td className="px-3 py-2 text-right text-gray-400">{stats.max}</td>
                          <td className="px-3 py-2 text-right text-gray-400">{stats.mean}</td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Scatter chart */}
          {hasChart && (
            <div>
              <div className="flex items-center gap-2 mb-4">
                <ChartScatter size={18} className="text-gray-400" />
                <h2 className="text-lg font-semibold text-white">O₂% vs Airflow</h2>
              </div>
              <div className="bg-space-800 border border-space-700 rounded-xl p-4">
                <Plot
                  data={[{
                    type: 'scatter',
                    mode: 'markers',
                    x: o2Values,
                    y: afValues,
                    marker: { color: '#f97316', size: 8, opacity: 0.7 },
                    hovertemplate: 'O₂: %{x}%<br>Airflow: %{y} cm/s<extra></extra>',
                  }]}
                  layout={{
                    ...DARK_PLOT,
                    margin: { t: 10, b: 50, l: 55, r: 10 },
                    height: 280,
                    xaxis: { title: { text: 'O₂ (%)', font: { color: '#9ca3af' } }, tickfont: { color: '#9ca3af' }, gridcolor: '#1f2937' },
                    yaxis: { title: { text: 'Airflow (cm/s)', font: { color: '#9ca3af' } }, tickfont: { color: '#9ca3af' }, gridcolor: '#1f2937' },
                  }}
                  config={{ displayModeBar: false, responsive: true }}
                  style={{ width: '100%' }}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

