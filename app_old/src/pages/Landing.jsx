import React from 'react'
import { Link } from 'react-router-dom'
import charizardLogo from '../assets/charizard.png'
import {
  Rocket,
  Search,
  ArrowRight,
  Flame,
  Shield,
  Layers,
  Activity,
  AlertTriangle,
  FileText,
  Compass,
  Cpu,
  Database,
  ExternalLink,
  ChevronRight,
  CheckCircle2,
} from 'lucide-react'

export default function Landing() {
  return (
    <div className="space-y-16 py-4">
      {/* ─── Hero Section with Charizard Symbol ───────────────────────────────── */}
      <section className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-space-900 via-space-900/90 to-space-950 border-2 border-space-700/80 p-8 lg:p-12 shadow-2xl">
        {/* Subtle background glow effect */}
        <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 bg-flame-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/3 -mb-20 w-80 h-80 bg-ember-400/10 rounded-full blur-3xl pointer-events-none" />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center relative z-10">
          {/* Left Column: Hero Text */}
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-flame-500/10 border border-flame-500/30 text-flame-400 text-xs font-mono font-medium tracking-wide">
              <Flame className="w-3.5 h-3.5 animate-pulse text-flame-400" />
              <span>NASA PHYSICAL SCIENCES INFORMATICS PLATFORM</span>
            </div>

            <div className="space-y-2">
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-display font-extrabold text-white tracking-tight leading-none">
                CHARIZARD
              </h1>
              <p className="text-xl sm:text-2xl text-transparent bg-clip-text bg-gradient-to-r from-flame-400 via-ember-400 to-amber-200 font-semibold tracking-tight">
                Microgravity Combustion Intelligence & Spacecraft Fire Safety Engine
              </p>
            </div>

            <p className="text-gray-300 text-sm sm:text-base leading-relaxed max-w-2xl">
              An authoritative research workspace transforming raw NASA microgravity combustion flight records,
              droplet extinguishment tables, and spacecraft fire demonstration telemetry into validated,
              model-ready scientific intelligence for deep space exploration.
            </p>

            {/* Action CTA Buttons */}
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <Link
                to="/overview"
                className="flex items-center gap-2 bg-gradient-to-r from-flame-500 to-flame-600 hover:from-flame-600 hover:to-flame-700 text-white font-semibold px-6 py-3.5 rounded-xl shadow-lg shadow-flame-500/25 transition-all transform hover:-translate-y-0.5"
              >
                <Activity className="w-4 h-4" />
                <span>Launch Mission Control</span>
                <ArrowRight className="w-4 h-4 ml-1" />
              </Link>
              <Link
                to="/explorer"
                className="flex items-center gap-2 bg-space-800 hover:bg-space-700 text-white font-semibold px-5 py-3.5 rounded-xl border border-space-600 transition-all hover:border-flame-500/50"
              >
                <Search className="w-4 h-4 text-flame-400" />
                <span>Explore 11 Investigations</span>
              </Link>
              <Link
                to="/ask"
                className="flex items-center gap-2 bg-space-900/80 hover:bg-space-800 text-gray-300 hover:text-white font-medium px-4 py-3.5 rounded-xl border border-space-700 text-sm transition-colors"
              >
                <span>Ask AI Agent</span>
              </Link>
            </div>

            {/* Quick telemetry badges */}
            <div className="pt-4 border-t border-space-800 flex flex-wrap gap-4 text-xs font-mono text-gray-400">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-green-400" />
                11 Core Investigations
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-flame-400" />
                2,241 Tabular Flight Runs
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-ember-400" />
                SHA-256 Provenance Verified
              </span>
            </div>
          </div>

          {/* Right Column: Charizard Mascot Symbol & Classic Retro Card */}
          <div className="lg:col-span-5 flex flex-col items-center justify-center space-y-4">
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-flame-500 to-amber-500 rounded-3xl blur-2xl opacity-30 group-hover:opacity-50 transition-opacity" />
              <div className="relative bg-space-950 p-6 rounded-2xl border-2 border-space-700 shadow-2xl flex flex-col items-center">
                <img
                  src={charizardLogo}
                  alt="Charizard Mission Emblem"
                  className="w-64 h-64 object-contain filter drop-shadow-[0_0_20px_rgba(249,115,22,0.6)] transform group-hover:scale-105 transition-transform duration-300"
                />

                {/* Classic Retro Pokemon Box / Mission Control Dialog */}
                <div className="w-full mt-3 bg-space-900 p-3 rounded-lg border-2 border-gray-400 font-mono text-xs text-gray-200 shadow-inner">
                  <div className="flex items-center justify-between border-b border-gray-700 pb-1.5 mb-1.5">
                    <span className="font-bold text-white tracking-wider flex items-center gap-1">
                      <span className="text-flame-500">▶</span> CHARIZARD
                    </span>
                    <span className="text-[10px] bg-flame-500/20 text-flame-400 border border-flame-500/40 px-1.5 py-0.5 rounded font-semibold">
                      LV. 100
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-[11px] text-gray-400">
                    <div>
                      <span>HP: </span>
                      <strong className="text-white">100 / 100</strong>
                    </div>
                    <div>
                      <span>ENV: </span>
                      <strong className="text-green-400">MICROGRAVITY</strong>
                    </div>
                  </div>
                  <div className="mt-2 text-[10px] text-gray-400 flex items-center justify-between border-t border-gray-800 pt-1.5">
                    <span>SPECIALTY:</span>
                    <span className="text-ember-400 font-semibold uppercase">Flames & Suppression</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Mission Telemetry Metric Grid ───────────────────────────────────── */}
      <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-space-800/80 p-5 rounded-xl border border-space-700 hover:border-flame-500/40 transition-colors">
          <div className="flex items-center justify-between text-gray-400 mb-2">
            <span className="text-xs font-mono uppercase tracking-wider">Flight Experiments</span>
            <Rocket className="w-4 h-4 text-flame-400" />
          </div>
          <div className="text-3xl font-display font-bold text-white">11</div>
          <p className="text-xs text-gray-400 mt-1">FLEX, Saffire, BASS, ACME, SPICE, SAME</p>
        </div>

        <div className="bg-space-800/80 p-5 rounded-xl border border-space-700 hover:border-flame-500/40 transition-colors">
          <div className="flex items-center justify-between text-gray-400 mb-2">
            <span className="text-xs font-mono uppercase tracking-wider">Telemetry Rows</span>
            <Database className="w-4 h-4 text-ember-400" />
          </div>
          <div className="text-3xl font-display font-bold text-white">2,241</div>
          <p className="text-xs text-gray-400 mt-1">Sensor logs with verified units & ranges</p>
        </div>

        <div className="bg-space-800/80 p-5 rounded-xl border border-space-700 hover:border-flame-500/40 transition-colors">
          <div className="flex items-center justify-between text-gray-400 mb-2">
            <span className="text-xs font-mono uppercase tracking-wider">Partial-G Gap</span>
            <AlertTriangle className="w-4 h-4 text-red-400" />
          </div>
          <div className="text-3xl font-display font-bold text-red-400">0 / 11</div>
          <p className="text-xs text-red-300 mt-1">Zero Moon/Mars partial gravity data</p>
        </div>

        <div className="bg-space-800/80 p-5 rounded-xl border border-space-700 hover:border-flame-500/40 transition-colors">
          <div className="flex items-center justify-between text-gray-400 mb-2">
            <span className="text-xs font-mono uppercase tracking-wider">Data Provenance</span>
            <Shield className="w-4 h-4 text-green-400" />
          </div>
          <div className="text-3xl font-display font-bold text-green-400">100%</div>
          <p className="text-xs text-gray-400 mt-1">SHA-256 verified manifests & DOI citations</p>
        </div>
      </section>

      {/* ─── Platform Architecture Blueprint ─────────────────────────────────── */}
      <section className="space-y-6">
        <div>
          <h2 className="text-2xl font-display font-bold text-white flex items-center gap-2.5">
            <Layers className="text-flame-500 w-6 h-6" />
            The Charizard Scientific Architecture
          </h2>
          <p className="text-gray-400 text-sm mt-1">
            End-to-end data pipeline connecting raw NASA S3 buckets to operational mission risk engines
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Step 1 */}
          <div className="bg-space-800 p-5 rounded-xl border border-space-700 space-y-3 relative overflow-hidden group hover:border-space-600 transition-colors">
            <div className="text-xs font-mono text-flame-400 font-bold">PHASE 01 // INGESTION</div>
            <h3 className="font-semibold text-white text-base">NASA PSI Geode Connector</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Harvests public S3 prefixes (unsigned requests) and reverse-engineered Geode backend REST APIs
              for metadata, flight reports, and tabular sensor tables under 25 MB.
            </p>
            <div className="text-[11px] font-mono text-gray-500 bg-space-900/60 p-2 rounded">
              boto3 • requests • pypdf
            </div>
          </div>

          {/* Step 2 */}
          <div className="bg-space-800 p-5 rounded-xl border border-space-700 space-y-3 relative overflow-hidden group hover:border-space-600 transition-colors">
            <div className="text-xs font-mono text-ember-400 font-bold">PHASE 02 // PROVENANCE</div>
            <h3 className="font-semibold text-white text-base">Cryptographic Manifests</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Generates immutable per-investigation JSON manifests with SHA-256 checksums, retrieval timestamps,
              and PDF text extraction with exact page delimiters for citations.
            </p>
            <div className="text-[11px] font-mono text-gray-500 bg-space-900/60 p-2 rounded">
              SHA-256 • manifests • page tags
            </div>
          </div>

          {/* Step 3 */}
          <div className="bg-space-800 p-5 rounded-xl border border-space-700 space-y-3 relative overflow-hidden group hover:border-space-600 transition-colors">
            <div className="text-xs font-mono text-blue-400 font-bold">PHASE 03 // EXTRACTION</div>
            <h3 className="font-semibold text-white text-base">Pydantic Fact Extraction</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Synthesizes structured schema values with mandatory evidence quotes. Enforces strict enums,
              physical unit conversion (mmHg → psi, mole fraction → %), and oxygen limits [0–100].
            </p>
            <div className="text-[11px] font-mono text-gray-500 bg-space-900/60 p-2 rounded">
              Pydantic v2 • Gemini 2.5 • AST
            </div>
          </div>

          {/* Step 4 */}
          <div className="bg-space-800 p-5 rounded-xl border border-space-700 space-y-3 relative overflow-hidden group hover:border-space-600 transition-colors">
            <div className="text-xs font-mono text-green-400 font-bold">PHASE 04 // DECISION ENGINE</div>
            <h3 className="font-semibold text-white text-base">Multi-Scenario Evaluation</h3>
            <p className="text-xs text-gray-400 leading-relaxed">
              Evaluates investigation relevance across ISS, Lunar Base, Mars Habitat, and Pressurized Rover
              profiles with transparent, rule-backed scoring rationales.
            </p>
            <div className="text-[11px] font-mono text-gray-500 bg-space-900/60 p-2 rounded">
              FastAPI • Plotly • Multi-Attribute
            </div>
          </div>
        </div>
      </section>

      {/* ─── Featured Flight Investigations Spotlight ─────────────────────────── */}
      <section className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 className="text-2xl font-display font-bold text-white flex items-center gap-2.5">
              <Flame className="text-flame-500 w-6 h-6" />
              Core Combustion Investigations
            </h2>
            <p className="text-gray-400 text-sm mt-1">
              Select flight experiments with rich telemetry logs and fire safety significance
            </p>
          </div>
          <Link
            to="/explorer"
            className="text-xs font-semibold text-flame-400 hover:text-flame-300 flex items-center gap-1 group self-start sm:self-auto"
          >
            <span>View All 11 Investigations</span>
            <ChevronRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Card 1: FLEX */}
          <div className="bg-space-800 p-6 rounded-xl border border-space-700 hover:border-flame-500/50 transition-all space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider bg-flame-500/10 text-flame-400 border border-flame-500/20 px-2.5 py-1 rounded-md font-mono">
                PSI-69 // FLEX
              </span>
              <span className="text-xs text-gray-400 font-mono">274 Flight Runs</span>
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Flame Extinguishment Experiment</h3>
              <p className="text-xs text-gray-300 mt-1 line-clamp-2">
                Fundamental droplet combustion in microgravity aboard ISS CIR/MDCA. Discovered spherical cool-flame
                burning and measured exact droplet extinction diameters across varying N2, He, and CO2 diluents.
              </p>
            </div>
            <div className="flex items-center justify-between pt-2 border-t border-space-700 text-xs">
              <span className="text-gray-400 font-mono">Fuel: Heptane / Methanol</span>
              <Link
                to="/investigation/PSI-69"
                className="text-flame-400 hover:text-white font-medium flex items-center gap-1"
              >
                <span>Inspect Experiment</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* Card 2: SAFFIRE-I */}
          <div className="bg-space-800 p-6 rounded-xl border border-space-700 hover:border-flame-500/50 transition-all space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider bg-ember-500/10 text-ember-400 border border-ember-500/20 px-2.5 py-1 rounded-md font-mono">
                PSI-98 // SAFFIRE-I
              </span>
              <span className="text-xs text-gray-400 font-mono">4 Large Burns</span>
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Spacecraft Fire Safety Experiment I</h3>
              <p className="text-xs text-gray-300 mt-1 line-clamp-2">
                Burned a full 0.4m x 1.0m SIBAL fabric composite sample inside a Cygnus cargo vehicle after ISS undocking.
                The largest intentional fire ever created aboard a spacecraft.
              </p>
            </div>
            <div className="flex items-center justify-between pt-2 border-t border-space-700 text-xs">
              <span className="text-gray-400 font-mono">Hardware: Cygnus Enclosure</span>
              <Link
                to="/investigation/PSI-98"
                className="text-flame-400 hover:text-white font-medium flex items-center gap-1"
              >
                <span>Inspect Experiment</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* Card 3: BASS-II */}
          <div className="bg-space-800 p-6 rounded-xl border border-space-700 hover:border-flame-500/50 transition-all space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2.5 py-1 rounded-md font-mono">
                PSI-25 // BASS-II
              </span>
              <span className="text-xs text-gray-400 font-mono">129 Test Runs</span>
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Burning and Suppression of Solids II</h3>
              <p className="text-xs text-gray-300 mt-1 line-clamp-2">
                Conducted in the Microgravity Science Glovebox (MSG). Systematically mapped flame spread rates
                and quenching limits across PMMA, cotton, and engineering polymers under variable forced flow.
              </p>
            </div>
            <div className="flex items-center justify-between pt-2 border-t border-space-700 text-xs">
              <span className="text-gray-400 font-mono">Safety: Detection & Suppression</span>
              <Link
                to="/investigation/PSI-25"
                className="text-flame-400 hover:text-white font-medium flex items-center gap-1"
              >
                <span>Inspect Experiment</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* Card 4: ACME CFI-G */}
          <div className="bg-space-800 p-6 rounded-xl border border-space-700 hover:border-flame-500/50 transition-all space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider bg-purple-500/10 text-purple-400 border border-purple-500/20 px-2.5 py-1 rounded-md font-mono">
                PSI-159 // ACME CFI-G
              </span>
              <span className="text-xs text-gray-400 font-mono">1,194 Flame Runs</span>
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Cool Flames Investigation with Gases</h3>
              <p className="text-xs text-gray-300 mt-1 line-clamp-2">
                Investigated spherical and opposed-flow gaseous diffusion flames in CIR. Examined low-temperature
                oxidation and extinction dynamics at oxygen concentrations down to 12%.
              </p>
            </div>
            <div className="flex items-center justify-between pt-2 border-t border-space-700 text-xs">
              <span className="text-gray-400 font-mono">Gas: Dimethyl Ether / Ethylene</span>
              <Link
                to="/investigation/PSI-159"
                className="text-flame-400 hover:text-white font-medium flex items-center gap-1"
              >
                <span>Inspect Experiment</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ─── The Artemis Partial-G Research Frontier Callout ─────────────────── */}
      <section className="bg-gradient-to-r from-red-950/40 via-space-900 to-space-900 border-2 border-red-500/40 rounded-2xl p-8 relative overflow-hidden shadow-xl">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
          <div className="space-y-3 max-w-2xl">
            <div className="inline-flex items-center gap-2 text-xs font-mono text-red-400 font-bold bg-red-500/10 px-2.5 py-1 rounded border border-red-500/20">
              <AlertTriangle className="w-4 h-4" />
              <span>CRITICAL RESEARCH GAP: THE PARTIAL-GRAVITY VOID</span>
            </div>
            <h3 className="text-2xl font-display font-bold text-white">
              Why Charizard Exists: Moon (0.16g) & Mars (0.38g) Flammability
            </h3>
            <p className="text-gray-300 text-sm leading-relaxed">
              NASA’s entire historical microgravity fire safety corpus is anchored in Earth orbit (≈0g).
              Because natural buoyant convection is non-linear, fire behavior in 1/6g (Lunar) or 3/8g (Martian)
              cannot be safely interpolated. Charizard systematically exposes this gap to direct future Artemis testing.
            </p>
          </div>
          <Link
            to="/gaps"
            className="flex-shrink-0 bg-red-600 hover:bg-red-700 text-white font-semibold px-6 py-3.5 rounded-xl transition-all shadow-lg shadow-red-600/20 flex items-center gap-2"
          >
            <span>Explore Gap Matrix</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      {/* ─── Bottom Navigation Shortcuts ─────────────────────────────────────── */}
      <section className="border-t border-space-800 pt-8 pb-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <Link
            to="/overview"
            className="p-4 rounded-xl bg-space-900/60 hover:bg-space-800 border border-space-800 hover:border-space-700 transition-colors block"
          >
            <Activity className="w-5 h-5 text-flame-400 mx-auto mb-2" />
            <div className="font-semibold text-sm text-white">Mission Control</div>
            <div className="text-xs text-gray-500 mt-0.5">Global overview metrics</div>
          </Link>

          <Link
            to="/compare"
            className="p-4 rounded-xl bg-space-900/60 hover:bg-space-800 border border-space-800 hover:border-space-700 transition-colors block"
          >
            <Layers className="w-5 h-5 text-ember-400 mx-auto mb-2" />
            <div className="font-semibold text-sm text-white">Comparative Lab</div>
            <div className="text-xs text-gray-500 mt-0.5">Side-by-side telemetry diffs</div>
          </Link>

          <Link
            to="/scenario"
            className="p-4 rounded-xl bg-space-900/60 hover:bg-space-800 border border-space-800 hover:border-space-700 transition-colors block"
          >
            <Rocket className="w-5 h-5 text-blue-400 mx-auto mb-2" />
            <div className="font-semibold text-sm text-white">Scenario Engine</div>
            <div className="text-xs text-gray-500 mt-0.5">ISS, Moon, Mars, Rover ranks</div>
          </Link>

          <Link
            to="/export"
            className="p-4 rounded-xl bg-space-900/60 hover:bg-space-800 border border-space-800 hover:border-space-700 transition-colors block"
          >
            <Database className="w-5 h-5 text-green-400 mx-auto mb-2" />
            <div className="font-semibold text-sm text-white">Data Export</div>
            <div className="text-xs text-gray-500 mt-0.5">CSV & JSON download</div>
          </Link>
        </div>
      </section>
    </div>
  )
}

