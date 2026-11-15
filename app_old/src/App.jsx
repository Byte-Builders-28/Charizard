import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout.jsx'
import Landing from './pages/Landing.jsx'
import Overview from './pages/Overview.jsx'
import Explorer from './pages/Explorer.jsx'
import InvestigationDetail from './pages/InvestigationDetail.jsx'
import Compare from './pages/Compare.jsx'
import ScenarioAnalysis from './pages/ScenarioAnalysis.jsx'
import AskAI from './pages/AskAI.jsx'
import ResearchGaps from './pages/ResearchGaps.jsx'
import DataExport from './pages/DataExport.jsx'

export default function App() {
  return (
    <BrowserRouter>
      <div className="dark">
        <Layout>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/overview" element={<Overview />} />
            <Route path="/explorer" element={<Explorer />} />
            <Route path="/investigation/:id" element={<InvestigationDetail />} />
            <Route path="/compare" element={<Compare />} />
            <Route path="/scenario" element={<ScenarioAnalysis />} />
            <Route path="/ask" element={<AskAI />} />
            <Route path="/gaps" element={<ResearchGaps />} />
            <Route path="/export" element={<DataExport />} />
          </Routes>
        </Layout>
      </div>
    </BrowserRouter>
  )
}
