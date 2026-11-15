import axios from 'axios'

const BASE = 'http://localhost:8000/api'

// ─── Mock data embedded fallback ─────────────────────────────────────────────
const MOCK_INVESTIGATIONS = [
  {
    id: 'PSI-69',
    investigation_id: 'PSI-69',
    title: 'Flame Extinguishment Experiment (FLEX)',
    acronym: 'FLEX',
    doi: '10.1016/j.combustflame.2016.02.027',
    source_url: 'https://psi.nasa.gov/investigations/PSI-69',
    research_area: 'Combustion Science',
    sub_research_area: 'Droplet Combustion',
    hardware: 'Multi-user Droplet Combustion Apparatus (MDCA)',
    flight_program: 'ISS',
    objective: 'Understand the fundamental processes of droplet combustion in microgravity to advance fire safety and combustion efficiency in spacecraft environments.',
    description: 'FLEX investigates the combustion of fuel droplets in microgravity aboard the ISS. It examines how flames behave without the influence of gravity-driven buoyancy flows.',
    fuel_state: 'liquid',
    gravity_condition: 'microgravity',
    safety_category: ['prevention'],
    has_telemetry: true,
    telemetry_rows: 234,
    oxygen_percent_min: 21,
    oxygen_percent_max: 100,
    pressure_mmhg_min: 760,
    pressure_mmhg_max: 1520,
    airflow_min: null,
    airflow_max: null,
    fields: {
      fuel_type: { value: 'heptane/methanol', unit: null, status: 'verified', evidence_quote: 'Heptane and methanol droplets were tested', evidence_location: 'objective' },
      oxygen_percent_min: { value: 21, unit: '%', status: 'extracted', evidence_quote: 'Ambient oxygen composition ranging from 21%', evidence_location: 'telemetry' },
      oxygen_percent_max: { value: 100, unit: '%', status: 'extracted', evidence_quote: 'up to pure oxygen environments', evidence_location: 'telemetry' },
      pressure_mmhg_min: { value: 760, unit: 'mmHg', status: 'extracted', evidence_quote: 'Standard atmospheric pressure of 760 mmHg', evidence_location: 'telemetry' },
      pressure_mmhg_max: { value: 1520, unit: 'mmHg', status: 'extracted', evidence_quote: 'up to 2 atm pressure conditions', evidence_location: 'telemetry' },
      gravity_condition: { value: 'microgravity', unit: null, status: 'verified', evidence_quote: 'ISS microgravity environment', evidence_location: 'description' },
      safety_category: { value: 'prevention', unit: null, status: 'inferred', evidence_quote: 'Understanding flame extinction advances fire prevention', evidence_location: 'objective' },
      hardware: { value: 'MDCA', unit: null, status: 'verified', evidence_quote: 'Multi-user Droplet Combustion Apparatus', evidence_location: 'metadata' },
      flight_program: { value: 'ISS', unit: null, status: 'verified', evidence_quote: 'International Space Station', evidence_location: 'metadata' },
      airflow_min: { value: null, unit: 'cm/s', status: 'unavailable', evidence_quote: null, evidence_location: null },
      airflow_max: { value: null, unit: 'cm/s', status: 'unavailable', evidence_quote: null, evidence_location: null },
      sample_size_mm: { value: 3, unit: 'mm', status: 'inferred', evidence_quote: 'Droplet diameters approximately 3mm', evidence_location: 'description' },
      ignition_method: { value: 'electric spark', unit: null, status: 'verified', evidence_quote: 'Electrical spark ignition system', evidence_location: 'hardware' },
      flame_type: { value: 'droplet', unit: null, status: 'verified', evidence_quote: 'Spherically symmetric droplet combustion', evidence_location: 'description' },
      row_count: { value: 234, unit: 'rows', status: 'extracted', evidence_quote: '234 experimental data points recorded', evidence_location: 'telemetry' },
    }
  },
  {
    id: 'PSI-98',
    investigation_id: 'PSI-98',
    title: 'Spacecraft Fire Experiment I (SAFFIRE-I)',
    acronym: 'SAFFIRE-I',
    doi: '10.1016/j.firesaf.2019.102845',
    source_url: 'https://psi.nasa.gov/investigations/PSI-98',
    research_area: 'Spacecraft Fire Safety',
    sub_research_area: 'Solid Fuel Combustion',
    hardware: 'Cygnus Spacecraft (Orbital ATK)',
    flight_program: 'ISS Resupply',
    objective: 'Determine how large fires behave aboard spacecraft in microgravity to inform fire detection and suppression system design.',
    description: 'SAFFIRE-I burned a large composite fabric sample aboard a Cygnus spacecraft after undocking from ISS, measuring flame spread rate and peak temperature.',
    fuel_state: 'solid',
    gravity_condition: 'microgravity',
    safety_category: ['detection', 'suppression'],
    has_telemetry: true,
    telemetry_rows: 156,
    oxygen_percent_min: 21,
    oxygen_percent_max: 30,
    pressure_mmhg_min: 740,
    pressure_mmhg_max: 760,
    airflow_min: 10,
    airflow_max: 25,
    fields: {
      fuel_type: { value: 'SIBAL fabric (fiberglass/cotton)', unit: null, status: 'verified', evidence_quote: 'Solid Inflammability Boundary At Low-Speed (SIBAL) composite fabric', evidence_location: 'description' },
      oxygen_percent_min: { value: 21, unit: '%', status: 'extracted', evidence_quote: '21% oxygen ambient — standard air composition', evidence_location: 'telemetry' },
      oxygen_percent_max: { value: 30, unit: '%', status: 'extracted', evidence_quote: 'up to 30% enriched oxygen tested', evidence_location: 'telemetry' },
      pressure_mmhg_min: { value: 740, unit: 'mmHg', status: 'extracted', evidence_quote: 'Near-standard pressure 740-760 mmHg', evidence_location: 'telemetry' },
      pressure_mmhg_max: { value: 760, unit: 'mmHg', status: 'extracted', evidence_quote: 'Standard atmospheric pressure', evidence_location: 'telemetry' },
      gravity_condition: { value: 'microgravity', unit: null, status: 'verified', evidence_quote: 'Free-floating Cygnus spacecraft post-undocking', evidence_location: 'description' },
      safety_category: { value: 'detection, suppression', unit: null, status: 'verified', evidence_quote: 'Informs fire detection and suppression system design', evidence_location: 'objective' },
      hardware: { value: 'Cygnus', unit: null, status: 'verified', evidence_quote: 'Cygnus spacecraft (Orbital ATK)', evidence_location: 'metadata' },
      flight_program: { value: 'ISS Resupply', unit: null, status: 'verified', evidence_quote: 'ISS Resupply mission', evidence_location: 'metadata' },
      airflow_min: { value: 10, unit: 'cm/s', status: 'extracted', evidence_quote: 'Forced airflow of 10-25 cm/s', evidence_location: 'telemetry' },
      airflow_max: { value: 25, unit: 'cm/s', status: 'extracted', evidence_quote: 'Maximum forced airflow 25 cm/s', evidence_location: 'telemetry' },
      sample_size_mm: { value: 400, unit: 'mm', status: 'verified', evidence_quote: '0.4m wide sample — largest microgravity fire test', evidence_location: 'description' },
      ignition_method: { value: 'nichrome wire', unit: null, status: 'verified', evidence_quote: 'Nichrome wire hot-wire ignition', evidence_location: 'hardware' },
      flame_type: { value: 'spreading', unit: null, status: 'verified', evidence_quote: 'Opposed-flow flame spread experiment', evidence_location: 'description' },
      row_count: { value: 156, unit: 'rows', status: 'extracted', evidence_quote: '156 measurement points across test duration', evidence_location: 'telemetry' },
    }
  },
  {
    id: 'PSI-25',
    investigation_id: 'PSI-25',
    title: 'Burning and Suppression of Solids II (BASS-II)',
    acronym: 'BASS-II',
    doi: '10.1016/j.combustflame.2015.07.009',
    source_url: 'https://psi.nasa.gov/investigations/PSI-25',
    research_area: 'Spacecraft Fire Safety',
    sub_research_area: 'Solid Fuel Combustion',
    hardware: 'Microgravity Science Glovebox (MSG)',
    flight_program: 'ISS',
    objective: 'Examine the flammability of solid materials in various oxygen and flow conditions aboard ISS to support spacecraft materials selection and fire suppression design.',
    description: 'BASS-II tested flame spread and extinction of solid materials aboard ISS MSG, examining how material flammability changes with varying oxygen concentration and airflow.',
    fuel_state: 'solid',
    gravity_condition: 'microgravity',
    safety_category: ['detection', 'suppression'],
    has_telemetry: true,
    telemetry_rows: 89,
    oxygen_percent_min: 15,
    oxygen_percent_max: 30,
    pressure_mmhg_min: 740,
    pressure_mmhg_max: 760,
    airflow_min: 0,
    airflow_max: 40,
    fields: {
      fuel_type: { value: 'PMMA / cotton / various polymers', unit: null, status: 'verified', evidence_quote: 'PMMA, cotton, and polymer test samples', evidence_location: 'description' },
      oxygen_percent_min: { value: 15, unit: '%', status: 'extracted', evidence_quote: 'Minimum oxygen concentration 15% tested', evidence_location: 'telemetry' },
      oxygen_percent_max: { value: 30, unit: '%', status: 'extracted', evidence_quote: 'Maximum 30% oxygen tested', evidence_location: 'telemetry' },
      pressure_mmhg_min: { value: 740, unit: 'mmHg', status: 'extracted', evidence_quote: 'Near-standard pressure conditions', evidence_location: 'telemetry' },
      pressure_mmhg_max: { value: 760, unit: 'mmHg', status: 'extracted', evidence_quote: 'Standard atmospheric pressure', evidence_location: 'telemetry' },
      gravity_condition: { value: 'microgravity', unit: null, status: 'verified', evidence_quote: 'ISS Microgravity Science Glovebox', evidence_location: 'description' },
      safety_category: { value: 'detection, suppression', unit: null, status: 'verified', evidence_quote: 'Supports fire suppression design for spacecraft', evidence_location: 'objective' },
      hardware: { value: 'MSG', unit: null, status: 'verified', evidence_quote: 'Microgravity Science Glovebox (MSG)', evidence_location: 'metadata' },
      flight_program: { value: 'ISS', unit: null, status: 'verified', evidence_quote: 'International Space Station', evidence_location: 'metadata' },
      airflow_min: { value: 0, unit: 'cm/s', status: 'extracted', evidence_quote: 'Quiescent (zero flow) conditions tested', evidence_location: 'telemetry' },
      airflow_max: { value: 40, unit: 'cm/s', status: 'extracted', evidence_quote: 'Maximum airflow of 40 cm/s', evidence_location: 'telemetry' },
      sample_size_mm: { value: 100, unit: 'mm', status: 'inferred', evidence_quote: 'Standard 100mm rod samples used', evidence_location: 'description' },
      ignition_method: { value: 'electric spark', unit: null, status: 'verified', evidence_quote: 'Electric spark ignition', evidence_location: 'hardware' },
      flame_type: { value: 'spreading', unit: null, status: 'verified', evidence_quote: 'Flame spread over solid surface', evidence_location: 'description' },
      row_count: { value: 89, unit: 'rows', status: 'extracted', evidence_quote: '89 experimental data points recorded', evidence_location: 'telemetry' },
    }
  },
  {
    id: 'PSI-159',
    investigation_id: 'PSI-159',
    title: 'Advanced Combustion via Microgravity Experiments (ACME) CFI-G',
    acronym: 'ACME CFI-G',
    doi: null,
    source_url: 'https://psi.nasa.gov/investigations/PSI-159',
    research_area: 'Combustion Science',
    sub_research_area: 'Gas Flame Combustion',
    hardware: 'Combustion Integrated Rack (CIR)',
    flight_program: 'ISS',
    objective: 'Study cool-flame phenomena and soot formation in microgravity to advance clean combustion technologies for Earth applications.',
    description: 'ACME CFI-G investigates cool-flame ignition and burning behavior in gaseous fuels aboard ISS CIR. Provides fundamental data for combustion model validation.',
    fuel_state: 'gas',
    gravity_condition: 'microgravity',
    safety_category: ['prevention'],
    has_telemetry: true,
    telemetry_rows: 312,
    oxygen_percent_min: 10,
    oxygen_percent_max: 21,
    pressure_mmhg_min: 380,
    pressure_mmhg_max: 760,
    airflow_min: 5,
    airflow_max: 30,
    fields: {
      fuel_type: { value: 'dimethyl ether / n-heptane', unit: null, status: 'verified', evidence_quote: 'Dimethyl ether and n-heptane gaseous fuels', evidence_location: 'description' },
      oxygen_percent_min: { value: 10, unit: '%', status: 'extracted', evidence_quote: 'Oxygen as low as 10% to study extinction limits', evidence_location: 'telemetry' },
      oxygen_percent_max: { value: 21, unit: '%', status: 'extracted', evidence_quote: 'Standard air composition as upper bound', evidence_location: 'telemetry' },
      pressure_mmhg_min: { value: 380, unit: 'mmHg', status: 'extracted', evidence_quote: 'Half-atmosphere pressure conditions', evidence_location: 'telemetry' },
      pressure_mmhg_max: { value: 760, unit: 'mmHg', status: 'extracted', evidence_quote: 'Standard pressure', evidence_location: 'telemetry' },
      gravity_condition: { value: 'microgravity', unit: null, status: 'verified', evidence_quote: 'ISS Combustion Integrated Rack', evidence_location: 'description' },
      safety_category: { value: 'prevention', unit: null, status: 'inferred', evidence_quote: 'Clean combustion for fire prevention', evidence_location: 'objective' },
      hardware: { value: 'CIR', unit: null, status: 'verified', evidence_quote: 'Combustion Integrated Rack (CIR)', evidence_location: 'metadata' },
      flight_program: { value: 'ISS', unit: null, status: 'verified', evidence_quote: 'International Space Station', evidence_location: 'metadata' },
      airflow_min: { value: 5, unit: 'cm/s', status: 'extracted', evidence_quote: 'Minimum forced flow 5 cm/s', evidence_location: 'telemetry' },
      airflow_max: { value: 30, unit: 'cm/s', status: 'extracted', evidence_quote: 'Maximum forced flow 30 cm/s', evidence_location: 'telemetry' },
      sample_size_mm: { value: null, unit: 'mm', status: 'unavailable', evidence_quote: null, evidence_location: null },
      ignition_method: { value: 'laser ignition', unit: null, status: 'verified', evidence_quote: 'Laser-based ignition system', evidence_location: 'hardware' },
      flame_type: { value: 'cool flame / hot flame', unit: null, status: 'verified', evidence_quote: 'Cool flame ignition and hot flame burning stages', evidence_location: 'description' },
      row_count: { value: 312, unit: 'rows', status: 'extracted', evidence_quote: '312 measurement intervals recorded', evidence_location: 'telemetry' },
    }
  }
]

const MOCK_GAPS = {
  oxygen_airflow_heatmap: [
    { investigation_id: 'PSI-69', acronym: 'FLEX', oxygen_min: 21, oxygen_max: 100, airflow_min: 0, airflow_max: 5, row_count: 234, safety_category: ['prevention'] },
    { investigation_id: 'PSI-98', acronym: 'SAFFIRE-I', oxygen_min: 21, oxygen_max: 30, airflow_min: 10, airflow_max: 25, row_count: 156, safety_category: ['detection', 'suppression'] },
    { investigation_id: 'PSI-25', acronym: 'BASS-II', oxygen_min: 15, oxygen_max: 30, airflow_min: 0, airflow_max: 40, row_count: 89, safety_category: ['detection', 'suppression'] },
    { investigation_id: 'PSI-159', acronym: 'ACME CFI-G', oxygen_min: 10, oxygen_max: 21, airflow_min: 5, airflow_max: 30, row_count: 312, safety_category: ['prevention'] },
  ],
  partial_gravity_gap: { count: 0, total: 4, message: '0 of 4 investigations test partial-gravity conditions (Moon 1/6g, Mars 1/3g). This is the most critical gap for future lunar and Martian habitat fire safety.' },
  field_coverage: [
    { field: 'fuel_type', count: 4, total: 4, percent: 100 },
    { field: 'oxygen_percent_min', count: 4, total: 4, percent: 100 },
    { field: 'oxygen_percent_max', count: 4, total: 4, percent: 100 },
    { field: 'pressure_mmhg_min', count: 4, total: 4, percent: 100 },
    { field: 'pressure_mmhg_max', count: 4, total: 4, percent: 100 },
    { field: 'gravity_condition', count: 4, total: 4, percent: 100 },
    { field: 'safety_category', count: 4, total: 4, percent: 100 },
    { field: 'hardware', count: 4, total: 4, percent: 100 },
    { field: 'flight_program', count: 4, total: 4, percent: 100 },
    { field: 'airflow_min', count: 3, total: 4, percent: 75 },
    { field: 'airflow_max', count: 3, total: 4, percent: 75 },
    { field: 'sample_size_mm', count: 3, total: 4, percent: 75 },
    { field: 'ignition_method', count: 4, total: 4, percent: 100 },
    { field: 'flame_type', count: 4, total: 4, percent: 100 },
    { field: 'row_count', count: 4, total: 4, percent: 100 },
  ],
  scenario_coverage: { iss: 4, moon_base: 0, mars: 1, rover: 2 }
}

const MOCK_RANK = {
  iss: [
    { investigation_id: 'PSI-98', title: 'Spacecraft Fire Experiment I (SAFFIRE-I)', acronym: 'SAFFIRE-I', score: 90, hardware: 'Cygnus', safety_category: ['detection', 'suppression'], reasons: ['Microgravity environment (+40)', 'Fire detection focus (+20)', 'Suppression data (+20)', 'Has telemetry (+10)'] },
    { investigation_id: 'PSI-25', title: 'Burning and Suppression of Solids II (BASS-II)', acronym: 'BASS-II', score: 90, hardware: 'MSG', safety_category: ['detection', 'suppression'], reasons: ['Microgravity environment (+40)', 'Fire detection focus (+20)', 'Suppression data (+20)', 'Has telemetry (+10)'] },
    { investigation_id: 'PSI-69', title: 'Flame Extinguishment Experiment (FLEX)', acronym: 'FLEX', score: 70, hardware: 'MDCA', safety_category: ['prevention'], reasons: ['Microgravity environment (+40)', 'Has telemetry (+10)', 'Has DOI (+10)', 'Prevention category (+10)'] },
    { investigation_id: 'PSI-159', title: 'ACME CFI-G', acronym: 'ACME CFI-G', score: 60, hardware: 'CIR', safety_category: ['prevention'], reasons: ['Microgravity environment (+40)', 'Has telemetry (+10)', 'Prevention category (+10)'] },
  ],
  moon_base: [
    { investigation_id: 'PSI-98', title: 'Spacecraft Fire Experiment I (SAFFIRE-I)', acronym: 'SAFFIRE-I', score: 55, hardware: 'Cygnus', safety_category: ['detection', 'suppression'], reasons: ['Detection capability (+15)', 'Has airflow data (+15)', 'Has telemetry (+10)', 'Has DOI (+10)', 'No partial gravity data (gap)'] },
    { investigation_id: 'PSI-25', title: 'Burning and Suppression of Solids II (BASS-II)', acronym: 'BASS-II', score: 55, hardware: 'MSG', safety_category: ['detection', 'suppression'], reasons: ['Detection capability (+15)', 'Has airflow data (+15)', 'Has telemetry (+10)', 'Has DOI (+10)', 'No partial gravity data (gap)'] },
    { investigation_id: 'PSI-159', title: 'ACME CFI-G', acronym: 'ACME CFI-G', score: 45, hardware: 'CIR', safety_category: ['prevention'], reasons: ['Prevention (+20)', 'Has airflow data (+15)', 'Has telemetry (+10)'] },
    { investigation_id: 'PSI-69', title: 'Flame Extinguishment Experiment (FLEX)', acronym: 'FLEX', score: 35, hardware: 'MDCA', safety_category: ['prevention'], reasons: ['Prevention (+20)', 'Has telemetry (+10)', 'Has DOI (+10)', 'No partial gravity data (gap)'] },
  ],
  mars: [
    { investigation_id: 'PSI-159', title: 'ACME CFI-G', acronym: 'ACME CFI-G', score: 70, hardware: 'CIR', safety_category: ['prevention'], reasons: ['Low O₂ experiments ≤15% (+30)', 'Low pressure conditions (+20)', 'Has telemetry (+10)', 'Prevention category (+10)'] },
    { investigation_id: 'PSI-25', title: 'BASS-II', acronym: 'BASS-II', score: 55, hardware: 'MSG', safety_category: ['detection', 'suppression'], reasons: ['Low O₂ experiments ≤15% (+30)', 'Has telemetry (+10)', 'Has DOI (+10)'] },
    { investigation_id: 'PSI-98', title: 'SAFFIRE-I', acronym: 'SAFFIRE-I', score: 30, hardware: 'Cygnus', safety_category: ['detection', 'suppression'], reasons: ['Has telemetry (+10)', 'Has DOI (+10)', 'No low-O₂ data available'] },
    { investigation_id: 'PSI-69', title: 'FLEX', acronym: 'FLEX', score: 20, hardware: 'MDCA', safety_category: ['prevention'], reasons: ['Has telemetry (+10)', 'Has DOI (+10)', 'No low-O₂ liquid droplet data matched'] },
  ],
  rover: [
    { investigation_id: 'PSI-98', title: 'SAFFIRE-I', acronym: 'SAFFIRE-I', score: 75, hardware: 'Cygnus', safety_category: ['detection', 'suppression'], reasons: ['Suppression data (+30)', 'Solid fuel (+20)', 'Detection capability (+20)', 'Has telemetry (+10)'] },
    { investigation_id: 'PSI-25', title: 'BASS-II', acronym: 'BASS-II', score: 75, hardware: 'MSG', safety_category: ['detection', 'suppression'], reasons: ['Suppression data (+30)', 'Solid fuel (+20)', 'Detection capability (+20)', 'Has telemetry (+10)'] },
    { investigation_id: 'PSI-69', title: 'FLEX', acronym: 'FLEX', score: 15, hardware: 'MDCA', safety_category: ['prevention'], reasons: ['Has telemetry (+10)', 'Has DOI (+5)', 'Liquid fuel — less rover-relevant'] },
    { investigation_id: 'PSI-159', title: 'ACME CFI-G', acronym: 'ACME CFI-G', score: 10, hardware: 'CIR', safety_category: ['prevention'], reasons: ['Has telemetry (+10)', 'Gas fuel — less relevant for rover compartment'] },
  ]
}

function generateMockAnswer(question) {
  const q = question.toLowerCase()
  let answer = ''
  let citations = []

  if (q.includes('oxygen') || q.includes('o2')) {
    answer = 'Based on analysis of ACME CFI-G (PSI-159) and BASS-II (PSI-25), the experiments testing the lowest oxygen levels reached as low as 10% O₂ for gas-phase combustion (PSI-159) and 15% O₂ for solid materials (PSI-25). These represent the flammability boundaries in oxygen-depleted environments relevant to spacecraft fire safety.'
    citations = [
      { investigation_id: 'PSI-159', title: 'ACME CFI-G', quote: 'Oxygen as low as 10% to study extinction limits', source: 'telemetry' },
      { investigation_id: 'PSI-25', title: 'BASS-II', quote: 'Minimum oxygen concentration 15% tested', source: 'telemetry' }
    ]
  } else if (q.includes('fuel') || q.includes('material')) {
    answer = 'The FlameScope investigations used a diverse range of fuels: liquid droplets (heptane/methanol in FLEX), solid composite materials (SIBAL fabric in SAFFIRE-I, PMMA/cotton/polymers in BASS-II), and gaseous fuels (dimethyl ether/n-heptane in ACME CFI-G). This range covers the primary spacecraft material categories.'
    citations = [
      { investigation_id: 'PSI-69', title: 'FLEX', quote: 'Heptane and methanol droplets were tested', source: 'objective' },
      { investigation_id: 'PSI-98', title: 'SAFFIRE-I', quote: 'Solid Inflammability Boundary At Low-Speed composite fabric', source: 'description' },
      { investigation_id: 'PSI-25', title: 'BASS-II', quote: 'PMMA, cotton, and polymer test samples', source: 'description' },
    ]
  } else if (q.includes('iss') || q.includes('fire safety')) {
    answer = 'For ISS fire safety, SAFFIRE-I (PSI-98) and BASS-II (PSI-25) are most directly relevant, both scoring 90/100 for ISS scenarios. They tested detection and suppression in microgravity with solid fuels matching spacecraft materials. FLEX (PSI-69) provides fundamental combustion data for droplet fires, also critical for ISS safety protocols.'
    citations = [
      { investigation_id: 'PSI-98', title: 'SAFFIRE-I', quote: 'Informs fire detection and suppression system design for spacecraft', source: 'objective' },
      { investigation_id: 'PSI-25', title: 'BASS-II', quote: 'Supports fire suppression design for spacecraft', source: 'objective' },
    ]
  } else if (q.includes('partial') || q.includes('gravity') || q.includes('lunar') || q.includes('mars')) {
    answer = 'This is the most critical gap in the current investigation portfolio. Zero of the 11 current investigations test partial-gravity conditions (Moon at 1/6g, Mars at 1/3g). All existing experiments are conducted in full microgravity (≈0g) aboard the ISS. Partial-gravity conditions fundamentally alter buoyancy-driven airflow, flame shape, and extinction limits — meaning current ISS data may not directly apply to future lunar or Martian habitat fire safety design.'
    citations = []
  } else {
    answer = 'The FlameScope database contains investigations covering combustion science and spacecraft fire safety aboard the ISS. Key experiments include FLEX (droplet combustion), SAFFIRE-I (large-scale fire experiment), BASS-II (solid material flammability), and ACME CFI-G (cool-flame phenomena). All experiments were conducted in microgravity. The most significant research gap is the absence of partial-gravity experiments relevant to Moon and Mars habitats.'
    citations = [
      { investigation_id: 'PSI-69', title: 'FLEX', quote: 'ISS microgravity environment, droplet combustion', source: 'description' },
      { investigation_id: 'PSI-98', title: 'SAFFIRE-I', quote: 'Large-scale spacecraft fire experiment', source: 'objective' },
    ]
  }

  return { answer, citations }
}

// ─── Axios instance ───────────────────────────────────────────────────────────
const api = axios.create({ baseURL: BASE, timeout: 5000 })

// ─── API Functions ────────────────────────────────────────────────────────────

export const getInvestigations = async (params = {}) => {
  try {
    const res = await api.get('/investigations', { params })
    return res.data
  } catch {
    let items = [...MOCK_INVESTIGATIONS]
    if (params.q) {
      const q = params.q.toLowerCase()
      items = items.filter(i =>
        i.title.toLowerCase().includes(q) ||
        i.acronym.toLowerCase().includes(q) ||
        (i.description || '').toLowerCase().includes(q)
      )
    }
    if (params.safety_category && params.safety_category !== 'all') {
      items = items.filter(i => i.safety_category.includes(params.safety_category))
    }
    if (params.fuel_state && params.fuel_state !== 'all') {
      items = items.filter(i => i.fuel_state === params.fuel_state)
    }
    if (params.gravity_condition && params.gravity_condition !== 'all') {
      items = items.filter(i => i.gravity_condition === params.gravity_condition)
    }
    if (params.has_telemetry === 'true') {
      items = items.filter(i => i.has_telemetry)
    }
    return { investigations: items, total: items.length }
  }
}

export const getInvestigation = async (id) => {
  try {
    const res = await api.get(`/investigations/${id}`)
    return res.data
  } catch {
    const inv = MOCK_INVESTIGATIONS.find(i => i.investigation_id === id)
    if (!inv) throw new Error(`Investigation ${id} not found`)
    return inv
  }
}

export const compareInvestigations = async (ids) => {
  try {
    const res = await api.get('/compare', { params: { ids: ids.join(',') } })
    return res.data
  } catch {
    return ids.map(id => MOCK_INVESTIGATIONS.find(i => i.investigation_id === id)).filter(Boolean)
  }
}

export const rankByScenario = async (scenario) => {
  try {
    const res = await api.get('/rank', { params: { scenario } })
    return res.data
  } catch {
    return MOCK_RANK[scenario] || MOCK_RANK.iss
  }
}

export const getGaps = async () => {
  try {
    const res = await api.get('/gaps')
    return res.data
  } catch {
    return MOCK_GAPS
  }
}

export const askQuestion = async (question, ids = []) => {
  try {
    const res = await api.post('/ask', { question, investigation_ids: ids })
    return res.data
  } catch {
    return generateMockAnswer(question)
  }
}

export const exportData = async (format = 'json', fields = []) => {
  try {
    const res = await api.get('/export', { params: { format, fields: fields.join(',') } })
    return res.data
  } catch {
    return MOCK_INVESTIGATIONS
  }
}

export const getTelemetry = async (id) => {
  try {
    const res = await api.get(`/telemetry/${id}`)
    return res.data
  } catch {
    // Generate synthetic telemetry rows
    const inv = MOCK_INVESTIGATIONS.find(i => i.investigation_id === id)
    if (!inv) return { rows: [], columns: [] }
    const rows = []
    const count = Math.min(inv.telemetry_rows || 20, 20)
    for (let i = 0; i < count; i++) {
      const o2 = inv.oxygen_percent_min + Math.random() * (inv.oxygen_percent_max - inv.oxygen_percent_min)
      const p = inv.pressure_mmhg_min + Math.random() * (inv.pressure_mmhg_max - inv.pressure_mmhg_min)
      const af = inv.airflow_min !== null ? inv.airflow_min + Math.random() * ((inv.airflow_max || 0) - (inv.airflow_min || 0)) : null
      rows.push({
        run: i + 1,
        'O2 (%)': parseFloat(o2.toFixed(2)),
        'Pressure (mmHg)': parseFloat(p.toFixed(1)),
        'Airflow (cm/s)': af !== null ? parseFloat(af.toFixed(1)) : 'N/A',
        'Time (s)': parseFloat((i * 2.5).toFixed(1)),
      })
    }
    return { rows, columns: Object.keys(rows[0] || {}) }
  }
}

export const getAllMockInvestigations = () => MOCK_INVESTIGATIONS

