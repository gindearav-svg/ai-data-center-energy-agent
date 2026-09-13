from typing import Any, Literal

from pydantic import BaseModel, Field


ScenarioName = Literal[
    "cost_focused",
    "balanced",
    "carbon_focused",
]


class RootResponse(BaseModel):
    name: str
    version: str
    documentation: str


class HealthResponse(BaseModel):
    status: str


class RegionsResponse(BaseModel):
    count: int
    regions: list[str]


class ElectricityPriceResponse(BaseModel):
    region: str
    price_year: int
    average_price_usd_per_mwh: float
    median_price_usd_per_mwh: float
    minimum_price_usd_per_mwh: float
    maximum_price_usd_per_mwh: float
    p95_price_usd_per_mwh: float
    p99_price_usd_per_mwh: float
    price_observations: int


class RegionEnergyProfileResponse(BaseModel):
    region: str
    ercot_settlement_point: str
    egrid_subregion: str
    noaa_station_id: str
    noaa_station_name: str
    price_year: int
    emissions_year: int
    annual_average_dam_price_usd_per_mwh: float
    annual_median_dam_price_usd_per_mwh: float
    minimum_dam_price_usd_per_mwh: float
    maximum_dam_price_usd_per_mwh: float
    price_observations: int
    grid_emissions_kg_co2e_per_mwh: float
    price_standard_deviation_usd_per_mwh: float
    p95_price_usd_per_mwh: float
    p99_price_usd_per_mwh: float
    negative_price_hours: int
    high_price_hours_above_100: int
    extreme_price_hours_above_500: int


class RecommendationRequest(BaseModel):
    it_load_mw: float = Field(
        gt=0,
        description="IT equipment load in megawatts.",
        examples=[200],
    )

    pue: float = Field(
        ge=1,
        description="Power Usage Effectiveness.",
        examples=[1.25],
    )

    utilization: float = Field(
        gt=0,
        le=1,
        description="Average utilization expressed as a decimal.",
        examples=[0.95],
    )

    scenario: ScenarioName = Field(
        default="balanced",
        description="Stakeholder preference scenario.",
    )


class RequirementsResponse(BaseModel):
    it_load_mw: float
    pue: float
    utilization: float


class WeightsResponse(BaseModel):
    cost: float
    carbon: float
    price_risk: float


class RecommendationSummaryResponse(BaseModel):
    region: str
    overall_score: float


class RegionalRecommendationResult(BaseModel):
    rank: int
    region: str
    estimated_annual_wholesale_cost_usd: float
    estimated_annual_emissions_metric_tons_co2e: float
    cost_score: float
    carbon_score: float
    price_risk_score: float
    overall_score: float


class RecommendationResponse(BaseModel):
    requirements: RequirementsResponse
    scenario: ScenarioName
    weights: WeightsResponse
    recommendation: RecommendationSummaryResponse
    regional_results: list[RegionalRecommendationResult]


class AgentQueryRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000,
        description="Natural-language data-center comparison request.",
        examples=[
            (
                "Compare Texas regions for a 200 MW IT load, "
                "1.25 PUE, and 95% utilization."
            )
        ],
    )


class AgentQueryResponse(BaseModel):
    answer: str
    answer_source: Literal[
        "llm",
        "deterministic_fallback",
    ]
    grounded: bool
    grounding_checks: dict[str, bool]
    grounded_summary: dict[str, Any]
    tool_trace: list[dict[str, Any]]