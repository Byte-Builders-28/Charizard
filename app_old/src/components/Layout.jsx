import React from 'react'
import Sidebar from './Sidebar.jsx'

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-space-950 flex font-sans antialiased selection:bg-flame-500 selection:text-white">
      <Sidebar />
      <main className="flex-1 ml-64 min-h-screen overflow-auto bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-space-900 via-space-950 to-space-950">
        <div className="px-8 py-8 max-w-7xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  )
}
