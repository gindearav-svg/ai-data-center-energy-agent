import pandas as pd


REQUIRED_PRICE_COLUMNS = {
    "Settlement Point",
    "Settlement Point Price",
}


def calculate_price_risk_metrics(
    price_data: pd.DataFrame,
    settlement_points: list[str],
) -> pd.DataFrame:
    """
    Calculate annual price-risk metrics for selected ERCOT
    settlement points.
    """
    missing_columns = REQUIRED_PRICE_COLUMNS - set(price_data.columns)

    if missing_columns:
        raise ValueError(
            f"Price data is missing columns: {sorted(missing_columns)}"
        )

    cleaned_data = price_data.copy()

    cleaned_data["Settlement Point"] = (
        cleaned_data["Settlement Point"]
        .astype(str)
        .str.strip()
    )

    cleaned_data["Settlement Point Price"] = pd.to_numeric(
        cleaned_data["Settlement Point Price"],
        errors="coerce",
    )

    cleaned_data = cleaned_data.dropna(
        subset=["Settlement Point Price"]
    )

    cleaned_data = cleaned_data[
        cleaned_data["Settlement Point"].isin(settlement_points)
    ]

    if cleaned_data.empty:
        raise ValueError(
            "No matching settlement points were found in the price data."
        )

    grouped_prices = cleaned_data.groupby(
        "Settlement Point"
    )["Settlement Point Price"]

    results = grouped_prices.agg(
        price_observations="count",
        average_price_usd_per_mwh="mean",
        price_standard_deviation_usd_per_mwh="std",
        p95_price_usd_per_mwh=lambda values: values.quantile(0.95),
        p99_price_usd_per_mwh=lambda values: values.quantile(0.99),
        negative_price_hours=lambda values: (values < 0).sum(),
        high_price_hours_above_100=lambda values: (values > 100).sum(),
        extreme_price_hours_above_500=lambda values: (
            values > 500
        ).sum(),
    ).reset_index()

    results = results.rename(
        columns={
            "Settlement Point": "ercot_settlement_point",
        }
    )

    numeric_columns = [
        "average_price_usd_per_mwh",
        "price_standard_deviation_usd_per_mwh",
        "p95_price_usd_per_mwh",
        "p99_price_usd_per_mwh",
    ]

    results[numeric_columns] = results[numeric_columns].round(3)

    return results