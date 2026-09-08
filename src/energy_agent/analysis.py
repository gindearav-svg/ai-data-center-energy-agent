import pandas as pd

from src.energy_agent.calculations import (
    calculate_annual_cost,
    calculate_annual_emissions_metric_tons,
    calculate_annual_energy,
    calculate_facility_load,
)


REQUIRED_REGIONAL_COLUMNS = {
    "region",
    "annual_average_dam_price_usd_per_mwh",
    "grid_emissions_kg_co2e_per_mwh",
}


def compare_regions(
    regional_metrics: pd.DataFrame,
    it_load_mw: float,
    pue: float,
    utilization: float,
) -> pd.DataFrame:
    """Calculate and rank regional cost and emissions results."""

    missing_columns = (
        REQUIRED_REGIONAL_COLUMNS
        - set(regional_metrics.columns)
    )

    if missing_columns:
        raise ValueError(
            "Regional data is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    if regional_metrics.empty:
        raise ValueError("Regional data cannot be empty.")

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

    results[
        "estimated_annual_wholesale_cost_usd"
    ] = results[
        "annual_average_dam_price_usd_per_mwh"
    ].apply(
        lambda price: calculate_annual_cost(
            annual_energy_mwh=annual_energy_mwh,
            electricity_price_usd_per_mwh=price,
        )
    )

    results[
        "estimated_annual_emissions_metric_tons_co2e"
    ] = results[
        "grid_emissions_kg_co2e_per_mwh"
    ].apply(
        lambda intensity: calculate_annual_emissions_metric_tons(
            annual_energy_mwh=annual_energy_mwh,
            emissions_intensity_kg_per_mwh=intensity,
        )
    )

    return (
        results
        .sort_values(
            by=[
                "estimated_annual_wholesale_cost_usd",
                "region",
            ]
        )
        .reset_index(drop=True)
    )