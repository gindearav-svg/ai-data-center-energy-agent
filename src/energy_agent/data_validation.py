import pandas as pd


REQUIRED_REGIONAL_COLUMNS = {
    "region",
    "ercot_settlement_point",
    "price_year",
    "annual_average_dam_price_usd_per_mwh",
    "price_observations",
    "emissions_year",
    "grid_emissions_kg_co2e_per_mwh",
    "price_standard_deviation_usd_per_mwh",
    "p95_price_usd_per_mwh",
    "p99_price_usd_per_mwh",
    "negative_price_hours",
    "high_price_hours_above_100",
    "extreme_price_hours_above_500",
}


def validate_regional_metrics(data: pd.DataFrame) -> None:
    """
    Validate the processed regional dataset.

    Raises ValueError when one or more quality checks fail.
    """
    missing_columns = REQUIRED_REGIONAL_COLUMNS - set(data.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    errors = []

    required_data = data[list(REQUIRED_REGIONAL_COLUMNS)]

    if required_data.isna().any().any():
        errors.append("Required columns contain missing values.")

    if data["region"].duplicated().any():
        errors.append("Region names must be unique.")

    if data["ercot_settlement_point"].duplicated().any():
        errors.append("ERCOT settlement points must be unique.")

    if (data["price_observations"] != 8760).any():
        errors.append(
            "Every region must contain exactly 8,760 hourly observations."
        )

    if (
        data["price_standard_deviation_usd_per_mwh"] < 0
    ).any():
        errors.append("Price standard deviation cannot be negative.")

    if (
        data["grid_emissions_kg_co2e_per_mwh"] < 0
    ).any():
        errors.append("Grid emissions intensity cannot be negative.")

    if (
        data["p99_price_usd_per_mwh"]
        < data["p95_price_usd_per_mwh"]
    ).any():
        errors.append(
            "The 99th-percentile price cannot be below "
            "the 95th-percentile price."
        )

    event_columns = [
        "negative_price_hours",
        "high_price_hours_above_100",
        "extreme_price_hours_above_500",
    ]

    for column in event_columns:
        if (data[column] < 0).any():
            errors.append(f"{column} cannot contain negative counts.")

        if (data[column] > data["price_observations"]).any():
            errors.append(
                f"{column} cannot exceed total price observations."
            )

    if errors:
        formatted_errors = "\n- ".join(errors)

        raise ValueError(
            f"Regional data validation failed:\n- {formatted_errors}"
        )


def build_data_quality_summary(data: pd.DataFrame) -> dict:
    """Validate the data and return a compact quality summary."""
    validate_regional_metrics(data)

    return {
        "status": "passed",
        "regional_rows": int(len(data)),
        "regions": sorted(data["region"].tolist()),
        "total_price_observations": int(
            data["price_observations"].sum()
        ),
        "missing_required_values": int(
            data[list(REQUIRED_REGIONAL_COLUMNS)]
            .isna()
            .sum()
            .sum()
        ),
        "price_years": sorted(
            data["price_year"].astype(int).unique().tolist()
        ),
        "emissions_years": sorted(
            data["emissions_year"].astype(int).unique().tolist()
        ),
    }