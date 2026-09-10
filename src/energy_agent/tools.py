import json
from pathlib import Path

from src.energy_agent.calculations import (
    calculate_annual_energy,
    calculate_facility_load,
)
from src.energy_agent.queries import (
    compare_all_regions,
    get_region_metrics,
    list_regions,
)
from src.energy_agent.recommendation import (
    build_regional_recommendation,
)
from src.energy_agent.scenarios import SCORING_SCENARIOS


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "energy_intelligence.db"
)


def get_available_regions(
    database_path: Path = DEFAULT_DATABASE_PATH,
) -> dict:
    """Return the regions currently available for analysis."""
    regions = list_regions(database_path)

    return {
        "count": len(regions),
        "regions": regions,
    }


def get_electricity_price(
    region: str,
    database_path: Path = DEFAULT_DATABASE_PATH,
) -> dict:
    """Return annual electricity-price metrics for one region."""
    profile = get_region_metrics(
        database_path=database_path,
        region_name=region,
    )

    return {
        "region": profile["region"],
        "price_year": profile["price_year"],
        "average_price_usd_per_mwh": profile[
            "annual_average_dam_price_usd_per_mwh"
        ],
        "median_price_usd_per_mwh": profile[
            "annual_median_dam_price_usd_per_mwh"
        ],
        "minimum_price_usd_per_mwh": profile[
            "minimum_dam_price_usd_per_mwh"
        ],
        "maximum_price_usd_per_mwh": profile[
            "maximum_dam_price_usd_per_mwh"
        ],
        "p95_price_usd_per_mwh": profile[
            "p95_price_usd_per_mwh"
        ],
        "p99_price_usd_per_mwh": profile[
            "p99_price_usd_per_mwh"
        ],
        "price_observations": profile["price_observations"],
    }


def get_region_energy_profile(
    region: str,
    database_path: Path = DEFAULT_DATABASE_PATH,
) -> dict:
    """Return all stored energy metrics for one region."""
    return get_region_metrics(
        database_path=database_path,
        region_name=region,
    )


def estimate_power_requirement(
    it_load_mw: float,
    pue: float,
    utilization: float,
) -> dict:
    """Estimate facility load and annual energy consumption."""
    facility_load_mw = calculate_facility_load(
        it_load_mw=it_load_mw,
        pue=pue,
    )

    annual_energy_mwh = calculate_annual_energy(
        facility_load_mw=facility_load_mw,
        utilization=utilization,
    )

    return {
        "it_load_mw": it_load_mw,
        "pue": pue,
        "utilization": utilization,
        "facility_load_mw": facility_load_mw,
        "annual_energy_mwh": annual_energy_mwh,
    }


def compare_energy_options(
    it_load_mw: float,
    pue: float,
    utilization: float,
    scenario: str,
    database_path: Path = DEFAULT_DATABASE_PATH,
) -> dict:
    """
    Rank all stored regions for a user-defined data-center scenario.
    """
    if scenario not in SCORING_SCENARIOS:
        available_scenarios = sorted(SCORING_SCENARIOS)

        raise ValueError(
            f"Unknown scenario: {scenario}. "
            f"Available scenarios: {available_scenarios}"
        )

    regional_metrics = compare_all_regions(database_path)
    weights = SCORING_SCENARIOS[scenario]

    results = build_regional_recommendation(
        regional_metrics=regional_metrics,
        it_load_mw=it_load_mw,
        pue=pue,
        utilization=utilization,
        weights=weights,
    )

    result_columns = [
        "rank",
        "region",
        "estimated_annual_wholesale_cost_usd",
        "estimated_annual_emissions_metric_tons_co2e",
        "cost_score",
        "carbon_score",
        "price_risk_score",
        "overall_score",
    ]

    # Convert through JSON to guarantee ordinary JSON-compatible types.
    regional_results = json.loads(
        results[result_columns].to_json(
            orient="records"
        )
    )

    winner = regional_results[0]

    return {
        "requirements": {
            "it_load_mw": it_load_mw,
            "pue": pue,
            "utilization": utilization,
        },
        "scenario": scenario,
        "weights": weights,
        "recommendation": {
            "region": winner["region"],
            "overall_score": winner["overall_score"],
        },
        "regional_results": regional_results,
    }