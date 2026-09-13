from pathlib import Path

from fastapi import FastAPI, HTTPException


from src.energy_agent.schemas import (
    AgentQueryRequest,
    AgentQueryResponse,
    ElectricityPriceResponse,
    HealthResponse,
    RecommendationRequest,
    RecommendationResponse,
    RegionEnergyProfileResponse,
    RegionsResponse,
    RootResponse,
)
from src.energy_agent.tools import (
    compare_energy_options,
    get_available_regions,
    get_electricity_price,
    get_region_energy_profile,
)
from src.energy_agent.agent import AgentError
from src.energy_agent.grounding import GroundingError
from src.energy_agent.service import (
    run_grounded_comparison_agent,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "energy_intelligence.db"
)


app = FastAPI(
    title="AI Data Center Energy Intelligence API",
    description=(
        "Compare Texas regions for AI data-center "
        "energy requirements."
    ),
    version="0.3.0",
)


@app.get(
    "/",
    response_model=RootResponse,
    summary="API information",
)
def root() -> dict:
    return {
        "name": "AI Data Center Energy Intelligence API",
        "version": "0.3.0",
        "documentation": "/docs",
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Check API health",
)
def health_check() -> dict:
    return {
        "status": "healthy",
    }


@app.get(
    "/regions",
    response_model=RegionsResponse,
    summary="List supported regions",
    responses={
        503: {
            "description": "Energy database is unavailable.",
        },
    },
)
def read_available_regions() -> dict:
    try:
        return get_available_regions(
            database_path=DATABASE_PATH,
        )
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error


@app.get(
    "/regions/{region}/price",
    response_model=ElectricityPriceResponse,
    summary="Get regional electricity prices",
    responses={
        404: {
            "description": "Region was not found.",
        },
        503: {
            "description": "Energy database is unavailable.",
        },
    },
)
def read_electricity_price(region: str) -> dict:
    try:
        return get_electricity_price(
            region=region,
            database_path=DATABASE_PATH,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error


@app.get(
    "/regions/{region}",
    response_model=RegionEnergyProfileResponse,
    summary="Get a regional energy profile",
    responses={
        404: {
            "description": "Region was not found.",
        },
        503: {
            "description": "Energy database is unavailable.",
        },
    },
)
def read_region_profile(region: str) -> dict:
    try:
        return get_region_energy_profile(
            region=region,
            database_path=DATABASE_PATH,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error


@app.post(
    "/recommendations",
    response_model=RecommendationResponse,
    summary="Create a regional recommendation",
    responses={
        400: {
            "description": "The analysis request is invalid.",
        },
        503: {
            "description": "Energy database is unavailable.",
        },
    },
)
def create_recommendation(
    request: RecommendationRequest,
) -> dict:
    try:
        return compare_energy_options(
            it_load_mw=request.it_load_mw,
            pue=request.pue,
            utilization=request.utilization,
            scenario=request.scenario,
            database_path=DATABASE_PATH,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error
    
@app.post(
    "/agent/query",
    response_model=AgentQueryResponse,
    summary="Run a grounded natural-language energy analysis",
    responses={
        400: {
            "description": "The agent request is invalid.",
        },
        503: {
            "description": (
                "The language model, grounding layer, "
                "or energy data is unavailable."
            ),
        },
    },
)
def query_energy_agent(
    request: AgentQueryRequest,
) -> dict:
    if not request.message.strip():
        raise HTTPException(
            status_code=422,
            detail="Message cannot be blank.",
        )

    try:
        return run_grounded_comparison_agent(
            request.message
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
    except (AgentError, GroundingError) as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error