from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

ERCOT_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "ercot_dam_prices_2025.xlsx"
)

REGION_MAPPING_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "region_mapping.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "regional_metrics.csv"
)

TARGET_SETTLEMENT_POINTS = {
    "LZ_NORTH",
    "LZ_HOUSTON",
    "LZ_WEST",
}

REQUIRED_COLUMNS = {
    "Delivery Date",
    "Hour Ending",
    "Repeated Hour Flag",
    "Settlement Point",
    "Settlement Point Price",
}


def load_ercot_workbook() -> pd.DataFrame:
    """Load and combine every monthly sheet in the ERCOT workbook."""

    if not ERCOT_FILE.exists():
        raise FileNotFoundError(
            f"ERCOT file was not found at {ERCOT_FILE}"
        )

    monthly_sheets = pd.read_excel(
        ERCOT_FILE,
        sheet_name=None,
    )

    monthly_frames = []

    for month_name, monthly_data in monthly_sheets.items():
        monthly_data.columns = [
            str(column).strip()
            for column in monthly_data.columns
        ]

        missing_columns = REQUIRED_COLUMNS - set(monthly_data.columns)

        if missing_columns:
            raise ValueError(
                f"Sheet {month_name} is missing columns: "
                f"{sorted(missing_columns)}"
            )

        monthly_data["Source Month"] = month_name
        monthly_frames.append(monthly_data)

    return pd.concat(
        monthly_frames,
        ignore_index=True,
    )


def calculate_annual_price_summary(
    all_prices: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate annual price statistics for the selected load zones."""

    all_prices["Settlement Point"] = (
        all_prices["Settlement Point"]
        .astype(str)
        .str.strip()
    )

    all_prices["Settlement Point Price"] = pd.to_numeric(
        all_prices["Settlement Point Price"],
        errors="coerce",
    )

    selected_prices = all_prices[
        all_prices["Settlement Point"].isin(
            TARGET_SETTLEMENT_POINTS
        )
    ].copy()

    found_points = set(selected_prices["Settlement Point"].unique())
    missing_points = TARGET_SETTLEMENT_POINTS - found_points

    if missing_points:
        raise ValueError(
            "The following settlement points were not found: "
            f"{sorted(missing_points)}"
        )

    missing_price_count = (
        selected_prices["Settlement Point Price"]
        .isna()
        .sum()
    )

    if missing_price_count:
        print(
            f"Warning: removing {missing_price_count} rows "
            "with missing or non-numeric prices."
        )

        selected_prices = selected_prices.dropna(
            subset=["Settlement Point Price"]
        )

    summary = (
        selected_prices
        .groupby("Settlement Point")["Settlement Point Price"]
        .agg(
            annual_average_dam_price_usd_per_mwh="mean",
            annual_median_dam_price_usd_per_mwh="median",
            minimum_dam_price_usd_per_mwh="min",
            maximum_dam_price_usd_per_mwh="max",
            price_observations="count",
        )
        .reset_index()
    )

    return summary


def create_regional_metrics(
    price_summary: pd.DataFrame,
) -> pd.DataFrame:
    """Join ERCOT results to project regions and add eGRID emissions."""

    region_mapping = pd.read_csv(REGION_MAPPING_FILE)

    regional_metrics = region_mapping.merge(
        price_summary,
        left_on="ercot_settlement_point",
        right_on="Settlement Point",
        how="left",
        validate="one_to_one",
    )

    missing_prices = regional_metrics[
        "annual_average_dam_price_usd_per_mwh"
    ].isna()

    if missing_prices.any():
        failed_regions = regional_metrics.loc[
            missing_prices,
            "region",
        ].tolist()

        raise ValueError(
            f"Missing price results for regions: {failed_regions}"
        )

    regional_metrics["price_year"] = 2025
    regional_metrics["emissions_year"] = 2023
    regional_metrics[
        "grid_emissions_kg_co2e_per_mwh"
    ] = 334.129

    regional_metrics[
        "annual_average_dam_price_usd_per_mwh"
    ] = regional_metrics[
        "annual_average_dam_price_usd_per_mwh"
    ].round(3)

    regional_metrics[
        "annual_median_dam_price_usd_per_mwh"
    ] = regional_metrics[
        "annual_median_dam_price_usd_per_mwh"
    ].round(3)

    regional_metrics[
        "minimum_dam_price_usd_per_mwh"
    ] = regional_metrics[
        "minimum_dam_price_usd_per_mwh"
    ].round(3)

    regional_metrics[
        "maximum_dam_price_usd_per_mwh"
    ] = regional_metrics[
        "maximum_dam_price_usd_per_mwh"
    ].round(3)

    output_columns = [
        "region",
        "ercot_settlement_point",
        "price_year",
        "annual_average_dam_price_usd_per_mwh",
        "annual_median_dam_price_usd_per_mwh",
        "minimum_dam_price_usd_per_mwh",
        "maximum_dam_price_usd_per_mwh",
        "price_observations",
        "egrid_subregion",
        "emissions_year",
        "grid_emissions_kg_co2e_per_mwh",
        "noaa_station_id",
        "noaa_station_name",
    ]

    return regional_metrics[output_columns]


def main() -> None:
    print("Loading all twelve ERCOT monthly sheets...")

    all_prices = load_ercot_workbook()

    print(f"Loaded {len(all_prices):,} total price records.")

    price_summary = calculate_annual_price_summary(all_prices)
    regional_metrics = create_regional_metrics(price_summary)

    regional_metrics.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\nAnnual ERCOT Day-Ahead Price Summary")
    print("------------------------------------")

    display_columns = [
        "region",
        "ercot_settlement_point",
        "annual_average_dam_price_usd_per_mwh",
        "price_observations",
    ]

    print(
        regional_metrics[display_columns]
        .to_string(index=False)
    )

    print(f"\nSaved processed data to:\n{OUTPUT_FILE}")


if __name__ == "__main__":
    main()