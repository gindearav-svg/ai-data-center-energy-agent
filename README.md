# AI Data Center Energy Intelligence Agent

A Texas-focused decision-support application for comparing the estimated energy cost, emissions, and electricity-price risk of AI data-center locations.

Users can submit a natural-language request through a browser interface or call the FastAPI endpoints directly. Deterministic Python and SQL tools produce the numerical results; an LLM can select tools, but its unverified wording is kept separate from the published recommendation.

## Current scope

The application compares three broad Texas regions: Houston, North Texas, and West Texas. Given an IT load, Power Usage Effectiveness (PUE), utilization, and preference scenario, it:

1. Calculates facility load and annual electricity consumption.
2. Estimates annual wholesale electricity cost and operational emissions.
3. Compares relative electricity-price risk.
4. Ranks the regions using a weighted scoring model.
5. Presents the results through an API and browser interface.

This is a regional screening tool, not a parcel-level site-selection or engineering-feasibility study.

## Data and limitations

The analysis uses:

- 2025 ERCOT Day-Ahead Market load-zone electricity prices.
- A 2023 EPA eGRID ERCT emissions factor.
- User-provided IT load, PUE, and utilization.

The estimated electricity cost is a **wholesale energy-cost estimate**, not a data center's final electricity bill. It excludes items such as transmission, distribution, demand charges, taxes, hedging, and power purchase agreements.

All three regions currently share the same coarse eGRID emissions factor. Equal emissions estimates therefore **do not establish that local generation mixes are identical**.

Electricity-price risk describes relative exposure to volatile or high prices in this dataset. It does **not** measure physical grid reliability or guarantee data-center uptime. The application does not yet assess individual parcels, interconnection capacity, water availability, or cooling-system design.

## How the analysis works

Facility load equals IT load multiplied by PUE. Annual energy consumption also accounts for average utilization and 8,760 hours per year.

The application analyzes hourly electricity prices using statistics including standard deviation, 95th- and 99th-percentile prices, negative-price hours, and hours above high-price thresholds. Its composite price-risk score uses:

- Price standard deviation: 35%.
- 95th-percentile price: 35%.
- Hours above $100/MWh: 20%.
- Hours above $500/MWh: 10%.

Scores are relative to the candidate regions: **higher price-risk scores mean better relative price stability**, not zero volatility.

### Preference scenarios

| Scenario | Cost | Carbon | Price risk |
| --- | ---: | ---: | ---: |
| Cost-focused | 85% | 5% | 10% |
| Balanced | 50% | 20% | 30% |
| Carbon-focused | 30% | 60% | 10% |

The selected weights determine the overall ranking. Because the current emissions factor is shared across the three regions, the carbon-focused scenario cannot meaningfully distinguish their local emissions.

## Set up the project locally

From the project directory, create and activate a virtual environment, then install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The processed regional metrics CSV and SQL schema are tracked in Git. Build the local SQLite database before starting the API:

```bash
python -m scripts.build_database
```

This reads `data/processed/regional_metrics.csv`, applies `database/schema.sql`, and creates `data/processed/energy_intelligence.db`. The SQLite database itself is not committed to Git.

Run the automated tests:

```bash
python -m pytest
```

Automated tests use simulated LLM clients where needed; they do not require Ollama to be running.

## Run the API and browser interface

Start the FastAPI server:

```bash
python -m uvicorn src.energy_agent.api:app --reload
```

With the server running, open:

- Browser interface: [http://127.0.0.1:8000/app](http://127.0.0.1:8000/app)
- Interactive API documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

The deterministic recommendation endpoint does not require an LLM. For example:

```bash
curl -X POST http://127.0.0.1:8000/recommendations \
  -H "Content-Type: application/json" \
  -d '{"it_load_mw":200,"pue":1.25,"utilization":0.95,"scenario":"balanced"}'
```

The natural-language `/agent/query` endpoint and the browser's agent request require access to the configured LLM.

### API endpoints

- `GET /health` — check API health.
- `GET /regions` — list supported regions.
- `GET /regions/{region}` — retrieve a regional energy profile.
- `GET /regions/{region}/price` — retrieve electricity-price statistics.
- `POST /recommendations` — run a deterministic regional comparison.
- `POST /agent/query` — interpret a natural-language request and return a tool-grounded answer.

Request and response models are defined with Pydantic and documented in the generated OpenAPI specification at `/docs`.

## Local LLM configuration

Local development uses Ollama through an OpenAI-compatible Python client. To use the `qwen3:8b` model, install and start Ollama, then run:

```bash
ollama pull qwen3:8b
export LLM_MODEL=qwen3:8b
```

The `export` applies to the current Terminal session. Set it again in a new Terminal session unless you configure it persistently. The LLM client also accepts `LLM_BASE_URL` and `LLM_API_KEY` environment variables for a compatible hosted provider.

To check the model selected by the application:

```bash
python -c "from src.energy_agent.llm_client import load_llm_settings; print(load_llm_settings().model)"
```

Run the command-line demonstrations:

```bash
python -m scripts.demo_llm
python -m scripts.demo_agent
```

Local Ollama runs on your computer. A publicly deployed version would need its own accessible LLM service; changing the client configuration alone does not make your Mac-hosted model publicly available.

## Grounded agent responses

The LLM interprets natural-language requests and can select approved energy-analysis tools. Python executes those tools; the LLM does not receive direct SQLite access.

For regional comparisons, the API's published `answer` is assembled from structured tool results. `answer_source: "tool_summary"` identifies that published answer, and `grounded: true` refers to the published tool-built response.

The separate `model_draft` field contains the LLM's original wording for inspection and is **not fully verified**. `grounding_checks` are basic presence checks on that draft; they do not certify every statement it makes. A check can be `false` while the separately assembled published answer remains grounded.

The browser interface displays decision figures and rationale from structured results. It labels the original model wording as unverified.

## Other command-line workflows

Run a custom recommendation:

```bash
python -m scripts.recommend_sites \
  --it-load-mw 200 \
  --pue 1.25 \
  --utilization 0.95 \
  --scenario balanced
```

Query the SQLite database:

```bash
python -m scripts.query_database --list-regions
python -m scripts.query_database --region "Houston"
python -m scripts.query_database --compare-all
```

Rebuild the database from the processed CSV:

```bash
python -m scripts.build_database
```

Regenerate the complete analytical pipeline:

```bash
python -m scripts.run_full_pipeline
```

The full pipeline may require the original source datasets. See `docs/data_sources.md` for source-data information; a fresh clone can build the API's database directly from the tracked processed CSV without rerunning the full pipeline.

## Data quality and project structure

Automated validation checks required values, region identifiers, hourly price-observation counts, price-percentile ordering, and nonnegative volatility and emissions values. Invalid inputs should fail before reaching downstream recommendations.

Key project locations:

- `src/energy_agent/` — analysis, database access, tools, agent, grounding, and API code.
- `scripts/` — pipeline, database-build, query, and demonstration commands.
- `data/processed/regional_metrics.csv` — tracked processed regional data.
- `database/schema.sql` — tracked SQLite schema.
- `tests/` — automated tests.
- `web/` — browser interface.
- `docs/` — supporting project and data-source documentation.