import sqlite3
from pathlib import Path

import pandas as pd


def require_database(database_path: Path) -> None:
    """Raise an error instead of creating an empty database."""
    if not database_path.exists():
        raise FileNotFoundError(
            f"Database does not exist: {database_path}"
        )


def list_regions(database_path: Path) -> list[str]:
    """Return all available region names alphabetically."""
    require_database(database_path)

    with sqlite3.connect(database_path) as connection:
        rows = connection.execute(
            """
            SELECT region_name
            FROM regions
            ORDER BY region_name
            """
        ).fetchall()

    return [row[0] for row in rows]


def get_region_metrics(
    database_path: Path,
    region_name: str,
) -> dict:
    """
    Return the latest stored metrics for one region.

    The parameter placeholder prevents SQL injection.
    """
    require_database(database_path)

    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row

        row = connection.execute(
            """
            SELECT
                r.region_name AS region,
                r.ercot_settlement_point,
                r.egrid_subregion,
                r.noaa_station_id,
                r.noaa_station_name,
                m.price_year,
                m.emissions_year,
                m.annual_average_dam_price_usd_per_mwh,
                m.annual_median_dam_price_usd_per_mwh,
                m.minimum_dam_price_usd_per_mwh,
                m.maximum_dam_price_usd_per_mwh,
                m.price_observations,
                m.grid_emissions_kg_co2e_per_mwh,
                m.price_standard_deviation_usd_per_mwh,
                m.p95_price_usd_per_mwh,
                m.p99_price_usd_per_mwh,
                m.negative_price_hours,
                m.high_price_hours_above_100,
                m.extreme_price_hours_above_500
            FROM regions AS r
            JOIN regional_metrics AS m
                ON r.region_id = m.region_id
            WHERE r.region_name = ?
            ORDER BY
                m.price_year DESC,
                m.emissions_year DESC
            LIMIT 1
            """,
            (region_name,),
        ).fetchone()

    if row is None:
        raise ValueError(
            f"Region is not available: {region_name}"
        )

    return dict(row)


def compare_all_regions(
    database_path: Path,
) -> pd.DataFrame:
    """Return the latest metrics for every stored region."""
    require_database(database_path)

    query = """
        SELECT
            r.region_name AS region,
            r.ercot_settlement_point,
            m.price_year,
            m.emissions_year,
            m.annual_average_dam_price_usd_per_mwh,
            m.grid_emissions_kg_co2e_per_mwh,
            m.price_standard_deviation_usd_per_mwh,
            m.p95_price_usd_per_mwh,
            m.p99_price_usd_per_mwh,
            m.negative_price_hours,
            m.high_price_hours_above_100,
            m.extreme_price_hours_above_500
        FROM regions AS r
        JOIN regional_metrics AS m
            ON r.region_id = m.region_id
        WHERE m.price_year = (
            SELECT MAX(latest.price_year)
            FROM regional_metrics AS latest
            WHERE latest.region_id = r.region_id
        )
        ORDER BY
            m.annual_average_dam_price_usd_per_mwh,
            r.region_name
    """

    with sqlite3.connect(database_path) as connection:
        results = pd.read_sql_query(
            query,
            connection,
        )

    return results