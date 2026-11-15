import React, { useEffect, useState } from 'react'
import { rankByScenario } from '../api/client.js'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import { Rocket, Moon, Globe, Compass, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react'

const SCENARIOS = [
  {
    id: 'iss',
    name: 'ISS Habitat',
    icon: Rocket,
    desc: 'Microgravity (~0g), standard pressure (760 mmHg), 21% O₂, forced ventilation dominant.',
    env: 'Microgravity (0g)',
  },
  {
    id: 'moon_base',
    name: 'Lunar Base',
    icon: Moon,
    desc: 'Partial gravity (1/6g), reduced pressure (8.2 psia/425 mmHg), 34% O₂ exploration atmosphere.',
    env: 'Partial Gravity (0.16g)',
  },
  {
    id: 'mars',
    name: 'Mars Surface Habitat',
    icon: Globe,
    desc: 'Partial gravity (3/8g), ~0.095% ambient O₂ external, habitat at 8.2 psia/34% O₂.',
    env: 'Partial Gravity (0.38g)',
  },
  {
    id: 'rover',
    name: 'Pressurized Rover',
    icon: Compass,
    desc: 'Confined volume, rapid evacuation constraints, solid internal materials, immediate suppression urgency.',
    env: 'Confined Cockpit (1/6g - 1g)',
  },
]

export default function ScenarioAnalysis() {
  const [selectedScenario, setSelectedScenario] = useState('iss')
  const [rankings, setRankings] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    document.title = 'FlameScope | Scenario Analysis'
  }, [])

  useEffect(() => {
    setLoading(true)
    rankByScenario(selectedScenario)
      .then(data => {
        setRankings(Array.isArray(data) ? data : (data.rankings || []))
      })
      .finally(() => setLoading(false))
  }, [selectedScenario])

  const currentScenarioObj = SCENARIOS.find(s => s.id === selectedScenario)

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <ShieldCheck className="text-flame-500 w-8 h-8" />
          Mission Scenario Analysis
        </h1>
        <p className="text-gray-400 mt-1">
          Evaluate microgravity combustion investigation relevance and applicability across operational space environments
        </p>
      </div>

      {/* Scenario Selector Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {SCENARIOS.map(sc => {
          const Icon = sc.icon
          const isActive = selectedScenario === sc.id
          return (
            <button
              key={sc.id}
              onClick={() => setSelectedScenario(sc.id)}
              className={`p-5 rounded-xl border text-left transition-all relative overflow-hidden ${
                isActive
                  ? 'bg-space-800 border-flame-500 ring-2 ring-flame-500/20 shadow-lg shadow-flame-500/10'
                  : 'bg-space-800/60 border-space-700 hover:border-space-600 hover:bg-space-800'
              }`}
            >
              <div className="flex items-center gap-3 mb-2">
                <div className={`p-2 rounded-lg ${isActive ? 'bg-flame-500/20 text-flame-400' : 'bg-space-700 text-gray-400'}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <h3 className="font-semibold text-white">{sc.name}</h3>
              </div>
              <p className="text-xs text-gray-400 line-clamp-2 mb-3">{sc.desc}</p>
              <div className="text-[11px] font-medium text-ember-400 bg-space-900/60 px-2 py-1 rounded inline-block">
                {sc.env}
              </div>
              {isActive && (
                <div className="absolute top-0 right-0 w-2 h-full bg-flame-500" />
              )}
            </button>
          )
        })}
      </div>

      {/* Environment Context Banner */}
      <div className="bg-space-800 p-4 rounded-xl border border-space-700 flex items-start gap-3">
        <AlertTriangle className="text-ember-400 w-5 h-5 flex-shrink-0 mt-0.5" />
        <div className="text-sm">
          <span className="font-semibold text-white">Target Operational Context: {currentScenarioObj?.name}</span>
          <p className="text-gray-400 mt-0.5">{currentScenarioObj?.desc}</p>
        </div>
      </div>

      {/* Rankings List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">
            Applicability Ranking ({rankings.length} Investigations Analyzed)
          </h2>
          <span className="text-xs text-gray-400">Scores computed via multi-attribute safety relevance model</span>
        </div>

        {loading ? (
          <LoadingSpinner message={`Scoring investigations for ${currentScenarioObj?.name}...`} />
        ) : rankings.length === 0 ? (
          <div className="text-center py-12 text-gray-500">No applicable investigations found for this scenario.</div>
        ) : (
          <div className="space-y-3">
            {rankings.map((item, index) => {
              const score = item.score || 0
              return (
                <div
                  key={item.investigation_id}
                  className="bg-space-800 rounded-xl p-5 border border-space-700 hover:border-space-600 transition-colors"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-space-900 border border-space-700 flex items-center justify-center font-bold text-gray-300">
                        #{index + 1}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold uppercase tracking-wider text-flame-400 bg-flame-500/10 px-2 py-0.5 rounded">
                            {item.acronym || item.investigation_id}
                          </span>
                          <span className="text-xs text-gray-400">{item.investigation_id}</span>
                        </div>
                        <h3 className="text-base font-semibold text-white mt-0.5">{item.title}</h3>
                      </div>
                    </div>

                    {/* Score Bar */}
                    <div className="flex items-center gap-3 sm:w-48 flex-shrink-0">
                      <div className="flex-1 bg-space-900 rounded-full h-2.5 overflow-hidden border border-space-700">
                        <div
                          className="bg-gradient-to-r from-ember-500 to-flame-500 h-2.5 rounded-full transition-all duration-500"
                          style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
                        />
                      </div>
                      <span className="text-sm font-bold text-white w-9 text-right">{score}%</span>
                    </div>
                  </div>

                  {/* Reasons list */}
                  <div className="bg-space-900/60 p-3.5 rounded-lg border border-space-700/60 mb-3">
                    <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                      Scoring Rationale & Evidence Points
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {item.reasons?.map((reason, rIdx) => (
                        <div key={rIdx} className="flex items-start gap-2 text-xs text-gray-300">
                          <CheckCircle2 className="w-3.5 h-3.5 text-green-400 flex-shrink-0 mt-0.5" />
                          <span>{reason}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Metadata Tags */}
                  <div className="flex flex-wrap items-center gap-2 text-xs text-gray-400">
                    {item.hardware && (
                      <span className="bg-space-900 px-2 py-1 rounded border border-space-700">
                        Hardware: <strong className="text-gray-300">{item.hardware}</strong>
                      </span>
                    )}
                    {item.safety_category && (
                      <span className="bg-space-900 px-2 py-1 rounded border border-space-700">
                        Safety: <strong className="text-gray-300">
                          {Array.isArray(item.safety_category) ? item.safety_category.join(', ') : item.safety_category}
                        </strong>
                      </span>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

