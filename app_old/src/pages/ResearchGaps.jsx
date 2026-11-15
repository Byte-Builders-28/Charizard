import React, { useEffect, useState } from 'react'
import Plot from 'react-plotly.js'
import { getGaps } from '../api/client.js'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import { AlertOctagon, HelpCircle, Flame, Moon, Compass, Rocket, Globe } from 'lucide-react'

const DARK_PLOT = { plot_bgcolor: '#111827', paper_bgcolor: '#111827' }

export default function ResearchGaps() {
  const [gapsData, setGapsData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    document.title = 'Charizard | Research Gaps'
    getGaps()
      .then(data => setGapsData(data))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner message="Mapping research frontiers and data gaps..." />

  const heatmap = gapsData?.oxygen_airflow_heatmap || []
  const fieldCoverage = gapsData?.field_coverage || []
  const scenarioCoverage = gapsData?.scenario_coverage || { iss: 0, moon_base: 0, mars: 0, rover: 0 }

  // Scatter plot data for O2 vs Airflow
  const scatterPlotData = [
    {
      x: heatmap.map(d => d.oxygen_midpoint || 21),
      y: heatmap.map(d => d.airflow_midpoint || 10),
      text: heatmap.map(d => `${d.acronym || d.investigation_id} (${d.rows || 0} runs)`),
      mode: 'markers+text',
      textposition: 'top center',
      textfont: { color: '#e5e7eb', size: 12 },
      marker: {
        size: heatmap.map(d => Math.max(14, Math.min(35, (d.rows || 20) / 10))),
        color: '#f97316',
        opacity: 0.85,
        line: { color: '#ea580c', width: 2 },
      },
      type: 'scatter',
      hoverinfo: 'text+x+y',
    },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <AlertOctagon className="text-ember-400 w-8 h-8" />
          Research Gaps & Frontiers
        </h1>
        <p className="text-gray-400 mt-1">
          Systematic identification of uncharacterized microgravity combustion regimes and planetary exploration hazards
        </p>
      </div>

      {/* Critical Gap Banner */}
      <div className="bg-gradient-to-r from-red-950/60 to-space-800 border-2 border-red-500/50 rounded-xl p-6 shadow-xl relative overflow-hidden">
        <div className="flex flex-col md:flex-row items-start md:items-center gap-5">
          <div className="w-14 h-14 rounded-2xl bg-red-500/20 text-red-400 flex items-center justify-center flex-shrink-0 border border-red-500/30">
            <Moon className="w-8 h-8 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-bold uppercase tracking-wider text-red-400 bg-red-500/10 px-2.5 py-0.5 rounded-full border border-red-500/20">
                Primary Scientific Blind Spot
              </span>
              <span className="text-xs text-gray-400">Artemis & Moon-to-Mars Critical Risk</span>
            </div>
            <h2 className="text-xl font-bold text-white">The Partial-Gravity Flammability Gap (0 of 11 Tested)</h2>
            <p className="text-gray-300 text-sm mt-1 leading-relaxed">
              Zero of the 11 cataloged combustion investigations test partial-gravity conditions (Lunar 0.16g or Martian 0.38g).
              All existing records were conducted either in ISS microgravity (≈0g) or terrestrial normal gravity (1g).
              Buoyancy, flame propagation rates, and extinction limits do not scale linearly between 0g and 1g.
            </p>
          </div>
        </div>
      </div>

      {/* Scenario Coverage Cards */}
      <div>
        <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400 mb-3">
          Exploration Environment Coverage
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-space-800 p-4 rounded-xl border border-space-700">
            <div className="flex items-center justify-between text-gray-400 mb-2">
              <span className="text-xs font-medium">ISS (Microgravity)</span>
              <Rocket className="w-4 h-4 text-blue-400" />
            </div>
            <div className="text-2xl font-bold text-white">{scenarioCoverage.iss} / 11</div>
            <div className="text-xs text-green-400 mt-1">✓ Well-characterized baseline</div>
          </div>

          <div className="bg-space-800 p-4 rounded-xl border border-space-700">
            <div className="flex items-center justify-between text-gray-400 mb-2">
              <span className="text-xs font-medium">Moon Base (1/6g)</span>
              <Moon className="w-4 h-4 text-ember-400" />
            </div>
            <div className="text-2xl font-bold text-white">{scenarioCoverage.moon_base} / 11</div>
            <div className="text-xs text-red-400 mt-1">✗ Critical experiment void</div>
          </div>

          <div className="bg-space-800 p-4 rounded-xl border border-space-700">
            <div className="flex items-center justify-between text-gray-400 mb-2">
              <span className="text-xs font-medium">Mars Surface (3/8g)</span>
              <Globe className="w-4 h-4 text-flame-400" />
            </div>
            <div className="text-2xl font-bold text-white">{scenarioCoverage.mars} / 11</div>
            <div className="text-xs text-amber-400 mt-1">⚠ Low-O₂ proxy data only</div>
          </div>

          <div className="bg-space-800 p-4 rounded-xl border border-space-700">
            <div className="flex items-center justify-between text-gray-400 mb-2">
              <span className="text-xs font-medium">Pressurized Rover</span>
              <Compass className="w-4 h-4 text-purple-400" />
            </div>
            <div className="text-2xl font-bold text-white">{scenarioCoverage.rover} / 11</div>
            <div className="text-xs text-gray-400 mt-1">Solid flammability matches</div>
          </div>
        </div>
      </div>

      {/* Main Grid: Scatter Plot + Field Coverage Table */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Section 1: Oxygen vs Airflow scatter plot */}
        <div className="bg-space-800 p-5 rounded-xl border border-space-700">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-white">Oxygen vs. Airflow Envelope</h3>
              <p className="text-xs text-gray-400">Co-varying flow and oxidizer parameter space</p>
            </div>
            <HelpCircle className="w-4 h-4 text-gray-500" title="Scatter of experiments with both oxygen and airflow measured" />
          </div>

          {heatmap.length === 0 ? (
            <div className="h-64 flex items-center justify-center text-sm text-gray-500 bg-space-900 rounded-lg">
              No investigations currently provide simultaneous O₂ and airflow ranges.
            </div>
          ) : (
            <div className="w-full flex justify-center">
              <Plot
                data={scatterPlotData}
                layout={{
                  ...DARK_PLOT,
                  xaxis: {
                    title: 'Oxygen Concentration (% O₂)',
                    color: '#9ca3af',
                    gridcolor: '#1f2937',
                    range: [10, 50],
                  },
                  yaxis: {
                    title: 'Forced Airflow Speed (cm/s)',
                    color: '#9ca3af',
                    gridcolor: '#1f2937',
                    range: [0, 50],
                  },
                  margin: { t: 20, r: 20, b: 50, l: 60 },
                  width: 480,
                  height: 320,
                }}
                config={{ displayModeBar: false, responsive: true }}
              />
            </div>
          )}
          <p className="text-xs text-gray-400 mt-3 italic text-center">
            Note: Most experiments vary only one parameter at a time. Multi-variable co-variation is rare.
          </p>
        </div>

        {/* Section 3: Field Coverage Table */}
        <div className="bg-space-800 p-5 rounded-xl border border-space-700">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-white">Schema Field Completeness</h3>
              <p className="text-xs text-gray-400">Structured data extraction yield across 11 investigations</p>
            </div>
            <span className="text-xs font-semibold text-flame-400 bg-flame-500/10 px-2 py-0.5 rounded">
              20 Core Schema Keys
            </span>
          </div>

          <div className="space-y-3 max-h-[340px] overflow-y-auto pr-1">
            {fieldCoverage.map(item => {
              const pct = item.percent || Math.round((item.count / (item.total || 11)) * 100)
              return (
                <div key={item.field} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="font-mono text-gray-300">{item.field}</span>
                    <span className="text-gray-400">
                      {item.count} / {item.total || 11} ({pct}%)
                    </span>
                  </div>
                  <div className="w-full bg-space-900 rounded-full h-1.5 overflow-hidden">
                    <div
                      className={`h-1.5 rounded-full ${
                        pct > 80 ? 'bg-green-500' : pct > 50 ? 'bg-amber-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

