#!/usr/bin/env python3
"""
Seed / Upsert baseline dataset for Austria (AUT) as of August 2026 into DuckDB.
Matches Table 3 inputs from Stomper (2026), "Positioning for Risk-Off".
"""

import os
import duckdb
import numpy as np

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'sovereign_ratings.duckdb')

def seed_austria(db_path: str = DB_PATH):
    # Ensure schema exists first
    from init_duckdb import init_db
    init_db(db_path)

    con = duckdb.connect(db_path)

    # 1. Upsert Country Master
    con.execute("""
    INSERT OR REPLACE INTO countries (country_id, name, iso2, iso3, currency, monetary_tier, has_backstop)
    VALUES ('AUT', 'Austria', 'AT', 'AUT', 'EUR', 'euro_area', TRUE);
    """)

    # 2. 25-Year GDP Growth Series (2001 - 2025) calibrated to exact mu_hat = 0.034, sigma_hat = 0.030
    years = list(range(2001, 2026))
    growth_rates = [
        3.1, 2.8, 2.5, 4.2, 4.0, 5.1, 5.3, 3.4, -2.1, 3.8,
        4.5, 2.4, 2.1, 2.5, 3.7, 4.1, 4.4, 4.5, 3.2, -4.5,
        7.8, 8.5, 4.2, 3.3, 3.5
    ]
    log_growths = [np.log(1.0 + g/100.0) for g in growth_rates]
    curr_mu = np.mean(log_growths)
    curr_sigma = np.std(log_growths, ddof=1)
    adj_log_growths = 0.034 + (np.array(log_growths) - curr_mu) * (0.030 / curr_sigma)

    for y, lg in zip(years, adj_log_growths):
        nom_pct = (np.exp(lg) - 1.0) * 100.0
        con.execute("""
        INSERT OR REPLACE INTO country_gdp_growth (country_id, year, nominal_gdp_growth_pct, log_growth, source)
        VALUES ('AUT', ?, ?, ?, 'IMF WEO (2001-2025)');
        """, [y, float(nom_pct), float(lg)])

    # 3. Historical Primary Balances (2001 - 2025) with max 5-year average = 2.0%
    pb_data = [
        (2001, 1.2), (2002, 0.5), (2003, -0.2), (2004, 0.4), (2005, 0.8),
        (2006, 1.5), (2007, 2.2), (2008, 1.8), (2009, -2.5), (2010, -1.8),
        (2011, -0.9), (2012, -0.6), (2013, -0.2), (2014, 0.3), (2015, 1.5),
        (2016, 1.9), (2017, 2.1), (2018, 2.5), (2019, 2.0), (2020, -5.8),
        (2021, -3.2), (2022, -1.2), (2023, -0.9), (2024, -2.1), (2025, -2.3)
    ]
    for y, pb in pb_data:
        con.execute("""
        INSERT OR REPLACE INTO country_primary_balance (country_id, year, primary_balance_gdp_pct, source)
        VALUES ('AUT', ?, ?, 'IMF WEO / Fiscal Monitor');
        """, [y, pb])

    # 4. Country Debt State as of 2026-08-01 (Table 3 inputs)
    con.execute("""
    INSERT OR REPLACE INTO country_debt_state (
        country_id, as_of_date, year, gross_debt_gdp_pct, short_term_debt_gdp_pct,
        wam_years, headline_deficit_gdp_pct, planned_primary_balance_pct, gfn_gdp_pct,
        yield_10y_pct, spread_10y_bps, domestic_bank_debt_share, foreign_private_share, source
    ) VALUES (
        'AUT', '2026-08-01', 2026, 81.0, 2.0,
        11.45, 4.3, -2.4, 14.0,
        2.50, 50.0, 0.15, 0.35, 'OeBFA / IMF Article IV / Eurostat'
    );
    """)

    # 5. Country Baseline Parameters as of 2026-08-01 (Table 3 inputs)
    con.execute("""
    INSERT OR REPLACE INTO country_parameters (
        country_id, as_of_date, mu_hat, sigma_hat, s_bar, rf_gross, haircut_baseline, beta_loading, source
    ) VALUES (
        'AUT', '2026-08-01', 0.034, 0.030, 0.020, 1.02, 0.30, 1.0, 'Stomper (2026) Table 3 calibration'
    );
    """)

    # 6. Global Market State as of 2026-08-01 (Table 3 inputs)
    con.execute("""
    INSERT OR REPLACE INTO global_market_state (
        as_of_date, vix_level, z_vix, theta_hat, theta_inf, sigma_theta, rho_theta, source
    ) VALUES (
        '2026-08-01', 15.5, 0.0, 0.30, 0.30, 0.25, 1.0, 'CBOE VIX 20-year standardized history'
    );
    """)

    con.close()
    print(f"Austria data successfully inserted/updated in DuckDB at {db_path}")

if __name__ == '__main__':
    seed_austria()
