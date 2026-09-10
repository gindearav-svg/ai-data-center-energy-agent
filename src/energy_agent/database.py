import sqlite3
from pathlib import Path

import pandas as pd

from src.energy_agent.data_validation import (
    validate_regional_metrics,
)


def connect_database(database_path: Path) -> sqlite3.Connection:
    """Open a SQLite connection with foreign-key enforcement."""
    database_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_schema(
    connection: sqlite3.Connection,
    schema_path: Path,
) -> None:
    """Create the database tables and indexes."""
    schema_sql = schema_path.read_text(encoding="utf-8")
    connection.executescript(schema_sql)


def load_regional_metrics(
    connection: sqlite3.Connection,
    regional_data: pd.DataFrame,
) -> None:
    """
    Insert or update validated regional metrics in SQLite.
    """
    validate_regional_metrics(regional_data)

    for row in regional_data.to_dict(orient="records"):
        connection.execute(
            """
            INSERT INTO regions (
                region_name,
                ercot_settlement_point,
                egrid_subregion,
                noaa_station_id,
                noaa_station_name
            )
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(region_name) DO UPDATE SET
                ercot_settlement_point =
                    excluded.ercot_settlement_point,
                egrid_subregion =
                    excluded.egrid_subregion,
                noaa_station_id =
                    excluded.noaa_station_id,
                noaa_station_name =
                    excluded.noaa_station_name
            """,
            (
                row["region"],
                row["ercot_settlement_point"],
                row["egrid_subregion"],
                row["noaa_station_id"],
                row["noaa_station_name"],
            ),
        )

        region_result = connection.execute(
            """
            SELECT region_id
            FROM regions
            WHERE region_name = ?
            """,
            (row["region"],),
        ).fetchone()

        if region_result is None:
            raise RuntimeError(
                f"Could not retrieve region ID for {row['region']}."
            )

        region_id = region_result[0]

        metric_values = {
            "region_id": region_id,
            "price_year": int(row["price_year"]),
            "emissions_year": int(row["emissions_year"]),
            "average_price": float(
                row["annual_average_dam_price_usd_per_mwh"]
            ),
            "median_price": float(
                row["annual_median_dam_price_usd_per_mwh"]
            ),
            "minimum_price": float(
                row["minimum_dam_price_usd_per_mwh"]
            ),
            "maximum_price": float(
                row["maximum_dam_price_usd_per_mwh"]
            ),
            "observations": int(row["price_observations"]),
            "emissions": float(
                row["grid_emissions_kg_co2e_per_mwh"]
            ),
            "standard_deviation": float(
                row["price_standard_deviation_usd_per_mwh"]
            ),
            "p95_price": float(
                row["p95_price_usd_per_mwh"]
            ),
            "p99_price": float(
                row["p99_price_usd_per_mwh"]
            ),
            "negative_hours": int(
                row["negative_price_hours"]
            ),
            "high_price_hours": int(
                row["high_price_hours_above_100"]
            ),
            "extreme_price_hours": int(
                row["extreme_price_hours_above_500"]
            ),
        }

        connection.execute(
            """
            INSERT INTO regional_metrics (
                region_id,
                price_year,
                emissions_year,
                annual_average_dam_price_usd_per_mwh,
                annual_median_dam_price_usd_per_mwh,
                minimum_dam_price_usd_per_mwh,
                maximum_dam_price_usd_per_mwh,
                price_observations,
                grid_emissions_kg_co2e_per_mwh,
                price_standard_deviation_usd_per_mwh,
                p95_price_usd_per_mwh,
                p99_price_usd_per_mwh,
                negative_price_hours,
                high_price_hours_above_100,
                extreme_price_hours_above_500
            )
            VALUES (
                :region_id,
                :price_year,
                :emissions_year,
                :average_price,
                :median_price,
                :minimum_price,
                :maximum_price,
                :observations,
                :emissions,
                :standard_deviation,
                :p95_price,
                :p99_price,
                :negative_hours,
                :high_price_hours,
                :extreme_price_hours
            )
            ON CONFLICT(
                region_id,
                price_year,
                emissions_year
            )
            DO UPDATE SET
                annual_average_dam_price_usd_per_mwh =
                    excluded.annual_average_dam_price_usd_per_mwh,
                annual_median_dam_price_usd_per_mwh =
                    excluded.annual_median_dam_price_usd_per_mwh,
                minimum_dam_price_usd_per_mwh =
                    excluded.minimum_dam_price_usd_per_mwh,
                maximum_dam_price_usd_per_mwh =
                    excluded.maximum_dam_price_usd_per_mwh,
                price_observations =
                    excluded.price_observations,
                grid_emissions_kg_co2e_per_mwh =
                    excluded.grid_emissions_kg_co2e_per_mwh,
                price_standard_deviation_usd_per_mwh =
                    excluded.price_standard_deviation_usd_per_mwh,
                p95_price_usd_per_mwh =
                    excluded.p95_price_usd_per_mwh,
                p99_price_usd_per_mwh =
                    excluded.p99_price_usd_per_mwh,
                negative_price_hours =
                    excluded.negative_price_hours,
                high_price_hours_above_100 =
                    excluded.high_price_hours_above_100,
                extreme_price_hours_above_500 =
                    excluded.extreme_price_hours_above_500
            """,
            metric_values,
        )


def initialize_database(
    database_path: Path,
    schema_path: Path,
    regional_data: pd.DataFrame,
) -> None:
    """Create the schema and load the regional dataset."""
    connection = connect_database(database_path)

    try:
        create_schema(connection, schema_path)
        load_regional_metrics(connection, regional_data)
        connection.commit()
    finally:
        connection.close()