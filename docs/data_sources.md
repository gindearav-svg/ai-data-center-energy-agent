# Data Source Inventory

## Purpose

This document records the source, geography, year, unit, intended use,
and limitations of each dataset used by the AI Data Center Energy
Intelligence Agent.

No external numerical value should enter the analytical model without
this information.

## 1. ERCOT Day-Ahead Market Prices

- Provider: Electric Reliability Council of Texas
- Dataset: Historical DAM Load Zone and Hub Prices
- Data year: 2025
- Market: Day-Ahead Market
- Unit: USD per MWh
- Geographic level: ERCOT load zone
- Project metric: Wholesale electricity-price proxy
- Source:
  https://www.ercot.com/mp/data-products/data-product-details?id=NP4-180-ER

### Project mappings

| Project region | ERCOT settlement point |
|---|---|
| North Texas | LZ_NORTH |
| Houston | LZ_HOUSTON |
| West Texas | LZ_WEST |

### Planned transformation

The project will filter the 2025 dataset to the three selected load
zones and calculate an annual time-average day-ahead settlement price
for each zone.

### Limitations

The settlement-point price is a wholesale-market proxy. It is not the
complete delivered electricity price paid by a data center.

It does not necessarily include transmission, distribution, demand
charges, retail margins, taxes, fees, power-purchase agreement terms,
or other contractual costs.

Historical prices do not guarantee future electricity costs.

## 2. EPA eGRID Emissions

- Provider: United States Environmental Protection Agency
- Dataset: eGRID 2023
- Data year: 2023
- Subregion: ERCT
- Original unit: lb CO2e per MWh
- Project unit: kg CO2e per MWh
- Geographic level: eGRID subregion
- Source: https://www.epa.gov/egrid/summary-data

### Source value

ERCT total output emission rate:

736.629 lb CO2e/MWh

### Unit conversion

1 lb = 0.45359237 kg

736.629 × 0.45359237 =
334.129 kg CO2e/MWh

### Project value

334.129 kg CO2e/MWh

### Limitations

The ERCT value represents the eGRID subregion average. It does not
provide distinct grid-emissions rates for North Texas, Houston, and
West Texas.

The same grid-average factor will initially be assigned to all three
regions. The application must not imply that this value represents a
specific utility contract, generator, or hourly marginal emission
rate.

## 3. NOAA Climate Normals

- Provider: National Oceanic and Atmospheric Administration
- Dataset: U.S. Climate Normals
- Normal period: 1991–2020
- Variable: Annual cooling degree days
- Base temperature: 65 degrees Fahrenheit
- Geographic level: Representative weather station
- Source:
  https://www.ncei.noaa.gov/products/land-based-station/us-climate-normals

### Project mappings

| Project region | Representative station | Station ID |
|---|---|---|
| North Texas | Dallas Fort Worth International Airport | USW00003927 |
| Houston | Houston Intercontinental Airport | USW00012960 |
| West Texas | Midland International Airport | USW00023023 |

### Intended use

Annual cooling degree days will serve as a simplified screening proxy
for climate-related cooling burden.

### Limitations

Cooling degree days do not directly determine data center PUE,
cooling-system efficiency, electricity consumption, or water use.

A specific facility's cooling performance depends on equipment,
cooling architecture, humidity, design temperatures, water
availability, operating practices, and other site-specific factors.

## Data-quality rules

1. Every value must retain its source and data year.
2. Every value must use an explicitly documented unit.
3. Raw source data must remain separate from processed data.
4. Missing values must not be replaced with LLM-generated estimates.
5. Proxies must be clearly labeled in the user interface.
6. Data covering different years must not be presented as though it
   came from one common observation period.
7. The application must distinguish wholesale price proxies from
   delivered customer electricity costs.
8. Calculations must be performed in Python rather than by the LLM.