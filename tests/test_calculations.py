import pytest

from src.energy_agent.calculations import (
    calculate_annual_cost,
    calculate_annual_emissions_metric_tons,
    calculate_annual_energy,
    calculate_facility_load,
)


def test_facility_load_calculation() -> None:
    result = calculate_facility_load(
        it_load_mw=200,
        pue=1.25,
    )

    assert result == 250


def test_annual_energy_calculation() -> None:
    result = calculate_annual_energy(
        facility_load_mw=250,
        utilization=0.95,
    )

    assert result == 2_080_500


def test_rejects_negative_it_load() -> None:
    with pytest.raises(ValueError):
        calculate_facility_load(
            it_load_mw=-200,
            pue=1.25,
        )


def test_rejects_impossible_pue() -> None:
    with pytest.raises(ValueError):
        calculate_facility_load(
            it_load_mw=200,
            pue=0.90,
        )


def test_rejects_utilization_above_100_percent() -> None:
    with pytest.raises(ValueError):
        calculate_annual_energy(
            facility_load_mw=250,
            utilization=1.10,
        )

def test_annual_cost_calculation() -> None:
    result = calculate_annual_cost(
        annual_energy_mwh=2_080_500,
        electricity_price_usd_per_mwh=40,
    )

    assert result == pytest.approx(83_220_000)


def test_rejects_negative_electricity_price() -> None:
    with pytest.raises(ValueError):
        calculate_annual_cost(
            annual_energy_mwh=2_080_500,
            electricity_price_usd_per_mwh=-10,
        )


def test_annual_emissions_calculation() -> None:
    result = calculate_annual_emissions_metric_tons(
        annual_energy_mwh=2_080_500,
        emissions_intensity_kg_per_mwh=334.129,
    )

    assert result == pytest.approx(695_155.3845)


def test_rejects_negative_emissions_intensity() -> None:
    with pytest.raises(ValueError):
        calculate_annual_emissions_metric_tons(
            annual_energy_mwh=2_080_500,
            emissions_intensity_kg_per_mwh=-100,
        )