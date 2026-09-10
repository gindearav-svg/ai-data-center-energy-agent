# AI Data Center Energy Info Agent

A decision-support application for evaluating where and how to power
AI data centers.

## Project objective

The application will compare various data-center regions and power
strategies based on -- 

- Electricity cost
- Regional grid reliability/availability
- Carbon intensity
- Cooling conditions
- Scalability

The final system will combine structured energy data, deterministic
Python calculations, SQL, document retrieval, LLM tool calling, and
a transparent site-scoring model.

## Initial scope        

Version 1 will focus on Texas and the ERCOT electricity market.

The first version will:

1. Estimate facility power from IT load and PUE.
2. Estimate annual electricity consumption.
3. Compare three candidate Texas regions.
4. Estimate annual electricity cost and operational emissions.
5. Rank regions using a transparent scoring model.

## Current functionality

The Week 1 calculator accepts:

- IT load in MW
- Expected PUE
- Expected average utilization

It returns:

- Total facility load in MW
- Annual electricity consumption in MWh
- Annual electricity consumption in TWh

## Regional comparison

The interactive command-line application compares North Texas,
Houston, and West Texas using:

- 2025 ERCOT Day-Ahead Market load-zone prices
- 2023 EPA eGRID ERCT emissions intensity
- User-provided IT load
- User-provided PUE
- User-provided average utilization


## Current limitations

- Wholesale day-ahead market prices are not the same as the final electricity
  price paid by a data center. The current results exclude transmission,
  distribution, demand charges, taxes, hedging, and power purchase agreements.
- All three candidate regions currently use the same EPA eGRID ERCT emissions
  factor. Therefore, the baseline model does not yet capture hourly or
  location-specific differences in grid carbon intensity.
- The model currently compares broad Texas regions rather than individual
  parcels, substations, utilities, or transmission interconnection points.
- Reliability, water availability, cooling demand, and transmission capacity
  will be added in later development stages.

## Initial regional scoring model

The first scoring model ranks candidate regions using three measurable
components:

- Annual wholesale electricity cost: 70%
- Annual grid emissions: 20%
- Maximum observed day-ahead electricity price: 10%

Each metric is normalized to a score from 0 to 100, where a higher score is
better. The weighted component scores produce the overall regional score.

The maximum electricity price is currently used only as a preliminary indicator
of exposure to extreme price events. It is not a complete measurement of grid
reliability.

Because all three regions currently use the same EPA eGRID ERCT emissions
factor, their carbon scores are equal. More granular carbon data will be added
in a later version.


### Preference scenarios

The model supports multiple decision-maker preference profiles:

| Scenario | Cost | Carbon | Price risk |
|---|---:|---:|---:|
| Cost-focused | 85% | 5% | 10% |
| Balanced | 50% | 20% | 30% |
| Carbon-focused | 30% | 60% | 10% |

Each scenario independently recalculates the overall scores and regional
rankings. This allows the analysis to show whether a recommendation is robust
or sensitive to the user's priorities.

The current carbon-focused results are limited because all candidate regions
use the same annual EPA eGRID emissions factor. More granular carbon data is
required before the carbon-focused scenario can meaningfully distinguish the
three regions.


## Running a custom recommendation

The command-line interface accepts user-defined data-center requirements and
a decision preference scenario.

Example:

```bash
python -m scripts.recommend_sites \
  --it-load-mw 200 \
  --pue 1.25 \
  --utilization 0.95 \
  --scenario balanced

### Electricity price-risk metrics

The project analyzes all hourly ERCOT day-ahead prices for each candidate
load zone rather than relying only on annual averages. The risk analysis
calculates:

- Price standard deviation
- 95th-percentile price
- 99th-percentile price
- Number of negative-price hours
- Number of hours above $100/MWh
- Number of extreme hours above $500/MWh

These statistics measure electricity-price volatility and exposure to
high-price events. They should not be interpreted as complete measures of
physical grid reliability or data-center uptime.



### Composite price-risk score

Price risk is evaluated using multiple statistics calculated from 8,760
hourly ERCOT day-ahead prices:

- Price standard deviation: 35%
- 95th-percentile price: 35%
- Hours above $100/MWh: 20%
- Hours above $500/MWh: 10%

Each component is normalized across the candidate regions, where higher
scores indicate lower price risk. The weighted components produce a
composite price-risk score from 0 to 100.

Negative-price hours and 99th-percentile prices are retained for analysis,
but they are not currently included in the composite score. Negative prices
can represent economic opportunity as well as congestion or market
imbalance, so they should not automatically be treated as beneficial or
harmful.

### Automated data-quality validation

Before regional data is used by the recommendation model, automated checks
verify:

- Required columns and values are present
- Region and settlement-point identifiers are unique
- Each region contains exactly 8,760 hourly price observations
- Price percentiles are logically ordered
- Volatility and emissions values are nonnegative
- Price-event counts do not exceed total observations

The validation process produces a machine-readable JSON quality report.
Invalid data raises an error before it can affect downstream recommendations.

Run the application:

```bash
python main.py
## Run the project

To create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
