from pathlib import Path

import pandas as pd

from src.energy_agent.calculations import (
    calculate_annual_cost,
    calculate_annual_emissions_metric_tons,
    calculate_annual_energy,
    calculate_facility_load,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REGIONAL_METRICS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "regional_metrics.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "baseline_regional_results.csv"
)


def main() -> None:
    """Calculate regional results for the baseline data center."""

    it_load_mw = 200
    pue = 1.25
    utilization = 0.95

    facility_load_mw = calculate_facility_load(
        it_load_mw=it_load_mw,
        pue=pue,
    )

    annual_energy_mwh = calculate_annual_energy(
        facility_load_mw=facility_load_mw,
        utilization=utilization,
    )

    regional_metrics = pd.read_csv(REGIONAL_METRICS_FILE)

    regional_metrics["it_load_mw"] = it_load_mw
    regional_metrics["pue"] = pue
    regional_metrics["utilization"] = utilization
    regional_metrics["facility_load_mw"] = facility_load_mw
    regional_metrics["annual_energy_mwh"] = annual_energy_mwh

    regional_metrics[
        "estimated_annual_wholesale_cost_usd"
    ] = regional_metrics[
        "annual_average_dam_price_usd_per_mwh"
    ].apply(
        lambda price: calculate_annual_cost(
            annual_energy_mwh=annual_energy_mwh,
            electricity_price_usd_per_mwh=price,
        )
    )

    regional_metrics[
        "estimated_annual_emissions_metric_tons_co2e"
    ] = regional_metrics[
        "grid_emissions_kg_co2e_per_mwh"
    ].apply(
        lambda intensity: calculate_annual_emissions_metric_tons(
            annual_energy_mwh=annual_energy_mwh,
            emissions_intensity_kg_per_mwh=intensity,
        )
    )

    regional_metrics.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    display = regional_metrics[
        [
            "region",
            "annual_average_dam_price_usd_per_mwh",
            "estimated_annual_wholesale_cost_usd",
            "estimated_annual_emissions_metric_tons_co2e",
        ]
    ].copy()

    display[
        "estimated_annual_wholesale_cost_usd"
    ] = display[
        "estimated_annual_wholesale_cost_usd"
    ].round(0)

    display[
        "estimated_annual_emissions_metric_tons_co2e"
    ] = display[
        "estimated_annual_emissions_metric_tons_co2e"
    ].round(1)

    print("Baseline Data Center")
    print("--------------------")
    print(f"IT load: {it_load_mw} MW")
    print(f"PUE: {pue}")
    print(f"Utilization: {utilization:.0%}")
    print(f"Facility load: {facility_load_mw:,.1f} MW")
    print(f"Annual energy: {annual_energy_mwh:,.0f} MWh")

    print("\nRegional Results")
    print("----------------")

    print(display.to_string(index=False))

    print(f"\nSaved results to:\n{OUTPUT_FILE}")


if __name__ == "__main__":
    main()