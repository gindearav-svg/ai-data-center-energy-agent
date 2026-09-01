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