from pathlib import Path

import pandas as pd

from src.energy_agent.price_risk import (
    calculate_price_risk_metrics,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

REGION_MAPPING_PATH = (
    PROCESSED_DATA_DIR / "region_mapping.csv"
)

OUTPUT_PATH = (
    PROCESSED_DATA_DIR / "price_risk_metrics.csv"
)


def find_ercot_workbook() -> Path:
    matching_files = list(
        RAW_DATA_DIR.glob("ercot_dam_prices_2025*.xlsx")
    )

    if not matching_files:
        raise FileNotFoundError(
            "The 2025 ERCOT price workbook was not found."
        )

    if len(matching_files) > 1:
        raise ValueError(
            f"Multiple ERCOT workbooks were found: {matching_files}"
        )

    return matching_files[0]


def main() -> None:
    workbook_path = find_ercot_workbook()
    region_mapping = pd.read_csv(REGION_MAPPING_PATH)

    print(f"\nReading ERCOT workbook:\n{workbook_path}")

    monthly_sheets = pd.read_excel(
        workbook_path,
        sheet_name=None,
    )

    annual_price_data = pd.concat(
        monthly_sheets.values(),
        ignore_index=True,
    )

    settlement_points = (
        region_mapping["ercot_settlement_point"]
        .dropna()
        .unique()
        .tolist()
    )

    risk_metrics = calculate_price_risk_metrics(
        price_data=annual_price_data,
        settlement_points=settlement_points,
    )

    results = region_mapping[
        ["region", "ercot_settlement_point"]
    ].merge(
        risk_metrics,
        on="ercot_settlement_point",
        how="left",
        validate="one_to_one",
    )

    if results["price_observations"].isna().any():
        missing_regions = results.loc[
            results["price_observations"].isna(),
            "region",
        ].tolist()

        raise ValueError(
            f"Price metrics are missing for regions: {missing_regions}"
        )

    results.to_csv(OUTPUT_PATH, index=False)

    print("\nPrice Risk Metrics")
    print("------------------")
    print(results.to_string(index=False))

    print(f"\nSaved results to:\n{OUTPUT_PATH}")


if __name__ == "__main__":
    main()