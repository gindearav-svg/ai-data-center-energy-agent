import pandas as pd


DEFAULT_WEIGHTS = {
    "cost": 0.70,
    "carbon": 0.20,
    "price_risk": 0.10,
}


PRICE_RISK_COMPONENT_WEIGHTS = {
    "volatility": 0.35,
    "p95_price": 0.35,
    "high_price_hours": 0.20,
    "extreme_price_hours": 0.10,
}


def normalize_lower_is_better(values: pd.Series) -> pd.Series:
    """
    Convert numeric values into scores from 0 to 100.

    The lowest value receives 100.
    The highest value receives 0.
    Identical values receive a neutral score of 50.
    """
    minimum = values.min()
    maximum = values.max()

    if minimum == maximum:
        return pd.Series(50.0, index=values.index)

    return (maximum - values) / (maximum - minimum) * 100


def validate_weights(weights: dict[str, float]) -> None:
    """Verify that scoring weights are valid and total 1.0."""
    required_categories = {"cost", "carbon", "price_risk"}

    if set(weights) != required_categories:
        raise ValueError(
            f"Weights must contain exactly: {required_categories}"
        )

    if any(weight < 0 for weight in weights.values()):
        raise ValueError("Weights cannot be negative.")

    if abs(sum(weights.values()) - 1.0) > 0.000001:
        raise ValueError("Weights must add up to 1.0.")


def calculate_composite_price_risk_score(
    regional_data: pd.DataFrame,
) -> pd.Series:
    """
    Calculate a 0–100 price-risk score using multiple annual metrics.

    Higher scores represent lower exposure to volatile or extreme prices.
    """
    volatility_score = normalize_lower_is_better(
        regional_data[
            "price_standard_deviation_usd_per_mwh"
        ]
    )

    p95_score = normalize_lower_is_better(
        regional_data["p95_price_usd_per_mwh"]
    )

    high_price_hours_score = normalize_lower_is_better(
        regional_data["high_price_hours_above_100"]
    )

    extreme_price_hours_score = normalize_lower_is_better(
        regional_data["extreme_price_hours_above_500"]
    )

    composite_score = (
        volatility_score
        * PRICE_RISK_COMPONENT_WEIGHTS["volatility"]
        + p95_score
        * PRICE_RISK_COMPONENT_WEIGHTS["p95_price"]
        + high_price_hours_score
        * PRICE_RISK_COMPONENT_WEIGHTS["high_price_hours"]
        + extreme_price_hours_score
        * PRICE_RISK_COMPONENT_WEIGHTS["extreme_price_hours"]
    )

    return composite_score.round(2)


def score_regions(
    regional_data: pd.DataFrame,
    weights: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Calculate component scores, an overall score, and a rank."""
    if weights is None:
        weights = DEFAULT_WEIGHTS.copy()

    validate_weights(weights)

    required_columns = {
        "region",
        "estimated_annual_wholesale_cost_usd",
        "estimated_annual_emissions_metric_tons_co2e",
        "price_standard_deviation_usd_per_mwh",
        "p95_price_usd_per_mwh",
        "high_price_hours_above_100",
        "extreme_price_hours_above_500",
    }

    missing_columns = required_columns - set(regional_data.columns)

    if missing_columns:
        raise ValueError(
            f"Regional data is missing columns: {sorted(missing_columns)}"
        )

    scored_data = regional_data.copy()

    scored_data["cost_score"] = normalize_lower_is_better(
        scored_data["estimated_annual_wholesale_cost_usd"]
    )

    scored_data["carbon_score"] = normalize_lower_is_better(
        scored_data[
            "estimated_annual_emissions_metric_tons_co2e"
        ]
    )

    scored_data["price_risk_score"] = (
        calculate_composite_price_risk_score(scored_data)
    )

    scored_data["overall_score"] = (
        scored_data["cost_score"] * weights["cost"]
        + scored_data["carbon_score"] * weights["carbon"]
        + scored_data["price_risk_score"] * weights["price_risk"]
    ).round(2)

    scored_data["rank"] = (
        scored_data["overall_score"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    return scored_data.sort_values(
        ["rank", "region"]
    ).reset_index(drop=True)