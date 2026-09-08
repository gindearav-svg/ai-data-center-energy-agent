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

Run the application:

```bash
python main.py
## Run the project

To create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
