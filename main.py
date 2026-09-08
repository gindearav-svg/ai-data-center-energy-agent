from pathlib import Path

import pandas as pd

from src.energy_agent.analysis import compare_regions
from src.energy_agent.calculations import (
    calculate_annual_energy,
    calculate_facility_load,
)


PROJECT_ROOT = Path(__file__).resolve().parent

REGIONAL_METRICS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "regional_metrics.csv"
)


def get_user_inputs() -> tuple[float, float, float]:
    """Collect the data center requirements from the user."""

    it_load_mw = float(
        input("Enter IT load in MW: ")
    )

    pue = float(
        input("Enter expected PUE: ")
    )

    utilization_percent = float(
        input("Enter expected average utilization (%): ")
    )

    utilization = utilization_percent / 100

    return it_load_mw, pue, utilization


def display_results(
    results: pd.DataFrame,
    facility_load_mw: float,
    annual_energy_mwh: float,
) -> None:
    """Display the regional comparison in the terminal."""

    print("\nEstimated Data Center Requirements")
    print("----------------------------------")
    print(f"Facility load: {facility_load_mw:,.2f} MW")
    print(f"Annual energy: {annual_energy_mwh:,.0f} MWh")
    print(
        "Annual energy: "
        f"{annual_energy_mwh / 1_000_000:,.3f} TWh"
    )

    display = results[
        [
            "region",
            "annual_average_dam_price_usd_per_mwh",
            "estimated_annual_wholesale_cost_usd",
            "estimated_annual_emissions_metric_tons_co2e",
        ]
    ].copy()

    display.columns = [
        "Region",
        "Average DAM Price",
        "Annual Wholesale Cost",
        "Annual Emissions",
    ]

    display["Average DAM Price"] = display[
        "Average DAM Price"
    ].map(
        lambda value: f"${value:,.2f}/MWh"
    )

    display["Annual Wholesale Cost"] = display[
        "Annual Wholesale Cost"
    ].map(
        lambda value: f"${value:,.0f}"
    )

    display["Annual Emissions"] = display[
        "Annual Emissions"
    ].map(
        lambda value: f"{value:,.1f} metric tons CO2e"
    )

    print("\nRegional Comparison")
    print("-------------------")
    print(display.to_string(index=False))

    lowest_cost_region = results.iloc[0]

    print("\nCurrent Findings")
    print("----------------")
    print(
        "Lowest estimated wholesale energy cost: "
        f"{lowest_cost_region['region']} "
        f"(${lowest_cost_region['estimated_annual_wholesale_cost_usd']:,.0f}/year)"
    )

    unique_emissions_rates = results[
        "grid_emissions_kg_co2e_per_mwh"
    ].nunique()

    if unique_emissions_rates == 1:
        print(
            "Lowest-carbon region: No distinction can currently "
            "be made because all regions use the same EPA "
            "ERCT-wide grid emissions factor."
        )
    else:
        lowest_emissions_region = results.loc[
            results[
                "estimated_annual_emissions_metric_tons_co2e"
            ].idxmin()
        ]

        print(
            "Lowest estimated operational emissions: "
            f"{lowest_emissions_region['region']}"
        )

    print("\nImportant Limitations")
    print("---------------------")
    print(
        "- Prices are 2025 ERCOT Day-Ahead Market wholesale proxies."
    )
    print(
        "- Estimates exclude transmission, distribution, demand "
        "charges, taxes, fees, and contract-specific terms."
    )
    print(
        "- Emissions use the 2023 EPA ERCT subregion average."
    )
    print(
        "- Results are for early-stage screening, not final "
        "site selection or engineering."
    )


def main() -> None:
    print("AI Data Center Regional Energy Comparison")
    print("-----------------------------------------")

    try:
        regional_metrics = pd.read_csv(
            REGIONAL_METRICS_FILE
        )

        it_load_mw, pue, utilization = get_user_inputs()

        results = compare_regions(
            regional_metrics=regional_metrics,
            it_load_mw=it_load_mw,
            pue=pue,
            utilization=utilization,
        )

        facility_load_mw = calculate_facility_load(
            it_load_mw=it_load_mw,
            pue=pue,
        )

        annual_energy_mwh = calculate_annual_energy(
            facility_load_mw=facility_load_mw,
            utilization=utilization,
        )

        display_results(
            results=results,
            facility_load_mw=facility_load_mw,
            annual_energy_mwh=annual_energy_mwh,
        )

    except FileNotFoundError:
        print(
            "\nError: regional_metrics.csv was not found. "
            "Run the ERCOT processing script first."
        )

    except ValueError as error:
        print(f"\nInput or data error: {error}")


if __name__ == "__main__":
    main()