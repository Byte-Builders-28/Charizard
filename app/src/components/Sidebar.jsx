import React from 'react'
import { NavLink } from 'react-router-dom'
import charizardLogo from '../assets/charizard.png'
import {
  Home,
  LayoutDashboard,
  Search,
  ArrowLeftRight,
  Rocket,
  MessageSquare,
  AlertTriangle,
  Download,
  Flame,
  Shield,
  Activity,
} from 'lucide-react'

const NAV = [
  { to: '/', label: 'Landing Page', icon: Home, end: true },
  { to: '/overview', label: 'Mission Control', icon: LayoutDashboard },
  { to: '/explorer', label: 'Investigation Explorer', icon: Search },
  { to: '/compare', label: 'Compare Lab', icon: ArrowLeftRight },
  { to: '/scenario', label: 'Scenario Engine', icon: Rocket },
  { to: '/ask', label: 'Ask Charizard AI', icon: MessageSquare },
  { to: '/gaps', label: 'Research Gaps', icon: AlertTriangle },
  { to: '/export', label: 'Data Export', icon: Download },
]

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-space-900 border-r border-space-700/80 flex flex-col z-30 shadow-2xl">
      {/* Brand Header with Charizard Symbol */}
      <NavLink
        to="/"
        className="px-5 py-4 border-b border-space-700/80 flex items-center gap-3 group hover:bg-space-800/50 transition-colors"
      >
        <div className="relative">
          <img
            src={charizardLogo}
            alt="Charizard Emblem"
            className="w-10 h-10 object-contain drop-shadow-[0_0_12px_rgba(255,107,26,0.5)] group-hover:scale-105 transition-transform"
          />
          <span className="absolute -bottom-1 -right-1 flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-flame-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-flame-500"></span>
          </span>
        </div>
        <div className="overflow-hidden">
          <div className="flex items-center gap-1.5">
            <span className="font-display font-bold text-white tracking-wider text-base">CHARIZARD</span>
            <span className="text-[9px] font-mono uppercase bg-flame-500/20 text-flame-400 border border-flame-500/30 px-1 py-0.5 rounded font-semibold">
              PSI
            </span>
          </div>
          <p className="text-gray-400 text-[10px] font-mono tracking-tight truncate">
            NASA Microgravity Intelligence
          </p>
        </div>
      </NavLink>

      {/* Classic Retro Mission Status Pill */}
      <div className="px-4 py-2 bg-space-950/70 border-b border-space-700/60 flex items-center justify-between text-[11px] font-mono">
        <span className="text-gray-400 flex items-center gap-1.5">
          <Activity className="w-3 h-3 text-green-400" />
          <span>STATUS: ONLINE</span>
        </span>
        <span className="text-ember-400 font-semibold">11 INVST</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="text-[10px] font-mono uppercase text-gray-400 tracking-wider px-3 mb-2 font-semibold">
          Platform Workspace
        </div>
        {NAV.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? 'bg-gradient-to-r from-flame-500/20 to-flame-500/5 text-flame-400 border-l-2 border-flame-500 font-semibold shadow-inner'
                  : 'text-gray-400 hover:text-white hover:bg-space-800/80'
              }`
            }
          >
            <Icon size={16} className="flex-shrink-0" />
            <span className="truncate">{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Classic Badge Footer */}
      <div className="px-4 py-3 border-t border-space-700/80 bg-space-950/40">
        <div className="border border-space-700 rounded-lg p-2.5 bg-space-900/60 text-xs">
          <div className="flex items-center justify-between text-[10px] font-mono text-gray-400 mb-1">
            <span className="flex items-center gap-1">
              <Shield className="w-3 h-3 text-flame-400" />
              <span>FIRE SAFETY</span>
            </span>
            <span className="text-gray-400">NASA PSI</span>
          </div>
          <div className="text-[11px] text-gray-300 font-mono flex items-center justify-between">
            <span>FLIGHT DATA:</span>
            <span className="text-white font-bold">2,241 RUNS</span>
          </div>
        </div>
      </div>
    </aside>
  )
}
