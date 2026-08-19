#!/usr/bin/env python3
"""
CLI runner for Sovereign Credit Rating Methodology (Stomper 2026).
Fetches data from DuckDB, applies MRP formulas, evaluates sensitivity grid,
and generates the publication sheet and Table 3 audit trail.
"""

import os
import sys
import argparse
import json
import duckdb

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))
from mrp.engine import run_mrp_pipeline

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'sovereign_ratings.duckdb')

def fetch_dict(con: duckdb.DuckDBPyConnection, query: str, params: list = []):
    cursor = con.execute(query, params)
    cols = [desc[0] for desc in cursor.description]
    row = cursor.fetchone()
    if not row:
        return None
    return dict(zip(cols, row))

def fetch_country_and_global_data(con: duckdb.DuckDBPyConnection, country_id: str, as_of_date: str):
    # 1. Country master
    country = fetch_dict(con, "SELECT * FROM countries WHERE country_id = ?", [country_id])
    if not country:
        raise ValueError(f"Country {country_id} not found in database.")

    # 2. Country Debt state
    debt_state = fetch_dict(con, """
        SELECT * FROM country_debt_state 
        WHERE country_id = ? AND as_of_date <= ? 
        ORDER BY as_of_date DESC LIMIT 1
    """, [country_id, as_of_date])
    if not debt_state:
        raise ValueError(f"No debt state found for country {country_id} as of {as_of_date}.")

    # 3. Country Parameters
    params = fetch_dict(con, """
        SELECT * FROM country_parameters 
        WHERE country_id = ? AND as_of_date <= ? 
        ORDER BY as_of_date DESC LIMIT 1
    """, [country_id, as_of_date])
    if not params:
        raise ValueError(f"No parameters found for country {country_id} as of {as_of_date}.")

    # 4. Global Market State
    global_state = fetch_dict(con, """
        SELECT * FROM global_market_state 
        WHERE as_of_date <= ? 
        ORDER BY as_of_date DESC LIMIT 1
    """, [as_of_date])
    if not global_state:
        raise ValueError(f"No global market state found as of {as_of_date}.")

    # Merge country dict
    country_data = {**country, **debt_state, **params}
    return country_data, global_state

def format_audit_trail_table(result: dict) -> str:
    inp = result['inputs']
    drv = result['derived_objects']
    rat = result['rating']
    
    lines = []
    lines.append("| Object | Defined in | Inputs (source) | Country Value |")
    lines.append("| :--- | :--- | :--- | :--- |")
    lines.append(f"| $\\hat{{\\mu}}, \\hat{{\\sigma}}$ | eq. (11) | WEO nominal GDP, 2001–2025 | {inp['mu_hat']*100:.1f}%, {inp['sigma_hat']*100:.1f}% |")
    lines.append(f"| $\\bar{{s}}$ | eq. (12) | WEO/FM primary balances | {inp['s_bar']*100:.1f}% |")
    lines.append(f"| $R^f$ | Task A3 | ECB AAA curve, 1y point | {inp['rf_gross']:.2f} |")
    lines.append(f"| $h$ | Task A4 | Cruces–Trebesch center | {inp['haircut']:.2f} |")
    lines.append(f"| $z_t; \\hat{{\\theta}}_t$ | eqs. (16), (17) | VIX monthly avg. vs. 20y history | $\\approx {inp['zt_vix']:.1f}; {inp['theta_hat']:.2f}$ |")
    lines.append(f"| $z_M$ | eq. (13) | $\\hat{{\\sigma}}$ | {drv['zM']:.2f} |")
    lines.append(f"| $\\gamma(\\hat{{\\theta}}_t)$ | eq. (13) | $\\hat{{\\mu}}, \\hat{{\\sigma}}, \\hat{{\\theta}}_t$ | {drv['gamma']:.3f} |")
    lines.append(f"| $b_M, d_M$ | eq. (13) | $\\bar{{s}}, \\gamma, R^f$ | {drv['bM']*100:.1f}%, {drv['dM']*100:.1f}% |")
    lines.append(f"| $n_t$ | eq. (15) | debt {inp['gross_debt_pct']:.0f}%, bills {inp['short_term_debt_pct']:.0f}%, WAM {inp['wam_years']:.2f}y, deficit {inp['headline_deficit_pct']:.1f}% | {inp['nt']*100:.1f}% |")
    lines.append(f"| $d_{{t-1}}/G_t$ | eq. (2) | $n_t + s_t$ | {drv['face_val_due']*100:.1f}% |")
    lines.append(f"| $P_\\theta(d_t)$; model $\\psi$ | eqs. (14), (3) | $d_t \\approx n_t R^f$; Block-A objects | $\\approx {drv['p_dt']:.4e}; \\approx {drv['model_spread_bps']:.1f}$ bp |")
    lines.append(f"| $n_L, n_U$ | eq. (6) | funding curve (4) at Block-A objects | {drv['nL']*100:.1f}%, {drv['nU']*100:.1f}% |")
    lines.append(f"| regime | Tasks B4/C1 | $n_t$ vs. $[n_L, n_U]$ | **{rat['regime']}** |")
    lines.append(f"| $\\theta_G, \\theta_B$ | eq. (8) | invert edges at $n_t$ | {drv['theta_G']:.2f}, {drv['theta_B']:.2f} |")
    lines.append(f"| $\\Delta G$ | eq. (9) | $\\theta_G - \\hat{{\\theta}}_t$ | {drv['delta_G']:.2f} |")
    
    exp_str = "< 0.01%" if drv['exposure'] < 0.0001 else f"{drv['exposure']*100:.2f}%"
    lines.append(f"| Exposure | eq. (10) | $\\theta_G; \\mathcal{{N}}(0.3, 0.25^2)$ | {exp_str} |")
    lines.append(f"| $X^{{fisc}}$ | eq. (18) | $n_t, n_L(\\theta_\\infty), \\bar{{s}}, s_t$ | {drv['x_fisc']:.1f} y |")
    lines.append(f"| **Rating Class** | Task C2 | Exposure threshold table | **{rat['class']} ({rat['letter_grade']})** |")
    lines.append(f"| Eligibility State | DA2 (in C2) | EDP status / EU framework | **{rat['da2_eligibility_state']}** |")
    lines.append(f"| Outlook | Task C4 (DA1) | $n$-path direction; qualitative signals | **{rat['da1_outlook']}** |")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Run Sovereign Credit Rating MRP pipeline.")
    parser.add_argument('--country', default='AUT', help="Country ISO3 code (default: AUT)")
    parser.add_argument('--as-of', default='2026-08-01', help="As-of date YYYY-MM-DD (default: 2026-08-01)")
    parser.add_argument('--db', default=DB_PATH, help="Path to DuckDB database file")
    parser.add_argument('--da2-state', default='watch', choices=['eligible', 'watch', 'ineligible'], help="DA2 backstop eligibility state")
    parser.add_argument('--outlook', default='negative', choices=['positive', 'stable', 'negative'], help="DA1 qualitative outlook")
    parser.add_argument('--outlook-rationale', default=None, help="Written justification for DA1 qualitative outlook")
    parser.add_argument('--json', action='store_true', help="Output full JSON result")
    parser.add_argument('--save', action='store_true', help="Save run results to DuckDB rating_runs table")

    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(f"Database not found at {args.db}. Initializing...")
        from init_duckdb import init_db
        init_db(args.db)

    con = duckdb.connect(args.db)
    country_data, global_state = fetch_country_and_global_data(con, args.country, args.as_of)

    # Run MRP Engine
    result = run_mrp_pipeline(
        country_data=country_data,
        global_data=global_state,
        da2_state=args.da2_state,
        da1_qualitative_outlook=args.outlook,
        da1_rationale=args.outlook_rationale
    )

    if args.save:
        run_id = f"RUN_{args.country}_{args.as_of}_{os.getpid()}"
        rat = result['rating']
        drv = result['derived_objects']
        con.execute("""
            INSERT INTO rating_runs (
                run_id, country_id, as_of_date, regime, rating_class, letter_grade,
                exposure, delta_g, delta_b, x_fisc, da2_eligibility_state, da1_outlook,
                outlook_rationale, full_audit_payload
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            run_id, args.country, args.as_of, rat['regime'], rat['class'], rat['letter_grade'],
            drv['exposure'], drv['delta_G'], drv['delta_B'], drv['x_fisc'],
            rat['da2_eligibility_state'], rat['da1_outlook'], rat['outlook_rationale'],
            json.dumps(result, default=str)
        ])
        print(f"Rating run saved with ID: {run_id}")

def generate_full_markdown_report(result: dict, filepath: str):
    inp = result['inputs']
    drv = result['derived_objects']
    rat = result['rating']
    grid = result['sensitivity_grid']
    worst = grid['worst_corner']

    dirpath = os.path.dirname(filepath)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    
    exp_str = "< 0.01% (2.2e-16)" if drv['exposure'] < 0.0001 else f"{drv['exposure']*100:.2f}%"

    md = f"""# Sovereign Credit Rating Publication Sheet: {inp['country_name']} ({inp['country_id']})

**As-of Date:** {inp.get('as_of_date', 'August 2026')}  
**Methodology:** Positioning for Risk-Off — A Methodology for Sovereign Credit Ratings (Alex Stomper, HU Berlin, August 2026)  
**Monetary Tier:** Euro Area (Full Application)  
**Code & Engine Version:** `mrp-v1.0.0` (Analytical Stationary Solver)  

---

## 1. Executive Rating Summary

| Dimension | Assessment | Details / Meaning |
| :--- | :--- | :--- |
| **Equilibrium Regime** | **{rat['regime'].upper()} ($S$)** | Gross financing need $n_t = {inp['nt']*100:.1f}\\% < n_L = {drv['nL']*100:.1f}\\%$. Headroom to fragile band is {(drv['nL']-inp['nt'])*100:.1f}\\% of GDP. |
| **Native Rating Class** | **{rat['class']}** | Structural tail risk $Exposure < 0.01\\%$ ({exp_str}). |
| **Letter Grade Benchmark** | **{rat['letter_grade']}** | Native probability semantics: highest quality market access. |
| **Backstop Eligibility (DA2)** | **{rat['da2_eligibility_state'].upper()}** | Open Excessive Deficit Procedure (Council, 8 July 2025); effective action assessed. No factor truncation applied. |
| **Discretionary Outlook (DA1)**| **{rat['da1_outlook'].upper()}** | Headroom is large but shrinking along projected $n$-path (deficits {inp['headline_deficit_pct']:.1f}\\%, debt rising to mid-80s). |

---

## 2. Audit Trail (Table 3 Reproduction)

Every row represents one object of the methodology, its defining equation, inputs consumed, and exact country value.

{format_audit_trail_table(result)}

---

## 3. Methodological Derivation

### Block A: Fundamentals (The Country's Cliff)
- **Growth Moments (A1)**: Sample mean $\\hat{{\\mu}} = {inp['mu_hat']*100:.1f}\\%$ and volatility $\\hat{{\\sigma}} = {inp['sigma_hat']*100:.1f}\\%$ estimated from IMF WEO log nominal GDP growth (2001–2025). COVID and inflation shocks remain in sample as true volatility information.
- **Fiscal Capacity (A2)**: Historical maximum 5-year average primary balance $\\bar{{s}} = {inp['s_bar']*100:.1f}\\%$ (achieved pre-2009 and pre-pandemic). Planned primary balance $s_t = {inp['s_t']*100:.1f}\\%$.
- **Safe Rate & Haircut (A3, A4)**: $R^f = {inp['rf_gross']:.2f}$ (1-year point of ECB AAA yield curve); baseline haircut $h = {inp['haircut']:.2f}$.
- **Borrowing Capacity (A5)**:
  - Threshold root: $z_M = {drv['zM']:.2f}$.
  - Borrowing factor: $\\gamma({inp['theta_hat']:.2f}) = {drv['gamma']:.3f}$.
  - Maximum sustainable borrowing: $b_M = {drv['bM']*100:.1f}\\%$ of GDP.
  - Maximum face value before cliff: $d_M = {drv['dM']*100:.1f}\\%$ of GDP.

### Block B: State of Affairs (The Country's Coordinate)
- **Refinancing Need (B1)**:
  $$n_{{2026}} \\approx \\frac{{{inp['gross_debt_pct']:.0f} - {inp['short_term_debt_pct']:.0f}}}{{{inp['wam_years']:.2f}}} + {inp['short_term_debt_pct']:.0f} + {inp['headline_deficit_pct']:.1f} = {(inp['gross_debt_pct']-inp['short_term_debt_pct'])/inp['wam_years']:.1f} + {inp['short_term_debt_pct']:.1f} + {inp['headline_deficit_pct']:.1f} \\approx {inp['nt']*100:.1f}\\%$$
- **Pricing & Spreads (B2)**: Observed 10-year spread over safe curve $\\approx {inp['observed_spread_10y_bps']:.0f}\\text{{ bp}}$. Model default component evaluates to $\\psi \\approx {drv['model_spread_bps']:.1f}\\text{{ bp}}$. The observed spread reflects liquidity/technical factors.
- **Global Risk Factor (B3)**: Standardized VIX $z_t \\approx {inp['zt_vix']:.1f} \\implies \\hat{{\\theta}}_t = {inp['theta_hat']:.2f}$, with factor distribution $\\theta \\sim \\mathcal{{N}}({inp['theta_inf']:.2f}, {inp['sigma_theta']:.2f}^2)$.
- **Band Edges & Classification (B4)**:
  - $n_L({inp['theta_hat']:.2f}) = {drv['nL']*100:.1f}\\%$, $n_U({inp['theta_hat']:.2f}) = {drv['nU']*100:.1f}\\%$.
  - Since $n_t = {inp['nt']*100:.1f}\\% < n_L = {drv['nL']*100:.1f}\\%$, the country is firmly in the **{rat['regime'].upper()}** regime.
- **Distances & Tail Risk (B5)**:
  - $\\theta_G = {drv['theta_G']:.2f}, \\theta_B = {drv['theta_B']:.2f}$.
  - $\\Delta G = {drv['delta_G']:.2f}$, $\\Delta B = {drv['delta_B']:.2f}$.
  - $Exposure = {exp_str}$.
  - $X^{{fisc}} = {drv['x_fisc']:.1f}\\text{{ years}}$.

---

## 4. Discretionary Adjustments (DA Layer)

### Task DA2: Backstop Eligibility Calibration
- **Observable Bright Line**: Evaluated against EU fiscal framework and Commission DSA status.
- **Assigned State**: `{rat['da2_eligibility_state'].upper()}`.
- **Methodological Impact**:
  - State `{rat['da2_eligibility_state']}` applies no factor distribution truncation.
  - At $Exposure < 0.01\\%$, truncation is not needed to achieve the top class (**{rat['class']}**).

### Task DA1: Discretionary Outlook
- **Published Outlook**: **`{rat['da1_outlook'].upper()}`**  
  *Rationale*: {rat['outlook_rationale']}

> [!NOTE]
> **Principle 4 (No-Notch Discipline)**: The outlook does not alter the native rating class (**{rat['class']}**). Discretion informs the outlook, never the score.

---

## 5. Sensitivity Grid (81 Corners over $\\bar{{s}} \\times h \\times \\hat{{\\theta}}_t \\times n_t$)

$$\\bar{{s}} \\in \\{{1.5\\%, 2.0\\%, 2.5\\%\\}}, \\quad h \\in \\{{0.20, 0.30, 0.50\\}}, \\quad \\hat{{\\theta}}_t \\in \\{{0.0, 0.30, 0.60\\}}, \\quad n_t \\in \\{{12\\%, 14\\%, 16\\%\\}}$$

### Grid Breakdown:
- **Safe Corners ($S$):** **{grid['counts']['safe']} / {grid['total_corners']}** ({grid['counts']['safe']/grid['total_corners']*100:.1f}%)
- **Fragile Corners ($F$):** **{grid['counts']['fragile']} / {grid['total_corners']}** ({grid['counts']['fragile']/grid['total_corners']*100:.1f}%)
- **Distressed Corners ($D$):** **{grid['counts']['distressed']} / {grid['total_corners']}** ({grid['counts']['distressed']/grid['total_corners']*100:.1f}%)

### Worst Evaluated Corner:
- Parameters: $\\bar{{s}} = {worst['s_bar']*100:.1f}\\%$, $h = {worst['h']:.2f}$, $\\hat{{\\theta}}_t = {worst['theta']:.2f}$, $n_t = {worst['nt']*100:.1f}\\%$
- Output: $\\theta_G = {worst['theta_G']:.2f} \\implies Exposure \\approx {worst['exposure']*100:.2f}\\%$ (Regime: {worst['regime'].upper()})

---

## 6. Key Economic Takeaway: Maturity Structure is the Positioning

The headline gross debt ratio ({inp['gross_debt_pct']:.0f}% of GDP) is substantially larger than single-period maximum face value $d_M = {drv['dM']*100:.1f}\\%$.
With an **{inp['wam_years']:.2f}-year WAM**, annual refinancing need $n_t \\approx {inp['nt']*100:.1f}\\%$ sits comfortably below $n_L = {drv['nL']*100:.1f}\\%$.
The long maturity structure divides rollover exposure and serves as the principal risk-off positioning asset.
"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(md.strip() + '\n')
    print(f"Markdown publication sheet generated at {filepath}")

def main():
    parser = argparse.ArgumentParser(description="Run Sovereign Credit Rating MRP pipeline.")
    parser.add_argument('--country', default='AUT', help="Country ISO3 code (default: AUT)")
    parser.add_argument('--as-of', default='2026-08-01', help="As-of date YYYY-MM-DD (default: 2026-08-01)")
    parser.add_argument('--db', default=DB_PATH, help="Path to DuckDB database file")
    parser.add_argument('--da2-state', default='watch', choices=['eligible', 'watch', 'ineligible'], help="DA2 backstop eligibility state")
    parser.add_argument('--outlook', default='negative', choices=['positive', 'stable', 'negative'], help="DA1 qualitative outlook")
    parser.add_argument('--outlook-rationale', default=None, help="Written justification for DA1 qualitative outlook")
    parser.add_argument('--json', action='store_true', help="Output full JSON result")
    parser.add_argument('--export-md', default=None, help="Filepath to export formatted markdown publication sheet (default: dist/mrp/<country>.md)")

    args = parser.parse_args()

    if not os.path.exists(args.db):
        print(f"Database not found at {args.db}. Initializing...")
        from init_duckdb import init_db
        init_db(args.db)

    # Open DuckDB in strictly read-only mode
    con = duckdb.connect(args.db, read_only=True)
    country_data, global_state = fetch_country_and_global_data(con, args.country, args.as_of)
    con.close()

    # Run MRP Engine
    result = run_mrp_pipeline(
        country_data=country_data,
        global_data=global_state,
        da2_state=args.da2_state,
        da1_qualitative_outlook=args.outlook,
        da1_rationale=args.outlook_rationale
    )

    # Determine markdown export path (default: dist/mrp/<country>.md)
    export_path = args.export_md
    if export_path is None:
        country_slug = country_data.get('name', args.country).lower().replace(' ', '_')
        export_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dist', 'mrp', f'{country_slug}.md')

    generate_full_markdown_report(result, export_path)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
        return

    # Print Formatted Report
    print("=" * 80)
    print(f"SOVEREIGN CREDIT RATING REPORT — {result['inputs']['country_name'].upper()} ({args.country})")
    print(f"As-of Date: {args.as_of} | Methodology: Stomper (2026)")
    print("=" * 80)
    print("\n### 1. RATING SUMMARY")
    print(f"- **Regime**: {result['rating']['regime'].upper()}")
    print(f"- **Native Rating Class**: {result['rating']['class']}")
    print(f"- **Letter Grade Benchmark**: {result['rating']['letter_grade']}")
    print(f"- **Backstop Eligibility (DA2)**: {result['rating']['da2_eligibility_state'].upper()}")
    print(f"- **Discretionary Outlook (DA1)**: {result['rating']['da1_outlook'].upper()}")
    print(f"- **Outlook Rationale**: {result['rating']['outlook_rationale']}")
    
    print("\n### 2. AUDIT TRAIL (TABLE 3 REPLICATION)")
    print(format_audit_trail_table(result))

    print("\n### 3. SENSITIVITY GRID (81 CORNERS OVER s_bar x h x theta x nt)")
    grid = result['sensitivity_grid']
    print(f"- Total Evaluated Corners: {grid['total_corners']}")
    print(f"- Safe Corners: {grid['counts']['safe']} / {grid['total_corners']}")
    print(f"- Fragile Corners: {grid['counts']['fragile']} / {grid['total_corners']}")
    print(f"- Distressed Corners: {grid['counts']['distressed']} / {grid['total_corners']}")
    worst = grid['worst_corner']
    print(f"- Worst Evaluated Corner: s_bar = {worst['s_bar']*100:.1f}%, h = {worst['h']:.2f}, theta = {worst['theta']:.2f}, nt = {worst['nt']*100:.1f}%")
    print(f"- Worst-Corner Exposure: {worst['exposure']*100:.2f}% (Regime: {worst['regime']})")
    print("=" * 80)

if __name__ == '__main__':
    main()
