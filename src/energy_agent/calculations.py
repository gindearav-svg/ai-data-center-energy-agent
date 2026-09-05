HOURS_PER_YEAR = 8760


def calculate_facility_load(it_load_mw: float, pue: float) -> float:
    """Calculate total facility power demand in megawatts."""

    if it_load_mw <= 0:
        raise ValueError("IT load must be greater than zero.")

    if pue < 1:
        raise ValueError("PUE cannot be less than 1.0.")

    return it_load_mw * pue


def calculate_annual_energy(
    facility_load_mw: float,
    utilization: float,
) -> float:
    """Calculate annual electricity consumption in megawatt-hours."""

    if facility_load_mw <= 0:
        raise ValueError("Facility load must be greater than zero.")

    if not 0 < utilization <= 1:
        raise ValueError("Utilization must be greater than 0 and no more than 1.")

    return facility_load_mw * HOURS_PER_YEAR * utilization

def calculate_annual_cost(
    annual_energy_mwh: float,
    electricity_price_usd_per_mwh: float,
) -> float:
    """Calculate annual wholesale electricity cost in US dollars."""

    if annual_energy_mwh <= 0:
        raise ValueError("Annual energy must be greater than zero.")

    if electricity_price_usd_per_mwh < 0:
        raise ValueError("Electricity price cannot be negative.")

    return annual_energy_mwh * electricity_price_usd_per_mwh


def calculate_annual_emissions_metric_tons(
    annual_energy_mwh: float,
    emissions_intensity_kg_per_mwh: float,
) -> float:
    """Calculate annual operational emissions in metric tons CO2e."""

    if annual_energy_mwh <= 0:
        raise ValueError("Annual energy must be greater than zero.")

    if emissions_intensity_kg_per_mwh < 0:
        raise ValueError("Emissions intensity cannot be negative.")

    emissions_kg = annual_energy_mwh * emissions_intensity_kg_per_mwh

    return emissions_kg / 1000