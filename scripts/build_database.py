import sqlite3
from pathlib import Path

import pandas as pd

from src.energy_agent.database import initialize_database


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REGIONAL_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "regional_metrics.csv"
)

SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"

DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "energy_intelligence.db"
)


def main() -> None:
    regional_data = pd.read_csv(REGIONAL_DATA_PATH)

    initialize_database(
        database_path=DATABASE_PATH,
        schema_path=SCHEMA_PATH,
        regional_data=regional_data,
    )

    with sqlite3.connect(DATABASE_PATH) as connection:
        results = connection.execute(
            """
            SELECT
                r.region_name,
                m.price_year,
                m.annual_average_dam_price_usd_per_mwh,
                m.price_standard_deviation_usd_per_mwh,
                m.grid_emissions_kg_co2e_per_mwh
            FROM regions AS r
            JOIN regional_metrics AS m
                ON r.region_id = m.region_id
            ORDER BY
                m.annual_average_dam_price_usd_per_mwh
            """
        ).fetchall()

    print("\nSQLite Regional Energy Database")
    print("-------------------------------")

    for row in results:
        region, year, average_price, volatility, emissions = row

        print(
            f"{region}: "
            f"year={year}, "
            f"average_price=${average_price:.3f}/MWh, "
            f"volatility=${volatility:.3f}/MWh, "
            f"emissions={emissions:.3f} kg CO2e/MWh"
        )

    print(f"\nDatabase created at:\n{DATABASE_PATH}")


if __name__ == "__main__":
    main()