#!/usr/bin/env python3
"""
Initialize DuckDB database schema for Sovereign Credit Rating Methodology (Stomper 2026).
Creates all core relational input tables. The database is strictly read-only for rating runs.
"""

import os
import duckdb

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'sovereign_ratings.duckdb')

def init_db(db_path: str = DB_PATH):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    con = duckdb.connect(db_path)

    # 1. Countries master table
    con.execute("""
    CREATE TABLE IF NOT EXISTS countries (
        country_id VARCHAR PRIMARY KEY,
        name VARCHAR NOT NULL,
        iso2 VARCHAR(2) NOT NULL,
        iso3 VARCHAR(3) NOT NULL,
        currency VARCHAR(3) NOT NULL,
        monetary_tier VARCHAR NOT NULL, -- 'euro_area' or 'own_currency'
        has_backstop BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Historical GDP growth series (Task A1)
    con.execute("""
    CREATE TABLE IF NOT EXISTS country_gdp_growth (
        country_id VARCHAR,
        year INTEGER,
        nominal_gdp_growth_pct DOUBLE,
        log_growth DOUBLE,
        source VARCHAR,
        PRIMARY KEY (country_id, year),
        FOREIGN KEY (country_id) REFERENCES countries(country_id)
    );
    """)

    # 3. Historical primary balance series (Task A2)
    con.execute("""
    CREATE TABLE IF NOT EXISTS country_primary_balance (
        country_id VARCHAR,
        year INTEGER,
        primary_balance_gdp_pct DOUBLE,
        source VARCHAR,
        PRIMARY KEY (country_id, year),
        FOREIGN KEY (country_id) REFERENCES countries(country_id)
    );
    """)

    # 4. State of Affairs: debt stock, short-term debt, maturity, deficit, financing need (Task B1, B2)
    con.execute("""
    CREATE TABLE IF NOT EXISTS country_debt_state (
        country_id VARCHAR,
        as_of_date DATE,
        year INTEGER,
        gross_debt_gdp_pct DOUBLE,
        short_term_debt_gdp_pct DOUBLE,
        wam_years DOUBLE,
        headline_deficit_gdp_pct DOUBLE,
        planned_primary_balance_pct DOUBLE,
        gfn_gdp_pct DOUBLE,
        yield_10y_pct DOUBLE,
        spread_10y_bps DOUBLE,
        domestic_bank_debt_share DOUBLE,
        foreign_private_share DOUBLE,
        source VARCHAR,
        PRIMARY KEY (country_id, as_of_date),
        FOREIGN KEY (country_id) REFERENCES countries(country_id)
    );
    """)

    # 5. Calibrated country parameters (Tasks C1-C6)
    con.execute("""
    CREATE TABLE IF NOT EXISTS country_parameters (
        country_id VARCHAR,
        as_of_date DATE,
        mu_r DOUBLE DEFAULT 0.014,
        pi_u DOUBLE DEFAULT 0.020,
        inflation_diff_projected DOUBLE DEFAULT 0.0,
        e_mrp DOUBLE DEFAULT 0.0,
        mu_hat DOUBLE,
        sigma_hat DOUBLE,
        s_bar DOUBLE,
        rf_gross DOUBLE,
        haircut_baseline DOUBLE,
        beta_loading DOUBLE DEFAULT 1.0,
        source VARCHAR,
        PRIMARY KEY (country_id, as_of_date),
        FOREIGN KEY (country_id) REFERENCES countries(country_id)
    );
    """)

    # 6. Global market state & VIX pricing factor (Task B3)
    con.execute("""
    CREATE TABLE IF NOT EXISTS global_market_state (
        as_of_date DATE PRIMARY KEY,
        vix_level DOUBLE,
        z_vix DOUBLE,
        theta_hat DOUBLE,
        theta_inf DOUBLE DEFAULT 0.30,
        sigma_theta DOUBLE DEFAULT 0.25,
        rho_theta DOUBLE DEFAULT 1.0,
        source VARCHAR
    );
    """)

    con.close()
    print(f"DuckDB schema initialized successfully at {db_path}")

if __name__ == '__main__':
    init_db()
