import pytest

from src.energy_agent.calculations import (
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