import React, { useEffect, useState, useCallback } from 'react'
import { Search } from 'lucide-react'
import { getInvestigations } from '../api/client.js'
import InvestigationCard from '../components/InvestigationCard.jsx'
import FilterChip from '../components/FilterChip.jsx'
import LoadingSpinner from '../components/LoadingSpinner.jsx'
import EmptyState from '../components/EmptyState.jsx'

const SAFETY_CATS = ['all', 'prevention', 'detection', 'suppression']
const FUEL_STATES = ['all', 'solid', 'liquid', 'gas']
const GRAVITY_OPTS = ['all', 'microgravity', 'partial', 'normal']
const TELEMETRY_OPTS = ['all', 'yes']

export default function Explorer() {
  const [investigations, setInvestigations] = useState([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [q, setQ] = useState('')
  const [filters, setFilters] = useState({
    safety_category: 'all',
    fuel_state: 'all',
    gravity_condition: 'all',
    has_telemetry: 'all',
  })

  useEffect(() => { document.title = 'FlameScope | Explorer' }, [])

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const params = { q: q || undefined }
      if (filters.safety_category !== 'all') params.safety_category = filters.safety_category
      if (filters.fuel_state !== 'all') params.fuel_state = filters.fuel_state
      if (filters.gravity_condition !== 'all') params.gravity_condition = filters.gravity_condition
      if (filters.has_telemetry === 'yes') params.has_telemetry = 'true'
      const data = await getInvestigations(params)
      const items = data.investigations || data
      setInvestigations(items)
      setTotal(data.total || items.length)
    } finally {
      setLoading(false)
    }
  }, [q, filters])

  useEffect(() => {
    const timer = setTimeout(fetchData, 300)
    return () => clearTimeout(timer)
  }, [fetchData])

  const setFilter = (key, val) => setFilters(f => ({ ...f, [key]: val }))

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Investigation Explorer</h1>
        <p className="text-gray-400 mt-1">Browse and filter all NASA PSI microgravity combustion experiments</p>
      </div>

      {/* Search */}
      <div className="relative">
        <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" />
        <input
          type="text"
          value={q}
          onChange={e => setQ(e.target.value)}
          placeholder="Search by title, acronym, or description..."
          className="w-full bg-space-800 border border-space-700 text-white rounded-xl pl-11 pr-4 py-3 focus:outline-none focus:border-flame-500 placeholder-gray-500"
        />
      </div>

      {/* Filters */}
      <div className="space-y-3">
        <FilterRow label="Safety Category" options={SAFETY_CATS} active={filters.safety_category} onSelect={v => setFilter('safety_category', v)} />
        <FilterRow label="Fuel State" options={FUEL_STATES} active={filters.fuel_state} onSelect={v => setFilter('fuel_state', v)} />
        <FilterRow label="Gravity" options={GRAVITY_OPTS} active={filters.gravity_condition} onSelect={v => setFilter('gravity_condition', v)} />
        <FilterRow label="Telemetry" options={TELEMETRY_OPTS} active={filters.has_telemetry} onSelect={v => setFilter('has_telemetry', v)} />
      </div>

      {/* Result count */}
      <p className="text-gray-400 text-sm">
        Showing <span className="text-white font-semibold">{investigations.length}</span> of{' '}
        <span className="text-white font-semibold">{total || investigations.length}</span> investigations
      </p>

      {/* Grid */}
      {loading ? (
        <LoadingSpinner />
      ) : investigations.length === 0 ? (
        <EmptyState
          title="No investigations match your filters"
          message="Try clearing some filters or broadening your search."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {investigations.map(inv => (
            <InvestigationCard key={inv.investigation_id} investigation={inv} />
          ))}
        </div>
      )}
    </div>
  )
}

function FilterRow({ label, options, active, onSelect }) {
  return (
    <div className="flex items-center gap-3 flex-wrap">
      <span className="text-gray-500 text-xs w-28 flex-shrink-0">{label}:</span>
      <div className="flex flex-wrap gap-2">
        {options.map(opt => (
          <FilterChip
            key={opt}
            label={opt.charAt(0).toUpperCase() + opt.slice(1)}
            active={active === opt}
            onClick={() => onSelect(opt)}
          />
        ))}
      </div>
    </div>
  )
}

