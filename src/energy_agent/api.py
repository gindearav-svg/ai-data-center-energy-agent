from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.energy_agent.tools import (
    compare_energy_options,
    get_available_regions,
    get_electricity_price,
    get_region_energy_profile,
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
    version="0.1.0",
)


class RecommendationRequest(BaseModel):
    it_load_mw: float = Field(
        gt=0,
        description="IT equipment load in megawatts.",
    )

    pue: float = Field(
        ge=1,
        description="Power Usage Effectiveness.",
    )

    utilization: float = Field(
        gt=0,
        le=1,
        description="Average utilization expressed as a decimal.",
    )

    scenario: Literal[
        "cost_focused",
        "balanced",
        "carbon_focused",
    ] = "balanced"


@app.get("/")
def root() -> dict:
    return {
        "name": "AI Data Center Energy Intelligence API",
        "version": "0.1.0",
        "documentation": "/docs",
    }


@app.get("/health")
def health_check() -> dict:
    return {
        "status": "healthy",
    }


@app.get("/regions")
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


@app.get("/regions/{region}/price")
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


@app.get("/regions/{region}")
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


@app.post("/recommendations")
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