# NASA Combustion Science & Spacecraft Fire Safety Telemetry Report

**Generated at:** 2026-11-14T09:28:22.092478+00:00 UTC

**Dataset Location:** `.\data\combustion`

This report summarizes structured sensor logs, flammability measurements, and microgravity combustion telemetry downloaded from the NASA Physical Sciences Informatics (PSI) repository for the FlameScope fire-safety application.

## 1. Downloaded Telemetry & Sensor Datasets Overview

| Investigation | Mission / Acronym | File Name | Rows | Columns | Size (KB) |
|---|---|---|---|---|---|
| **PSI-69** | FLEX | `PSI-69_Experimental table_FLEX.csv` | 274 | 15 | 24.2 KB |
| **PSI-68** | FLEX-2 | `PSI-68_Experimental table_Flex2.csv` | 8 | 7 | 1.0 KB |
| **PSI-98** | SAFFIRE-I | `PSI-98_Experimental table_SAFFIRE-1.csv` | 4 | 13 | 0.5 KB |
| **PSI-99** | SAFFIRE-II | `PSI-99_Experimental table_SAFFIRE-2.csv` | 15 | 17 | 1.9 KB |
| **PSI-25** | BASS-II | `PSI-25_Experimental table_BASS-II.csv` | 129 | 17 | 16.2 KB |
| **PSI-26** | BASS | `PSI-26_Experimental table_BASS.csv` | 122 | 6 | 4.6 KB |
| **PSI-107** | SPICE | `PSI-107_Experimental table_Spice.csv` | 469 | 9 | 30.5 KB |
| **PSI-102** | SAME | `PSI-102_Experimental table_SAME.csv` | 8 | 5 | 0.3 KB |
| **PSI-159** | ACME CFI-G | `PSI-159_Experimental table_CFI-G_Normal Flames.csv` | 179 | 18 | 21.6 KB |
| **PSI-159** | ACME CFI-G | `PSI-159_Experimental table_CFI-G_Inverse Flames.csv` | 1015 | 20 | 38.5 KB |
| **PSI-20** | ACME BRE | `PSI-20_Experimental table_ACME BRE.csv` | 18 | 8 | 1.1 KB |

## 2. Detailed Dataset Schemas & Unit Dictionaries

### PSI-69: FLEX — `PSI-69_Experimental table_FLEX.csv`

- **Sub-Research Area:** Spacecraft Fire Safety
- **Total Rows:** 274
- **Total Columns:** 15
- **File Size:** 24,776 bytes

| Column Header | Clean Name | Inferred Unit | Data Type | Sample Value |
|---|---|---|---|---|
| `FLEX Test #` | **FLEX Test #** | `dimensionless / unspecified` | int64 | 1 |
| `FLEX Identifier` | **FLEX Identifier** | `dimensionless / unspecified` | object | 20CAL08 |
| `Test Date` | **Test Date** | `dimensionless / unspecified` | object | 3/5/2009 |
| `Test GMT` | **Test GMT** | `dimensionless / unspecified` | object | 17:22:03 |
| `Fuel` | **Fuel** | `dimensionless / unspecified` | object | Methanol |
| `Ambient pressure; mmHg` | **Ambient pressure** | `mmHg` | float64 | 757.7 |
| `O initial ambient composition; mole fraction` | **O initial ambient composition** | `mole fraction` | float64 | 0.21 |
| `N initial ambient composition; mole fraction` | **N initial ambient composition** | `mole fraction` | float64 | 0.79 |
| `CO initial ambient composition; mole fraction` | **CO initial ambient composition** | `mole fraction` | float64 | 0.0 |
| `He initial ambient composition; mole fraction` | **He initial ambient composition** | `mole fraction` | float64 | 0.0 |
| `Droplet initial diameter; mm` | **Droplet initial diameter** | `mm` | object | 1.69 |
| `Visible flame extinction diameter; mm` | **Visible flame extinction diameter** | `mm` | object | 0.89 |
| `Burning rate; mm` | **Burning rate** | `mm` | float64 | 0.52 |
| `Burn time; s` | **Burn time** | `s` | object | 4.3 |
| `Test end` | **Test end** | `dimensionless / unspecified` | object | Disruption |

### PSI-68: FLEX-2 — `PSI-68_Experimental table_Flex2.csv`

- **Sub-Research Area:** Spacecraft Fire Safety
- **Total Rows:** 8
- **Total Columns:** 7
- **File Size:** 1,029 bytes

| Column Header | Clean Name | Inferred Unit | Data Type | Sample Value |
|---|---|---|---|---|
| `Sample (Fuel Type)` | **Sample** | `Fuel Type` | object | IsoOctane (pure) |
| `Initial Droplet Diameter (mm)` | **Initial Droplet Diameter** | `mm` | object | 1.5 - 5 |
| `Ambient Gas Mixture ` | **Ambient Gas Mixture** | `dimensionless / unspecified` | object | O2/N2 or O2/He |
| `Oxygen Mole Fraction` | **Oxygen Mole Fraction** | `dimensionless / unspecified` | object | 0.17; 0.21;0.25; 0.3 |
| `Ambient Pressure (atm)` | **Ambient Pressure** | `atm` | object | 0.5; 1.0; 1.5; 2.0; or 3.0  |
| ` Ambient Temperature (C)` | **Ambient Temperature** | `C` | int64 | 25 |
| `Flow Velocity (cm/s)` | **Flow Velocity** | `cm/s` | object | 0.1 - 5 |

### PSI-98: SAFFIRE-I — `PSI-98_Experimental table_SAFFIRE-1.csv`

- **Sub-Research Area:** Spacecraft Fire, Smoke Distribution
- **Total Rows:** 4
- **Total Columns:** 13
- **File Size:** 469 bytes

| Column Header | Clean Name | Inferred Unit | Data Type | Sample Value |
|---|---|---|---|---|
| `Sample Number ` | **Sample Number** | `dimensionless / unspecified` | object | S1 |
| `Material` | **Material** | `dimensionless / unspecified` | object | SIBAL Fabric |
| `Sample Thickness (cm)` | **Sample Thickness** | `cm` | float64 | 0.37 |
| `Sample Length (cm)` | **Sample Length** | `cm` | float64 | 40.6 |
| `Sample Width (cm)` | **Sample Width** | `cm` | float64 | 94.0 |
| `Air Flow (cm/s)` | **Air Flow** | `cm/s` | float64 | 20.0 |
| `Percent O2` | **Percent O2** | `%` | object | 21.5 - 21.7 |
| `Ignition Power (W)` | **Ignition Power** | `W` | float64 | 182.0 |
| `Ignition Time (s)` | **Ignition Time** | `s` | float64 | 8.0 |
| `Burn Time (s)` | **Burn Time** | `s` | float64 | 420.0 |
| `Flow Direction ` | **Flow Direction** | `dimensionless / unspecified` | object | Concurrent |
| `Camera 1` | **Camera 1** | `dimensionless / unspecified` | object | S1C1 |
| `Camera 2` | **Camera 2** | `dimensionless / unspecified` | object | S1C2 |

### PSI-99: SAFFIRE-II — `PSI-99_Experimental table_SAFFIRE-2.csv`

- **Sub-Research Area:** Surface Combustion
- **Total Rows:** 15
- **Total Columns:** 17
- **File Size:** 1,973 bytes

| Column Header | Clean Name | Inferred Unit | Data Type | Sample Value |
|---|---|---|---|---|
| `Sample Number` | **Sample Number** | `dimensionless / unspecified` | object | 2-1 |
| `Material` | **Material** | `dimensionless / unspecified` | object | Silicone |
| `Samle Thickness ` | **Samle Thickness** | `dimensionless / unspecified` | object | 0.27 mm |
| `Sample Length ` | **Sample Length** | `dimensionless / unspecified` | object | 29 cm |
| `Sample Width (cm)` | **Sample Width** | `cm` | object | 5 cm |
| `Air Flow (cm/s)` | **Air Flow** | `cm/s` | object | 20 cm/s |
| `Percent O2 (Note 1)` | **Percent O2** | `Note 1` | object | ~ 21.5 |
| `Ignition Power (W)` | **Ignition Power** | `W` | object | 80 W |
| `Ignition Time (s)` | **Ignition Time** | `s` | object | 9.2 s |
| `Burn Time (s)` | **Burn Time** | `s` | object | Insignificant |
| `Flow Direction` | **Flow Direction** | `dimensionless / unspecified` | object | Concurrent |
| `?-g Burn Length` | **?-g Burn Length** | `dimensionless / unspecified` | object | ~ 0 |
| `?-g Spread Length` | **?-g Spread Length** | `dimensionless / unspecified` | object | 2.1 mm/s |
| `1-g Burn Length` | **1-g Burn Length** | `dimensionless / unspecified` | object | Complete |
| `1-g Spread Rate` | **1-g Spread Rate** | `dimensionless / unspecified` | object | Acceleratory |
| `Camera 1` | **Camera 1** | `dimensionless / unspecified` | object | S1C1 |
| `Camera 2` | **Camera 2** | `dimensionless / unspecified` | object | S1C2 |

### PSI-25: BASS-II — `PSI-25_Experimental table_BASS-II.csv`

- **Sub-Research Area:** Spacecraft Fire Safety
- **Total Rows:** 129
- **Total Columns:** 17
- **File Size:** 16,590 bytes

| Column Header | Clean Name | Inferred Unit | Data Type | Sample Value |
|---|---|---|---|---|
| `PI` | **PI** | `dimensionless / unspecified` | object | Bhattacharjee |
| `Test #` | **Test #** | `dimensionless / unspecified` | object | B1 |
| `Date` | **Date** | `dimensionless / unspecified` | object | 2/19/2014 |
| `GMT` | **GMT** | `dimensionless / unspecified` | int64 | 50 |
| `Sample #` | **Sample #** | `dimensionless / unspecified` | object | 147 |
| `Fuel Sample Material` | **Fuel Sample Material** | `dimensionless / unspecified` | object | 100 micron PMMA film   2 cm wide |
| `Flow restrictor` | **Flow restrictor** | `dimensionless / unspecified` | int64 | 2 |
| `Fan display` | **Fan display** | `dimensionless / unspecified` | object | 62 |
| `Air display` | **Air display** | `dimensionless / unspecified` | object | 5 |
| `Radiometer gain   (1000   250   50   10)` | **Radiometer gain   (1000   250   50   10)** | `dimensionless / unspecified` | object | 50 |
| `Total Frames Shot` | **Total Frames Shot** | `dimensionless / unspecified` | object | 57 |
| `Calibrated  initial O2 % by vol ` | **Calibrated  initial O2 % by vol** | `%` | float64 | 22.2 |
| `Calibrated final O2 % by vol` | **Calibrated final O2 % by vol** | `%` | object | 22.2 |
| `Initial CO2 % by vol` | **Initial CO2 % by vol** | `%` | object | 0.44 |
| `Final CO2 % by vol` | **Final CO2 % by vol** | `%` | object | 0.44 |
| `Initial CO (ppm)` | **Initial CO** | `ppm` | object | 0 |
| `Final CO (ppm)` | **Final CO** | `ppm` | object | 6 |

### PSI-26: BASS — `PSI-26_Experimental table_BASS.csv`

- **Sub-Research Area:** Spacecraft Fire Safety
- **Total Rows:** 122
- **Total Columns:** 6
- **File Size:** 4,726 bytes

| Column Header | Clean Name | Inferred Unit | Data Type | Sample Value |
|---|---|---|---|---|
| `Date` | **Date** | `dimensionless / unspecified` | object | 3/30/2012 |
| `GMT` | **GMT** | `dimensionless / unspecified` | int64 | 90 |
| `As Run Test #` | **As Run Test #** | `dimensionless / unspecified` | float64 | 1.0 |
| `Test #` | **Test #** | `dimensionless / unspecified` | object | 1 |
| `Sample #` | **Sample #** | `dimensionless / unspecified` | float64 | 4.0 |
| `Fuel Sample Material` | **Fuel Sample Material** | `dimensionless / unspecified` | object | SIBAL 2 cm |

### PSI-107: SPICE — `PSI-107_Experimental table_Spice.csv`

- **Sub-Research Area:** Fire Safety
- **Total Rows:** 469
- **Total Columns:** 9
- **File Size:** 31,205 bytes

| Column Header | Clean Name | Inferred Unit | Data Type | Sample Value |
|---|---|---|---|---|
| `GMT date` | **GMT date** | `dimensionless / unspecified` | int64 | 45 |
| `GMT ignition` | **GMT ignition** | `dimensionless / unspecified` | object | 14:37:08 |
| `GMT  Flame Off ` | **GMT  Flame Off** | `dimensionless / unspecified` | object | 14:48:03 |
| `Fuel` | **Fuel** | `dimensionless / unspecified` | object | Ethylene |
| `Nozzle (mm)` | **Nozzle** | `mm` | float64 | 1.6002 |
| `Fuel Rate (sccm)` | **Fuel Rate** | `sccm` | float64 | 103.8 |
| `Fuel Rate (mg/s)` | **Fuel Rate** | `mg/s` | float64 | 1.971 |
| `HC Fuel Rate (mg/s)` | **HC Fuel Rate** | `mg/s` | float64 | 1.971 |
| `Air Rate (cm/s)` | **Air Rate** | `cm/s` | float64 | 36.39 |

### PSI-102: SAME — `PSI-102_Experimental table_SAME.csv`

- **Sub-Research Area:** Spacecraft Fire Safety
- **Total Rows:** 8
- **Total Columns:** 5
- **File Size:** 331 bytes

| Column Header | Clean Name | Inferred Unit | Data Type | Sample Value |
|---|---|---|---|---|
| `Sample #` | **Sample #** | `dimensionless / unspecified` | int64 | 1 |
| `Sample Material  ` | **Sample Material** | `dimensionless / unspecified` | object | Teflon |
| `Air Flow (cm/s)` | **Air Flow** | `cm/s` | float64 | 5.0 |
| `Weight loss rate (mg/min)` | **Weight loss rate** | `mg/min` | float64 | 2.0 |
| `Aging Duration (minutes)` | **Aging Duration** | `minutes` | float64 | 1.0 |

### PSI-159: ACME CFI-G — `PSI-159_Experimental table_CFI-G_Normal Flames.csv`

- **Sub-Research Area:** Flames of Gaseous Fuels
- **Total Rows:** 179
- **Total Columns:** 18
- **File Size:** 22,166 bytes

| Column Header | Clean Name | Inferred Unit | Data Type | Sample Value |
|---|---|---|---|---|
| `Flame Type` | **Flame Type** | `dimensionless / unspecified` | object | Normal |
| `Day` | **Day** | `dimensionless / unspecified` | int64 | 1 |
| `Fuel` | **Fuel** | `dimensionless / unspecified` | object | ethane |
| `Test` | **Test** | `dimensionless / unspecified` | object | 21088A1 |
| `Cool flame?` | **Cool flame?** | `dimensionless / unspecified` | object | no, PCI-hot |
| ` XO2 before test` | **XO2 before test** | `dimensionless / unspecified` | float64 | 0.3939 |
| `XO2  after test` | **XO2  after test** | `dimensionless / unspecified` | float64 | 0.389822946 |
| `approx p (bar)` | **approx p** | `bar` | float64 | 0.9443956 |
| `Xf` | **Xf** | `dimensionless / unspecified` | float64 | 1.0 |
| `mHC (mg/s)` | **mHC** | `mg/s` | float64 | 2.0 |
| `TFP` | **TFP** | `dimensionless / unspecified` | object | No |
| `Tad (K)` | **Tad** | `K` | object | 2719.323211 |
| `Zst` | **Zst** | `dimensionless / unspecified` | object | 0.102651783 |
| `Hot ignition` | **Hot ignition** | `dimensionless / unspecified` | object | Yes |
| `burn time (sec)` | **burn time** | `sec` | float64 | 50.0 |
| `Self-ext or flow term` | **Self-ext or flow term** | `dimensionless / unspecified` | object | SE |
| `Peak burner T (C )` | **Peak burner T** | `C` | object | 290.617198 |
| `Comments` | **Comments** | `dimensionless / unspecified` | object | hit burner T limit |

### PSI-159: ACME CFI-G — `PSI-159_Experimental table_CFI-G_Inverse Flames.csv`

- **Sub-Research Area:** Flames of Gaseous Fuels
- **Total Rows:** 1015
- **Total Columns:** 20
- **File Size:** 39,422 bytes

| Column Header | Clean Name | Inferred Unit | Data Type | Sample Value |
|---|---|---|---|---|
| `Flame Type` | **Flame Type** | `dimensionless / unspecified` | object | Inverse |
| `Day` | **Day** | `dimensionless / unspecified` | float64 | 1.0 |
| `Fuel` | **Fuel** | `dimensionless / unspecified` | object | ethane |
| `Test` | **Test** | `dimensionless / unspecified` | object | 21196 A1 |
| `Xf  before test` | **Xf  before test** | `dimensionless / unspecified` | float64 | 0.2981 |
| `Xf  after test` | **Xf  after test** | `dimensionless / unspecified` | float64 | 0.2981 |
| `approx p (bar)` | **approx p** | `bar` | float64 | 1.1 |
| `XO2` | **XO2** | `dimensionless / unspecified` | float64 | 0.21 |
| `HC burnrate (mg/s)` | **HC burnrate** | `mg/s` | float64 | 1.5 |
| `O2 flow rate (mg/s)` | **O2 flow rate** | `mg/s` | float64 | 5.59 |
| `TFP` | **TFP** | `dimensionless / unspecified` | object | No |
| `Tad (K)` | **Tad** | `K` | float64 | 2120.0 |
| `Zst` | **Zst** | `dimensionless / unspecified` | float64 | 0.1665 |
| `Hot ignition` | **Hot ignition** | `dimensionless / unspecified` | object | No |
| `burn time (sec)` | **burn time** | `sec` | float64 | 0.0 |
| `Self -ext or flow term` | **Self -ext or flow term** | `dimensionless / unspecified` | object | - |
| `Peak burner Temp (C)` | **Peak burner Temp** | `C` | object | 27.1 |
| `Peak burner temp (K)` | **Peak burner temp** | `K` | object | 300.25 |
| `Color` | **Color** | `dimensionless / unspecified` | object | - |
| `Comments` | **Comments** | `dimensionless / unspecified` | object | Failed to ignite |

### PSI-20: ACME BRE — `PSI-20_Experimental table_ACME BRE.csv`

- **Sub-Research Area:** Flames of Gaseous Fuels
- **Total Rows:** 18
- **Total Columns:** 8
- **File Size:** 1,113 bytes

| Column Header | Clean Name | Inferred Unit | Data Type | Sample Value |
|---|---|---|---|---|
| `Year` | **Year** | `dimensionless / unspecified` | int64 | 2019 |
| `Month` | **Month** | `dimensionless / unspecified` | object | Feb |
| `Date` | **Date** | `dimensionless / unspecified` | int64 | 8 |
| `Burner Size (mm)` | **Burner Size** | `mm` | int64 | 25 |
| `Fuel Bottle` | **Fuel Bottle** | `dimensionless / unspecified` | object | 100% C2H4 |
| `Oxygen Conc (percent)` | **Oxygen Conc** | `percent` | object | 21; 26.5; 40 |
| `Flames Ignited` | **Flames Ignited** | `dimensionless / unspecified` | int64 | 10 |
| `Notes` | **Notes** | `dimensionless / unspecified` | object | Oxygen Conc. (as diluted with nitroge... |

