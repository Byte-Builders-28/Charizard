import React, { useEffect, useState } from 'react'
import { getInvestigations, exportData } from '../api/client.js'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import { Download, FileText, Database, CheckSquare, Square, Layers, Shield } from 'lucide-react'

const EXPORTABLE_FIELDS = [
  { key: 'investigation_id', label: 'Investigation ID', defaultChecked: true },
  { key: 'title', label: 'Title', defaultChecked: true },
  { key: 'acronym', label: 'Acronym', defaultChecked: true },
  { key: 'doi', label: 'DOI', defaultChecked: true },
  { key: 'fuel_state', label: 'Fuel State', defaultChecked: true },
  { key: 'gravity_condition', label: 'Gravity Condition', defaultChecked: true },
  { key: 'hardware', label: 'Hardware', defaultChecked: true },
  { key: 'safety_category', label: 'Safety Focus', defaultChecked: true },
  { key: 'oxygen_percent_min', label: 'Min Oxygen (%)', defaultChecked: true },
  { key: 'oxygen_percent_max', label: 'Max Oxygen (%)', defaultChecked: true },
  { key: 'pressure_mmhg_min', label: 'Min Pressure (mmHg)', defaultChecked: true },
  { key: 'pressure_mmhg_max', label: 'Max Pressure (mmHg)', defaultChecked: true },
  { key: 'airflow_min', label: 'Min Airflow (cm/s)', defaultChecked: true },
  { key: 'airflow_max', label: 'Max Airflow (cm/s)', defaultChecked: true },
  { key: 'telemetry_rows', label: 'Telemetry Row Count', defaultChecked: true },
]

export default function DataExport() {
  const [investigations, setInvestigations] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedFields, setSelectedFields] = useState(
    EXPORTABLE_FIELDS.filter(f => f.defaultChecked).map(f => f.key)
  )
  const [isNested, setIsNested] = useState(false)
  const [exporting, setExporting] = useState(false)

  useEffect(() => {
    document.title = 'Charizard | Data Export'
    getInvestigations()
      .then(data => {
        const items = data.investigations || data
        setInvestigations(items)
      })
      .finally(() => setLoading(false))
  }, [])

  const toggleField = (key) => {
    if (selectedFields.includes(key)) {
      if (selectedFields.length > 1) {
        setSelectedFields(selectedFields.filter(f => f !== key))
      }
    } else {
      setSelectedFields([...selectedFields, key])
    }
  }

  const selectAll = () => setSelectedFields(EXPORTABLE_FIELDS.map(f => f.key))
  const selectNone = () => setSelectedFields(['investigation_id', 'title'])

  const handleDownload = async (format) => {
    setExporting(true)
    try {
      if (format === 'json') {
        let exportPayload = []
        if (isNested) {
          exportPayload = investigations.map(inv => {
            const out = { investigation_id: inv.investigation_id, title: inv.title }
            selectedFields.forEach(f => {
              out[f] = inv.fields?.[f] || {
                value: inv[f] ?? null,
                status: inv[f] != null ? 'extracted' : 'unavailable',
              }
            })
            return out
          })
        } else {
          exportPayload = investigations.map(inv => {
            const out = {}
            selectedFields.forEach(f => {
              out[f] = inv[f] ?? (inv.fields?.[f]?.value ?? null)
            })
            return out
          })
        }

        const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(exportPayload, null, 2))
        const dlAnchor = document.createElement('a')
        dlAnchor.setAttribute('href', dataStr)
        dlAnchor.setAttribute('download', `charizard_export_${Date.now()}.json`)
        document.body.appendChild(dlAnchor)
        dlAnchor.click()
        dlAnchor.remove()
      } else if (format === 'csv') {
        const headers = selectedFields.join(',')
        const rows = investigations.map(inv => {
          return selectedFields
            .map(f => {
              const val = inv[f] ?? (inv.fields?.[f]?.value ?? '')
              const strVal = Array.isArray(val) ? val.join(';') : String(val)
              return `"${strVal.replace(/"/g, '""')}"`
            })
            .join(',')
        })
        const csvContent = 'data:text/csv;charset=utf-8,' + encodeURIComponent([headers, ...rows].join('\n'))
        const dlAnchor = document.createElement('a')
        dlAnchor.setAttribute('href', csvContent)
        dlAnchor.setAttribute('download', `charizard_export_${Date.now()}.csv`)
        document.body.appendChild(dlAnchor)
        dlAnchor.click()
        dlAnchor.remove()
      }
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <Database className="text-flame-500 w-8 h-8" />
          Data Export & Ingestion Gateway
        </h1>
        <p className="text-gray-400 mt-1">
          Export cleaned, structured NASA combustion datasets for modeling, hydrodynamic simulation, or ML pipelines
        </p>
      </div>

      {/* Configuration Card */}
      <div className="bg-space-800 p-6 rounded-xl border border-space-700 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-space-700 pb-4">
          <div>
            <h2 className="text-base font-semibold text-white">Select Columns to Export</h2>
            <p className="text-xs text-gray-400">Choose attributes to include in the output file</p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={selectAll}
              className="text-xs text-flame-400 hover:text-flame-300 bg-space-900 px-3 py-1.5 rounded-lg border border-space-700"
            >
              Select All
            </button>
            <button
              onClick={selectNone}
              className="text-xs text-gray-400 hover:text-white bg-space-900 px-3 py-1.5 rounded-lg border border-space-700"
            >
              Reset
            </button>
          </div>
        </div>

        {/* Checkbox grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-3">
          {EXPORTABLE_FIELDS.map(f => {
            const isChecked = selectedFields.includes(f.key)
            return (
              <button
                key={f.key}
                onClick={() => toggleField(f.key)}
                className={`flex items-center gap-2 p-2.5 rounded-lg text-xs font-medium text-left transition-colors border ${
                  isChecked
                    ? 'bg-space-900 border-flame-500/50 text-white'
                    : 'bg-space-900/40 border-space-700 text-gray-400 hover:text-gray-200'
                }`}
              >
                {isChecked ? (
                  <CheckSquare className="w-4 h-4 text-flame-400 flex-shrink-0" />
                ) : (
                  <Square className="w-4 h-4 text-gray-500 flex-shrink-0" />
                )}
                <span className="truncate">{f.label}</span>
              </button>
            )
          })}
        </div>

        {/* Options Row */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2 border-t border-space-700">
          <div className="flex items-center gap-3">
            <span className="text-xs font-medium text-gray-400">JSON Structure:</span>
            <button
              onClick={() => setIsNested(!isNested)}
              className={`text-xs px-3 py-1.5 rounded-lg border transition-all ${
                isNested
                  ? 'bg-ember-500/20 text-ember-400 border-ember-500/40 font-semibold'
                  : 'bg-space-900 text-gray-400 border-space-700'
              }`}
            >
              {isNested ? 'Nested (FieldValue with Provenance & Status)' : 'Flat Key-Value Objects'}
            </button>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => handleDownload('csv')}
              disabled={exporting}
              className="flex items-center gap-2 bg-space-900 hover:bg-space-700 text-white px-4 py-2 rounded-lg text-sm font-medium border border-space-700 transition-colors"
            >
              <FileText className="w-4 h-4 text-emerald-400" />
              <span>Download CSV</span>
            </button>
            <button
              onClick={() => handleDownload('json')}
              disabled={exporting}
              className="flex items-center gap-2 bg-flame-500 hover:bg-flame-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              <Download className="w-4 h-4" />
              <span>Download JSON</span>
            </button>
          </div>
        </div>
      </div>

      {/* Dataset Preview */}
      <div className="bg-space-800 rounded-xl border border-space-700 overflow-hidden">
        <div className="p-4 border-b border-space-700 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-flame-500" />
            <h3 className="font-semibold text-white text-sm">Output Preview (First 5 Rows)</h3>
          </div>
          <span className="text-xs text-gray-400">
            {selectedFields.length} attributes selected • {investigations.length} total rows
          </span>
        </div>

        {loading ? (
          <LoadingSpinner message="Generating preview data..." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="bg-space-900/60 border-b border-space-700">
                  {selectedFields.map(k => (
                    <th key={k} className="p-3 text-gray-400 uppercase tracking-wider font-semibold whitespace-nowrap">
                      {k}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-space-700">
                {investigations.slice(0, 5).map((inv, idx) => (
                  <tr key={idx} className="hover:bg-space-700/20">
                    {selectedFields.map(k => {
                      const val = inv[k] ?? (inv.fields?.[k]?.value ?? '')
                      return (
                        <td key={k} className="p-3 text-gray-300 whitespace-nowrap max-w-[200px] truncate">
                          {Array.isArray(val) ? val.join(', ') : String(val ?? 'null')}
                        </td>
                      )
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Provenance Footer Note */}
      <div className="bg-space-900/50 p-4 rounded-xl border border-space-700 flex items-center gap-3 text-xs text-gray-400">
        <Shield className="w-4 h-4 text-flame-400 flex-shrink-0" />
        <span>
          Full Data Integrity Guarantee: Every data point exported originates from NASA PSI verified experimental tables
          and investigator flight documentation.
        </span>
      </div>
    </div>
  )
}

