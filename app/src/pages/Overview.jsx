import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Plot from 'react-plotly.js'
import { getInvestigations, getAllMockInvestigations } from '../api/client.js'
import InvestigationCard from '../components/InvestigationCard.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import { AlertTriangle, FlaskConical, Layers, Activity } from 'lucide-react'

const FEATURED_IDS = ['PSI-69', 'PSI-98', 'PSI-159']
const DARK_PLOT = { plot_bgcolor: '#111827', paper_bgcolor: '#111827' }

export default function Overview() {
  const [investigations, setInvestigations] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    document.title = 'FlameScope | Overview'
    getInvestigations()
      .then(d => setInvestigations(d.investigations || d))
      .catch(() => setInvestigations(getAllMockInvestigations()))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingSpinner message="Loading investigations..." />

  const featured = FEATURED_IDS.map(id => investigations.find(i => i.investigation_id === id)).filter(Boolean)
  const withTelemetry = investigations.filter(i => i.has_telemetry).length
  const totalRows = investigations.reduce((a, i) => a + (i.telemetry_rows || 0), 0)

  // Safety category distribution
  const catCounts = { prevention: 0, detection: 0, suppression: 0 }
  investigations.forEach(inv => {
    const cats = Array.isArray(inv.safety_category) ? inv.safety_category : [inv.safety_category]
    cats.forEach(c => { if (catCounts[c] !== undefined) catCounts[c]++ })
  })

  // Research area distribution
  const areaCounts = {}
  investigations.forEach(inv => {
    const a = inv.research_area || 'Unknown'
    areaCounts[a] = (areaCounts[a] || 0) + 1
  })

  // Missing airflow
  const missingAirflow = investigations.filter(i => i.airflow_min === null || i.airflow_min === undefined).length

  const sortedByID = [...investigations].sort((a, b) => {
    const na = parseInt(a.investigation_id.replace('PSI-', ''))
    const nb = parseInt(b.investigation_id.replace('PSI-', ''))
    return na - nb
  })

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Mission Control</h1>
        <p className="text-gray-400 mt-1">NASA Microgravity Combustion Science Platform</p>
      </div>

      {/* Stats bar */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={<Layers size={20} className="text-flame-400" />} label="Investigations" value={investigations.length} sub="PSI records" />
        <StatCard icon={<Activity size={20} className="text-ember-400" />} label="Total Rows" value={totalRows.toLocaleString()} sub="telemetry data points" />
        <StatCard icon={<FlaskConical size={20} className="text-blue-400" />} label="With Telemetry" value={withTelemetry} sub={`of ${investigations.length} investigations`} />
        <StatCard icon={<AlertTriangle size={20} className="text-purple-400" />} label="Safety Categories" value={Object.values(catCounts).filter(v => v > 0).length} sub="prevention · detection · suppression" />
      </div>

      {/* Featured investigations */}
      <section>
        <h2 className="text-lg font-semibold text-white mb-4">Featured Investigations</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {featured.map(inv => (
            <InvestigationCard key={inv.investigation_id} investigation={inv} />
          ))}
        </div>
      </section>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Safety Category Donut */}
        <div className="bg-space-800 border border-space-700 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-4">Safety Category Distribution</h3>
          <Plot
            data={[{
              type: 'pie',
              labels: ['Prevention', 'Detection', 'Suppression'],
              values: [catCounts.prevention, catCounts.detection, catCounts.suppression],
              hole: 0.5,
              marker: { colors: ['#8b5cf6', '#3b82f6', '#ef4444'] },
              textfont: { color: '#fff' },
              hovertemplate: '<b>%{label}</b><br>%{value} investigations<extra></extra>',
            }]}
            layout={{
              ...DARK_PLOT,
              margin: { t: 0, b: 0, l: 0, r: 0 },
              height: 240,
              showlegend: true,
              legend: { font: { color: '#9ca3af' }, orientation: 'h', y: -0.1 },
            }}
            config={{ displayModeBar: false, responsive: true }}
            style={{ width: '100%' }}
          />
        </div>

        {/* Research Area Bar */}
        <div className="bg-space-800 border border-space-700 rounded-xl p-5">
          <h3 className="text-white font-semibold mb-4">Research Area Breakdown</h3>
          <Plot
            data={[{
              type: 'bar',
              x: Object.keys(areaCounts),
              y: Object.values(areaCounts),
              marker: { color: '#f97316' },
              hovertemplate: '<b>%{x}</b><br>%{y} investigations<extra></extra>',
            }]}
            layout={{
              ...DARK_PLOT,
              margin: { t: 10, b: 80, l: 40, r: 10 },
              height: 240,
              xaxis: { tickfont: { color: '#9ca3af', size: 10 }, gridcolor: '#1f2937' },
              yaxis: { tickfont: { color: '#9ca3af' }, gridcolor: '#1f2937', dtick: 1 },
            }}
            config={{ displayModeBar: false, responsive: true }}
            style={{ width: '100%' }}
          />
        </div>
      </div>

      {/* Key gaps */}
      <div className="bg-space-800 border border-flame-500/40 rounded-xl p-5">
        <div className="flex items-center gap-2 mb-3">
          <AlertTriangle size={18} className="text-flame-400" />
          <h3 className="text-white font-semibold">Key Research Gaps</h3>
        </div>
        <ul className="space-y-2">
          <GapItem text="0 partial-gravity experiments found (Moon 1/6g, Mars 1/3g) — critical gap for future habitat fire safety" />
          <GapItem text={`${missingAirflow} investigation${missingAirflow !== 1 ? 's' : ''} missing airflow data — limits fluid dynamics modeling`} />
          <GapItem text="0 investigations with pressure below 380 mmHg — Mars surface conditions (≈6 mmHg) untested" />
        </ul>
      </div>

      {/* Recent activity list */}
      <section>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white">All Investigations</h2>
          <Link to="/explorer" className="text-flame-400 text-sm hover:text-flame-300">View all →</Link>
        </div>
        <div className="bg-space-800 border border-space-700 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-space-700">
                <th className="px-4 py-3 text-left text-gray-400 font-medium">ID</th>
                <th className="px-4 py-3 text-left text-gray-400 font-medium">Acronym</th>
                <th className="px-4 py-3 text-left text-gray-400 font-medium">Title</th>
                <th className="px-4 py-3 text-left text-gray-400 font-medium">Fuel</th>
                <th className="px-4 py-3 text-right text-gray-400 font-medium">Rows</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-space-700">
              {sortedByID.map(inv => (
                <tr key={inv.investigation_id} className="hover:bg-space-700/40 transition-colors">
                  <td className="px-4 py-3 text-gray-400 font-mono text-xs">{inv.investigation_id}</td>
                  <td className="px-4 py-3">
                    <Link to={`/investigation/${inv.investigation_id}`} className="text-flame-400 hover:text-flame-300 font-semibold text-xs">
                      {inv.acronym}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-white max-w-xs truncate">{inv.title}</td>
                  <td className="px-4 py-3 text-gray-400 capitalize">{inv.fuel_state}</td>
                  <td className="px-4 py-3 text-right text-gray-400">{inv.telemetry_rows || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}

function StatCard({ icon, label, value, sub }) {
  return (
    <div className="bg-space-800 border border-space-700 rounded-xl p-5">
      <div className="flex items-center gap-3 mb-2">
        {icon}
        <span className="text-gray-400 text-sm">{label}</span>
      </div>
      <p className="text-3xl font-bold text-white">{value}</p>
      <p className="text-gray-500 text-xs mt-1">{sub}</p>
    </div>
  )
}

function GapItem({ text }) {
  return (
    <li className="flex items-start gap-2 text-sm text-gray-300">
      <span className="text-flame-400 mt-0.5 flex-shrink-0">⚠</span>
      {text}
    </li>
  )
}

