PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS regions (
    region_id INTEGER PRIMARY KEY AUTOINCREMENT,
    region_name TEXT NOT NULL UNIQUE,
    ercot_settlement_point TEXT NOT NULL UNIQUE,
    egrid_subregion TEXT NOT NULL,
    noaa_station_id TEXT NOT NULL,
    noaa_station_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS regional_metrics (
    metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
    region_id INTEGER NOT NULL,
    price_year INTEGER NOT NULL,
    emissions_year INTEGER NOT NULL,
    annual_average_dam_price_usd_per_mwh REAL NOT NULL,
    annual_median_dam_price_usd_per_mwh REAL NOT NULL,
    minimum_dam_price_usd_per_mwh REAL NOT NULL,
    maximum_dam_price_usd_per_mwh REAL NOT NULL,
    price_observations INTEGER NOT NULL,
    grid_emissions_kg_co2e_per_mwh REAL NOT NULL,
    price_standard_deviation_usd_per_mwh REAL NOT NULL,
    p95_price_usd_per_mwh REAL NOT NULL,
    p99_price_usd_per_mwh REAL NOT NULL,
    negative_price_hours INTEGER NOT NULL,
    high_price_hours_above_100 INTEGER NOT NULL,
    extreme_price_hours_above_500 INTEGER NOT NULL,

    FOREIGN KEY (region_id)
        REFERENCES regions(region_id)
        ON DELETE CASCADE,

    UNIQUE (region_id, price_year, emissions_year)
);

CREATE INDEX IF NOT EXISTS idx_regional_metrics_region
ON regional_metrics(region_id);

CREATE INDEX IF NOT EXISTS idx_regional_metrics_years
ON regional_metrics(price_year, emissions_year);