import pandas as pd
import pytest

from src.energy_agent.analysis import compare_regions


@pytest.fixture
def example_regional_data() -> pd.DataFrame:
    """Create a small controlled dataset for testing."""

    return pd.DataFrame(
        {
            "region": [
                "Region A",
                "Region B",
            ],
            "annual_average_dam_price_usd_per_mwh": [
                50,
                30,
            ],
            "grid_emissions_kg_co2e_per_mwh": [
                400,
                400,
            ],
        }
    )


def test_compare_regions_ranks_lowest_cost_first(
    example_regional_data: pd.DataFrame,
) -> None:
    results = compare_regions(
        regional_metrics=example_regional_data,
        it_load_mw=10,
        pue=1.2,
        utilization=1.0,
    )

    assert results.iloc[0]["region"] == "Region B"
    assert results.iloc[1]["region"] == "Region A"


def test_compare_regions_calculates_expected_values(
    example_regional_data: pd.DataFrame,
) -> None:
    results = compare_regions(
        regional_metrics=example_regional_data,
        it_load_mw=10,
        pue=1.2,
        utilization=1.0,
    )

    region_b = results[
        results["region"] == "Region B"
    ].iloc[0]

    assert region_b["facility_load_mw"] == pytest.approx(12)
    assert region_b["annual_energy_mwh"] == pytest.approx(105_120)

    assert region_b[
        "estimated_annual_wholesale_cost_usd"
    ] == pytest.approx(3_153_600)

    assert region_b[
        "estimated_annual_emissions_metric_tons_co2e"
    ] == pytest.approx(42_048)


def test_compare_regions_rejects_missing_columns() -> None:
    invalid_data = pd.DataFrame(
        {
            "region": ["Region A"],
        }
    )

    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        compare_regions(
            regional_metrics=invalid_data,
            it_load_mw=10,
            pue=1.2,
            utilization=1.0,
        )