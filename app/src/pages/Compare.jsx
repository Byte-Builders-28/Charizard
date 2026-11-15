import React, { useEffect, useState } from 'react'
import Plot from 'react-plotly.js'
import { getInvestigations, compareInvestigations } from '../api/client.js'
import StatusBadge from '../components/StatusBadge.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import { GitCompare, AlertCircle } from 'lucide-react'

const DEFAULT_SELECTION = ['PSI-69', 'PSI-98', 'PSI-25']
const DARK_PLOT = { plot_bgcolor: '#111827', paper_bgcolor: '#111827' }

const COMPARISON_FIELDS = [
  { key: 'acronym', label: 'Acronym' },
  { key: 'fuel_state', label: 'Fuel State' },
  { key: 'gravity_condition', label: 'Gravity Condition' },
  { key: 'hardware', label: 'Hardware' },
  { key: 'flight_program', label: 'Flight Program' },
  { key: 'safety_category', label: 'Safety Focus', isArray: true },
  { key: 'oxygen_range', label: 'Oxygen Range (%)' },
  { key: 'pressure_range', label: 'Pressure Range (mmHg)' },
  { key: 'airflow_range', label: 'Airflow Range (cm/s)' },
  { key: 'telemetry_rows', label: 'Telemetry Rows' },
]

export default function Compare() {
  const [allInvestigations, setAllInvestigations] = useState([])
  const [selectedIds, setSelectedIds] = useState(DEFAULT_SELECTION)
  const [comparedData, setComparedData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    document.title = 'FlameScope | Compare'
    getInvestigations().then(data => {
      const items = data.investigations || data
      setAllInvestigations(items)
    })
  }, [])

  useEffect(() => {
    if (selectedIds.length === 0) {
      setComparedData([])
      return
    }
    setLoading(true)
    compareInvestigations(selectedIds)
      .then(data => {
        setComparedData(Array.isArray(data) ? data : (data.investigations || []))
      })
      .finally(() => setLoading(false))
  }, [selectedIds])

  const toggleSelect = (id) => {
    if (selectedIds.includes(id)) {
      if (selectedIds.length > 1) {
        setSelectedIds(selectedIds.filter(x => x !== id))
      }
    } else {
      if (selectedIds.length < 3) {
        setSelectedIds([...selectedIds, id])
      } else {
        setSelectedIds([...selectedIds.slice(1), id])
      }
    }
  }

  // Helper to format values
  const getFieldValue = (inv, field) => {
    if (field.key === 'oxygen_range') {
      const min = inv.oxygen_percent_min ?? (inv.fields?.oxygen_percent_min?.value)
      const max = inv.oxygen_percent_max ?? (inv.fields?.oxygen_percent_max?.value)
      if (min != null || max != null) return `${min ?? '?'} - ${max ?? '?'} %`
      return 'N/A'
    }
    if (field.key === 'pressure_range') {
      const min = inv.pressure_mmhg_min ?? (inv.fields?.pressure_mmhg_min?.value)
      const max = inv.pressure_mmhg_max ?? (inv.fields?.pressure_mmhg_max?.value)
      if (min != null || max != null) return `${min ?? '?'} - ${max ?? '?'} mmHg`
      return 'N/A'
    }
    if (field.key === 'airflow_range') {
      const min = inv.airflow_min ?? (inv.fields?.airflow_min?.value)
      const max = inv.airflow_max ?? (inv.fields?.airflow_max?.value)
      if (min != null || max != null) return `${min ?? '?'} - ${max ?? '?'} cm/s`
      return 'N/A'
    }
    if (field.isArray) {
      const val = inv[field.key]
      if (Array.isArray(val)) return val.join(', ')
      return val || 'N/A'
    }
    return inv[field.key] || inv.fields?.[field.key]?.value || 'N/A'
  }

  const getFieldStatus = (inv, fieldKey) => {
    return inv.fields?.[fieldKey]?.status || (inv[fieldKey] ? 'extracted' : 'unavailable')
  }

  // Radar chart data preparation
  const categories = ['Oxygen Range', 'Pressure Range', 'Airflow Span', 'Telemetry Depth']
  const radarData = comparedData.map((inv, idx) => {
    const o2Span = ((inv.oxygen_percent_max || 21) - (inv.oxygen_percent_min || 21))
    const pSpan = ((inv.pressure_mmhg_max || 760) - (inv.pressure_mmhg_min || 760))
    const afSpan = ((inv.airflow_max || 0) - (inv.airflow_min || 0))
    const rows = inv.telemetry_rows || 0

    // Normalized scores (0 to 100)
    const o2Score = Math.min(100, Math.round((o2Span / 80) * 100))
    const pScore = Math.min(100, Math.round((pSpan / 1000) * 100))
    const afScore = Math.min(100, Math.round((afSpan / 40) * 100))
    const rowsScore = Math.min(100, Math.round((rows / 400) * 100))

    const colors = ['#f97316', '#38bdf8', '#a855f7']

    return {
      type: 'scatterpolar',
      r: [o2Score, pScore, afScore, rowsScore, o2Score],
      theta: [...categories, categories[0]],
      fill: 'toself',
      name: inv.acronym || inv.investigation_id,
      line: { color: colors[idx % colors.length] },
      opacity: 0.7
    }
  })

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <GitCompare className="text-flame-500 w-8 h-8" />
          Comparative Analysis
        </h1>
        <p className="text-gray-400 mt-1">Side-by-side scientific comparison of up to 3 investigations</p>
      </div>

      {/* Selector Chips */}
      <div className="bg-space-800 p-5 rounded-xl border border-space-700">
        <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider block mb-3">
          Select 2 or 3 Investigations to Compare
        </label>
        <div className="flex flex-wrap gap-2">
          {allInvestigations.map(inv => {
            const isSelected = selectedIds.includes(inv.investigation_id)
            return (
              <button
                key={inv.investigation_id}
                onClick={() => toggleSelect(inv.investigation_id)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                  isSelected
                    ? 'bg-flame-500 text-white shadow-lg shadow-flame-500/20'
                    : 'bg-space-900 text-gray-400 hover:text-white hover:bg-space-700 border border-space-700'
                }`}
              >
                {inv.acronym || inv.investigation_id}
              </button>
            )
          })}
        </div>
      </div>

      {loading ? (
        <LoadingSpinner message="Calculating comparison metrics..." />
      ) : comparedData.length === 0 ? (
        <div className="text-center py-12 text-gray-500">Please select at least one investigation to compare.</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Comparison Matrix (2 cols on desktop) */}
          <div className="lg:col-span-2 bg-space-800 rounded-xl border border-space-700 overflow-hidden">
            <div className="p-4 border-b border-space-700 font-semibold text-white">
              Attribute Comparison Matrix
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-space-700 bg-space-900/50">
                    <th className="p-4 text-gray-400 font-medium">Feature</th>
                    {comparedData.map(inv => (
                      <th key={inv.investigation_id} className="p-4 text-white font-semibold">
                        <div>{inv.acronym || inv.investigation_id}</div>
                        <div className="text-xs text-gray-400 font-normal truncate max-w-[180px]">{inv.title}</div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-space-700">
                  {COMPARISON_FIELDS.map(f => {
                    // Check if values differ across investigations
                    const values = comparedData.map(inv => String(getFieldValue(inv, f)))
                    const isDifferent = new Set(values).size > 1 && values.length > 1

                    return (
                      <tr key={f.key} className={isDifferent ? 'bg-space-900/30' : ''}>
                        <td className="p-4 text-gray-400 font-medium flex items-center gap-1.5">
                          {f.label}
                          {isDifferent && (
                            <span title="Divergent attribute" className="w-1.5 h-1.5 rounded-full bg-ember-400 inline-block" />
                          )}
                        </td>
                        {comparedData.map(inv => {
                          const val = getFieldValue(inv, f)
                          const status = getFieldStatus(inv, f.key)
                          return (
                            <td key={inv.investigation_id} className="p-4 text-gray-200">
                              <div className="flex items-center gap-2">
                                <span className={isDifferent ? 'font-semibold text-white' : ''}>{val}</span>
                                {inv.fields?.[f.key] && (
                                  <StatusBadge status={status} size="sm" />
                                )}
                              </div>
                            </td>
                          )
                        })}
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Radar Chart */}
          <div className="bg-space-800 p-5 rounded-xl border border-space-700 flex flex-col items-center">
            <h3 className="font-semibold text-white mb-2 self-start">Parameter Envelope (Radar)</h3>
            <p className="text-xs text-gray-400 mb-4 self-start">
              Normalized relative experimental span
            </p>
            <div className="w-full flex justify-center">
              <Plot
                data={radarData}
                layout={{
                  ...DARK_PLOT,
                  polar: {
                    radialaxis: {
                      visible: true,
                      range: [0, 100],
                      color: '#6b7280',
                      gridcolor: '#1f2937',
                    },
                    angularaxis: {
                      color: '#9ca3af',
                      gridcolor: '#1f2937',
                    },
                    bgcolor: '#111827',
                  },
                  showlegend: true,
                  legend: { orientation: 'h', y: -0.2, font: { color: '#9ca3af' } },
                  margin: { t: 20, r: 30, b: 40, l: 30 },
                  width: 320,
                  height: 320,
                }}
                config={{ displayModeBar: false, responsive: true }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

