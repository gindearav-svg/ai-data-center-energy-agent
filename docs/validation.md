# Validation Report

## Purpose

This document records how the first regional-comparison prototype was
tested and validated.

The objective is to confirm that the application performs reproducible
calculations, rejects invalid inputs, preserves data provenance, and
does not overstate what its current datasets support.

## Baseline scenario

- IT load: 200 MW
- PUE: 1.25
- Average utilization: 95%
- Price year: 2025
- Emissions year: 2023

## Manual calculation validation

### Facility load

200 MW × 1.25 = 250 MW

Application result: 250 MW

Status: Passed

### Annual electricity

250 MW × 8,760 hours × 0.95 =
2,080,500 MWh

Application result: 2,080,500 MWh

Status: Passed

### North Texas annual wholesale cost

2,080,500 MWh × $33.401/MWh =
$69,490,780.50

Application result: $69,490,780.50

Status: Passed

### Houston annual wholesale cost

2,080,500 MWh × $34.566/MWh =
$71,914,563.00

Application result: $71,914,563.00

Status: Passed

### West Texas annual wholesale cost

2,080,500 MWh × $42.716/MWh =
$88,870,638.00

Application result: $88,870,638.00

Status: Passed

### Annual operational emissions

2,080,500 MWh × 334.129 kg CO2e/MWh ÷ 1,000 =
695,155.3845 metric tons CO2e

Application result:
695,155.3845 metric tons CO2e

Status: Passed

## Data-quality validation

The processed dataset contains:

- Three expected candidate regions
- 8,760 price observations per region
- Unique ERCOT settlement-point identifiers
- Unique NOAA station identifiers
- Complete required values
- 2025 price metadata
- 2023 emissions metadata
- Logically ordered minimum, average, median, and maximum prices

## Input-validation scenarios

| Scenario | Expected behavior | Result |
|---|---|---|
| 200 MW, 1.25 PUE, 95% utilization | Produce baseline comparison | Passed |
| 100 MW, 1.20 PUE, 90% utilization | Produce scaled comparison | Passed |
| Negative IT load | Reject input | Passed |
| PUE below 1.0 | Reject input | Passed |
| Utilization above 100% | Reject input | Passed |
| Non-numerical load | Reject input | Passed |

## Automated tests

The project currently contains tests covering:

- Facility-load calculations
- Annual-energy calculations
- Annual-cost calculations
- Operational-emissions calculations
- Invalid numerical inputs
- Regional cost ranking
- Required analysis columns
- Expected candidate regions
- Missing processed values
- Annual price-observation counts
- Price-statistic relationships
- Expected annual average prices
- Source metadata
- Regional identifier uniqueness
- Baseline cost recalculation
- Baseline emissions recalculation

Test result:

21 passed

## Findings

The deterministic calculations produced the expected values for every
tested valid scenario.

The program rejected invalid numerical and structural inputs rather
than producing misleading recommendations.

The annual ERCOT datasets contained 8,760 observations for each
selected load zone.

## Current limitations

- ERCOT day-ahead prices are wholesale-market proxies.
- The cost estimate is not a complete delivered electricity bill.
- The EPA emissions factor is an ERCT-wide annual average.
- The current model cannot distinguish the three regions by carbon
  intensity.
- Climate data has been mapped but not yet incorporated into the
  calculations.
- Reliability, transmission, interconnection, land, and scalability
  are not yet quantified.
- The application does not yet compare alternative power portfolios.
- The application is an early-stage screening tool rather than an
  engineering model.

## Validation conclusion

The Week 1 analytical prototype is suitable for demonstrating
reproducible regional energy-cost and emissions screening.

It is not yet suitable for final data-center site selection,
engineering design, utility contracting, or investment decisions.