# Product Requirements Document

## 1. Product name

AI Data Center Energy Intelligence Agent

## 2. Product summary

The AI Data Center Energy Intelligence Agent is an early-stage
decision-support application that helps users compare potential
Texas regions and power strategies for an AI data center.

The app combines energy data, deterministic
calculations, document retrieval, and LLM tool calling to produce
transparent, source-grounded recommendations.

The model will explain and coordinate the analysis. It will
not independently invent electricity prices, emissions factors,
energy requirements, or site scores.

## 3. Target user

The initial target user is a data center strategy or development
analyst conducting an early-stage screening of potential Texas
locations.

The user needs to compare regions before commissioning detailed
engineering, utility interconnection, environmental, land, and
financial studies.

## 4. User problem

Selecting a data center location requires comparing information from
many different sources, including:

- Electricity prices
- Generation mix
- Grid emissions
- Climate and cooling conditions
- Grid constraints
- Reliability considerations
- Potential power technologies
- Future expansion potential

This information is fragmented across datasets, reports, and utility
or grid-operator documents. The user needs a faster way to organize
the available evidence, perform consistent calculations, and
understand the tradeoffs between candidate regions.

## 5. Primary user story

As a data center strategy analyst, I want to enter the power,
reliability, cost, and sustainability requirements for a proposed
AI data center so that I can compare candidate Texas regions and
power strategies using transparent calculations and cited evidence.

## 6. Example scenario

A user enters:

> I need a 200 MW IT-load data center in Texas with 99.99% target
> uptime, 1.25 PUE, 95% average utilization, and a preference for
> lower-carbon power.

The application estimates the facility's energy requirements,
compares candidate regions, evaluates potential power strategies,
and explains the most important tradeoffs.

## 7. Initial geographic scope

Version 1 will examine three candidate Texas regions:

1. North Texas, represented by the Dallas–Fort Worth area
2. Houston region
3. West Texas

These regions are screening areas rather than specific construction
sites. Each region may use a documented electricity-market,
utility, weather, or emissions proxy depending on available data.

Every proxy must include:

- Geographic definition
- Measurement unit
- Data year
- Source
- Explanation of why the proxy is appropriate

## 8. User inputs

### Required inputs

- IT load in megawatts
- Expected Power Usage Effectiveness
- Expected average utilization percentage
- Target uptime percentage
- Cost priority
- Carbon priority
- Preferred Texas region, if any

### Optional future inputs

- Target operating year
- Expected future load growth
- Maximum electricity price
- Preferred generation technologies
- On-site generation preference
- Renewable-energy target
- Water-use preference
- Maximum acceptable emissions
- Available land area

## 9. Application outputs

### Week 1 outputs

- Total facility load in MW
- Annual electricity consumption in MWh
- Annual electricity consumption in TWh
- Estimated annual electricity cost
- Estimated annual operational emissions
- Comparison of three Texas regions

### Final MVP outputs

- Ranked candidate regions
- Comparison of power strategies
- Electricity-price findings
- Generation-mix findings
- Grid-carbon-intensity findings
- Cooling and climate considerations
- Grid and transmission constraints
- Quantitative score breakdown
- Key assumptions
- Risks and uncertainties
- Source citations
- Final recommendation
- Alternative recommendation

## 10. Initial calculations

### Facility load

Facility Load = IT Load × PUE

### Annual electricity consumption

Annual Electricity Consumption =
Facility Load × 8,760 Hours × Utilization

### Annual electricity cost

Annual Electricity Cost =
Annual Electricity Consumption × Electricity Price

### Annual operational emissions

Annual Operational Emissions =
Annual Electricity Consumption × Grid Emissions Intensity

All calculations must use consistent units and reject impossible or
invalid inputs.

## 11. Site-selection factors

The final quantitative model will consider:

- Electricity cost
- Grid reliability
- Carbon intensity
- Cooling conditions
- Grid availability
- Scalability

Each factor will receive a normalized score. The application will
combine these scores using user-adjustable weights.

The application must display each component score rather than only
showing a final ranking.

## 12. Power strategies

The initial application may compare:

1. Grid electricity with backup generation
2. Grid electricity with a renewable power purchase agreement
3. Grid electricity combined with solar and battery storage
4. Grid electricity combined with a nuclear power agreement

The final selection of strategies will depend on data availability
and model feasibility.

NREL REopt may later be used to evaluate combinations of renewable
generation, storage, conventional generation, cost, emissions, and
resilience.

## 13. Functional requirements

### FR-1: Accept data center requirements

The system must accept numerical data center load, PUE, and
utilization inputs.

### FR-2: Validate inputs

The system must reject negative loads, PUE values below 1.0, and
utilization percentages outside the valid range.

### FR-3: Calculate energy requirements

The system must calculate facility load and annual electricity
consumption using deterministic Python functions.

### FR-4: Retrieve regional data

The system must retrieve regional values from a structured data
source rather than ask the language model to generate them.

### FR-5: Compare candidate regions

The system must compare candidate regions using the same calculation
methodology.

### FR-6: Preserve source information

Every externally obtained value must retain its source, date,
geographic scope, and measurement unit.

### FR-7: Explain recommendations

The system must explain why one region or power strategy ranks above
another.

### FR-8: Show uncertainty

The system must identify missing data, proxies, assumptions, and
limitations that could affect the recommendation.

## 14. Non-functional requirements

- Calculations must be reproducible.
- Identical numerical inputs must produce identical calculations.
- The application must clearly distinguish sourced facts from model
  interpretations.
- Invalid inputs must produce understandable error messages.
- Important calculations must have automated tests.
- The application must not expose API keys or credentials.
- A user should be able to understand the result without reading the
  source code.

## 15. Data principles

The project will follow these rules:

1. Do not use numbers generated by an LLM as source data.
2. Prefer government, grid-operator, utility, and peer-reviewed
   sources.
3. Record the year and unit of every value.
4. Do not compare values covering incompatible time periods without
   disclosing the difference.
5. Document all geographic and methodological proxies.
6. Preserve raw data separately from cleaned data.
7. Perform calculations in Python rather than inside the LLM.
8. Clearly label estimates and assumptions.

## 16. Out of scope

Version 1 will not:

- Select a specific parcel of land
- Guarantee grid interconnection
- Guarantee 99.99% operational uptime
- Replace an engineering study
- Replace utility or transmission studies
- Estimate a complete construction budget
- Provide investment or legal advice
- Cover every United States electricity market
- Produce real-time grid-operating recommendations
- Claim that a project is construction-ready
- Make autonomous infrastructure decisions

## 17. Reliability limitation

A user's uptime target is a facility requirement, not something the
application can guarantee from public regional data alone.

For example, 99.99% uptime permits approximately 52.6 minutes of
downtime per standard year. Achieving this target depends on facility
design, redundancy, backup power, maintenance, fuel availability,
grid service, and other operational factors.

The application will treat reliability as a screening consideration
and clearly identify where detailed engineering analysis is required.

## 18. MVP success criteria

The first usable version will be successful when it can:

1. Accept a valid data center scenario.
2. Calculate facility load and annual electricity consumption
   correctly.
3. Compare three Texas regions.
4. Estimate annual electricity cost and operational emissions.
5. Display the source and year for every regional input.
6. Rank regions using a transparent scoring methodology.
7. Explain the major tradeoffs without inventing unsupported numbers.
8. Pass automated numerical tests.
9. Produce the same quantitative results for identical inputs.
10. Run from documented setup instructions.

## 19. Final project success criteria

The final project will be successful when it includes:

- A deployed user interface
- A Python API
- A SQL database
- Reproducible data-ingestion pipelines
- LLM tool calling
- Document retrieval with citations
- A transparent quantitative model
- Thirty to fifty benchmark scenarios
- Numerical-accuracy evaluation
- Citation-correctness evaluation
- Hallucination evaluation
- Recommendation-consistency evaluation
- Feedback from five to ten test users

## 20. Known risks

- Public data may not match the exact geographic boundaries needed.
- Historical electricity prices may not represent a future contract.
- Grid carbon intensity changes over time.
- Public information may not reveal actual interconnection capacity.
- Cooling estimates may require simplified climate proxies.
- LLM explanations may overstate what the underlying evidence proves.
- A 200 MW project may require site-specific infrastructure that
  cannot be modeled using public regional data alone.

## 21. Current project status

Completed:

- Created the project repository
- Configured the Python environment
- Implemented facility-load calculation
- Implemented annual-energy calculation
- Added input validation
- Added automated calculation tests
- Published the repository on GitHub

Next:

- Identify authoritative data sources
- Collect initial data for the three candidate regions
- Add cost and emissions calculations
- Build the first regional comparison