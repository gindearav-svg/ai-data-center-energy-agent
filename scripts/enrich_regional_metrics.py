from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

REGIONAL_METRICS_PATH = (
    PROCESSED_DATA_DIR / "regional_metrics.csv"
)

PRICE_RISK_PATH = (
    PROCESSED_DATA_DIR / "price_risk_metrics.csv"
)


RISK_COLUMNS = [
    "price_standard_deviation_usd_per_mwh",
    "p95_price_usd_per_mwh",
    "p99_price_usd_per_mwh",
    "negative_price_hours",
    "high_price_hours_above_100",
    "extreme_price_hours_above_500",
]


def main() -> None:
    regional_metrics = pd.read_csv(REGIONAL_METRICS_PATH)
    price_risk = pd.read_csv(PRICE_RISK_PATH)

    required_columns = {
        "region",
        "ercot_settlement_point",
        *RISK_COLUMNS,
    }

    missing_columns = required_columns - set(price_risk.columns)

    if missing_columns:
        raise ValueError(
            f"Price-risk data is missing columns: "
            f"{sorted(missing_columns)}"
        )

    # Removing existing copies makes this script safe to rerun.
    regional_metrics = regional_metrics.drop(
        columns=RISK_COLUMNS,
        errors="ignore",
    )

    risk_data = price_risk[
        [
            "region",
            "ercot_settlement_point",
            *RISK_COLUMNS,
        ]
    ]

    enriched_data = regional_metrics.merge(
        risk_data,
        on=["region", "ercot_settlement_point"],
        how="left",
        validate="one_to_one",
    )

    if enriched_data[RISK_COLUMNS].isna().any().any():
        raise ValueError(
            "At least one region is missing price-risk metrics."
        )

    enriched_data.to_csv(
        REGIONAL_METRICS_PATH,
        index=False,
    )

    print("\nEnriched Regional Metrics")
    print("-------------------------")

    print(
        enriched_data[
            [
                "region",
                "annual_average_dam_price_usd_per_mwh",
                *RISK_COLUMNS,
            ]
        ].to_string(index=False)
    )

    print(f"\nUpdated:\n{REGIONAL_METRICS_PATH}")


if __name__ == "__main__":
    main()