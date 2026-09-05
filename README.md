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

## Run the project

To create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate