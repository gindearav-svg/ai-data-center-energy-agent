import pandas as pd

from src.energy_agent.calculations import (
    calculate_annual_energy,
    calculate_facility_load,
)
from src.energy_agent.scoring import score_regions


REQUIRED_REGIONAL_COLUMNS = {
    "region",
    "annual_average_dam_price_usd_per_mwh",
    "maximum_dam_price_usd_per_mwh",
    "grid_emissions_kg_co2e_per_mwh",
}


def build_regional_recommendation(
    regional_metrics: pd.DataFrame,
    it_load_mw: float,
    pue: float,
    utilization: float,
    weights: dict[str, float],
) -> pd.DataFrame:
    """
    Calculate energy, cost, emissions, scores, and rankings for a
    user-defined data-center scenario.
    """
    missing_columns = (
        REQUIRED_REGIONAL_COLUMNS - set(regional_metrics.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Regional data is missing columns: {sorted(missing_columns)}"
        )

    facility_load_mw = calculate_facility_load(
        it_load_mw=it_load_mw,
        pue=pue,
    )

    annual_energy_mwh = calculate_annual_energy(
        facility_load_mw=facility_load_mw,
        utilization=utilization,
    )

    results = regional_metrics.copy()

    results["it_load_mw"] = it_load_mw
    results["pue"] = pue
    results["utilization"] = utilization
    results["facility_load_mw"] = facility_load_mw
    results["annual_energy_mwh"] = annual_energy_mwh

    results["estimated_annual_wholesale_cost_usd"] = (
        results["annual_energy_mwh"]
        * results["annual_average_dam_price_usd_per_mwh"]
    )

    results["estimated_annual_emissions_metric_tons_co2e"] = (
        results["annual_energy_mwh"]
        * results["grid_emissions_kg_co2e_per_mwh"] 
        / 1000

    )

    return score_regions(
        regional_data=results,
        weights=weights,
    )