from src.energy_agent.calculations import (
    calculate_annual_energy,
    calculate_facility_load,
)


def main() -> None:
    print("AI Data Center Energy Calculator")
    print("--------------------------------")

    it_load_mw = float(input("Enter IT load in MW: "))
    pue = float(input("Enter expected PUE: "))
    utilization_percent = float(
        input("Enter expected average utilization (%): ")
    )

    utilization = utilization_percent / 100

    facility_load_mw = calculate_facility_load(it_load_mw, pue)
    annual_energy_mwh = calculate_annual_energy(
        facility_load_mw,
        utilization,
    )

    print("\nEstimated Energy Requirements")
    print(f"Facility load: {facility_load_mw:,.2f} MW")
    print(f"Annual energy: {annual_energy_mwh:,.0f} MWh")
    print(f"Annual energy: {annual_energy_mwh / 1_000_000:,.3f} TWh")


if __name__ == "__main__":
    main()