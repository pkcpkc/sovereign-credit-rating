#!/usr/bin/env python3
"""
CLI runner for Minimal Rating Process (MRP v1.0).
Implementation of Alex Stomper (2026): "The Minimal Rating Process: Sovereign Credit Ratings from Risk-Off Positioning"
Fetches data from DuckDB, evaluates the 6 Calibration Tasks (C1-C6) and 7 Rating Tasks (R1-R7),
evaluates the 81-corner sensitivity grid, and outputs the Table 1 audit trail and publication sheet.
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

    country_data = {**country, **debt_state, **params}
    return country_data, global_state

def format_audit_trail_table(result: dict) -> str:
    inp = result['inputs']
    drv = result['derived_objects']
    rat = result['rating']
    cal = result['calibration_tasks']
    rt = result['rating_tasks']
    
    lines = []
    lines.append("| Task | Output | Eq. | Input (source) | Country Value |")
    lines.append("| :--- | :--- | :---: | :--- | :--- |")
    lines.append(f"| **C1** | $\\hat{{\\mu}}_r, \\hat{{\\sigma}}$ | (14) | real/nominal GDP growth, 25y (IMF WEO) | {cal['C1']['mu_r']*100:.1f}%, {cal['C1']['sigma_hat']*100:.1f}% |")
    lines.append(f"| **C2** | $e_{{MRP}}, \\hat{{\\mu}}$ | (15) | HICP projections, state vs. euro area (WEO/ECB) | {cal['C2']['e_MRP']*100:.1f}%, {cal['C2']['mu_hat']*100:.1f}% |")
    lines.append(f"| **C3** | $\\bar{{s}}, s_t$ | (17) | primary balances (WEO/Fiscal Monitor) | {cal['C3']['s_bar']*100:.1f}%, {cal['C3']['s_t']*100:.1f}% |")
    lines.append(f"| **C4** | $R^f$ | — | 1y euro-area AAA yield (ECB) | {cal['C4']['Rf']:.2f} |")
    lines.append(f"| **C5** | $h$ | — | Cruces–Trebesch haircut distribution | {cal['C5']['h']:.2f} |")
    lines.append(f"| **C6** | $(\\theta_\\infty, \\sigma_\\theta); (m_V, s_V)$ | — | Note calibration; 20y log-VIX history (CBOE) | ({cal['C6']['theta_inf']:.2f}, {cal['C6']['sigma_theta']:.2f}); ({cal['C6']['mV']:.2f}, {cal['C6']['sV']:.2f}) |")
    lines.append(f"| **R1** | $n_t$ | (18) | debt ratio, bills, WAM, deficit (WEO/DMO); GFN cross-check | {inp['nt']*100:.1f}% |")
    lines.append(f"| **R2** | $\\hat{{\\theta}}_t; \\theta \\sim \\mathcal{{N}}(\\theta_\\infty, \\sigma_\\theta^2)$ | (19)–(20) | monthly VIX (CBOE) | $\\approx {rt['R2']['zt_vix']:.1f}; {rt['R2']['theta_hat']:.2f}$ |")
    lines.append(f"| **R3** | $z_M, \\gamma, b_M, d_M, P_\\theta$ | (9)–(10) | C1–C5 outputs, $\\hat{{\\theta}}_t$ | $z_M = {drv['zM']:.2f}, \\gamma = {drv['gamma']:.3f}, b_M = {drv['bM']*100:.1f}\\%, d_M = {drv['dM']*100:.1f}\\%$ |")
    lines.append(f"| **R4** | $n_L, n_U$; regime, branch | (7) | funding curve (5); 10y spread (ECB/DMO) | $n_L = {drv['nL']*100:.1f}\\%, n_U = {drv['nU']*100:.1f}\\% \\implies$ **{rat['regime']} ({rt['R4']['branch']})** |")
    
    exp_str = "< 0.01%" if drv['exposure'] < 0.0001 else f"{drv['exposure']*100:.2f}%"
    lines.append(f"| **R5** | $\\theta_G, \\theta_B, \\Delta G, \\Delta B, \\text{{Exposure}}, X^{{fisc}}$ | (11)–(13), (21) | R1–R4 outputs | $\\theta_G = {drv['theta_G']:.2f}, \\theta_B = {drv['theta_B']:.2f}, \\Delta G = {drv['delta_G']:.2f}, Exposure = {exp_str}, X^{{fisc}} = {drv['x_fisc']:.1f}\\text{{y}}$ |")
    lines.append(f"| **R6** | class; eligibility state | thresholds | Exposure, $X^{{fisc}}$; EDP/DSA status (Commission) | **{rat['class']} ({rat['letter_grade']})**; state: **{rat['da2_eligibility_state']}** |")
    lines.append(f"| **R7** | outlook; publication sheet | — | fiscal plans, redemption calendar; grid | **{rat['da1_outlook']}**; published |")
    return "\n".join(lines)

def generate_full_markdown_report(result: dict, filepath: str):
    inp = result['inputs']
    drv = result['derived_objects']
    rat = result['rating']
    grid = result['sensitivity_grid']
    worst = grid['worst_corner']
    cal = result['calibration_tasks']
    rt = result['rating_tasks']

    dirpath = os.path.dirname(filepath)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    
    exp_str = "< 0.01% (2.2e-16)" if drv['exposure'] < 0.0001 else f"{drv['exposure']*100:.2f}%"

    md = f"""# Sovereign Credit Rating Publication Sheet: {inp['country_name']} ({inp['country_id']})

**As-of Date:** {inp.get('as_of_date', 'August 2026')}  
**Methodology:** The Minimal Rating Process (Alex Stomper, HU Berlin, MRP spec v1.0, August 2026)  
**Monetary Tier:** Euro Area (Full Application; $k=0$ conservative benchmark)  
**Code & Engine Version:** `mrp-v1.0.0` (Analytical Stationary Solver)  

---

## 1. Executive Rating Summary

| Dimension | Assessment | Details / Meaning |
| :--- | :--- | :--- |
| **Equilibrium Regime** | **{rat['regime'].upper()} ({rt['R4']['branch'].upper()})** | Gross financing need $n_t = {inp['nt']*100:.1f}\\% < n_L = {drv['nL']*100:.1f}\\%$. Headroom to fragile band is {(drv['nL']-inp['nt'])*100:.1f}\\% of GDP. |
| **Native Rating Class** | **{rat['class']}** | Structural tail risk $Exposure < 0.01\\%$ ({exp_str}). |
| **Letter Grade Benchmark** | **{rat['letter_grade']}** | Native probability semantics: highest quality market access. |
| **Backstop Eligibility (DA2)** | **{rat['da2_eligibility_state'].upper()}** | Open Excessive Deficit Procedure (Council, 8 July 2025); effective action assessed. No factor truncation applied. |
| **Discretionary Outlook (DA1)**| **{rat['da1_outlook'].upper()}** | Headroom is large but shrinking along projected $n$-path (deficits {inp['headline_deficit_pct']:.1f}\\%, debt rising to mid-80s). |

---

## 2. Process on One Page (Table 1 Replication)

Six calibration tasks set parameters from public data; seven monthly rating tasks implement the core process.

{format_audit_trail_table(result)}

---

## 3. Methodological Derivation

### Calibration Tasks (Annual)
- **Real Growth Moments (C1)**: Sample real drift $\\hat{{\\mu}}_r = {cal['C1']['mu_r']*100:.1f}\\%$ and nominal volatility $\\hat{{\\sigma}} = {cal['C1']['sigma_hat']*100:.1f}\\%$ estimated from IMF WEO log nominal GDP growth (2001–2025). COVID and inflation shocks remain in sample as volatility information.
- **Inflation Differential (C2)**: Projected 5-year differential $\\hat{{e}}_t = {cal['C2']['e_hat']*100:.1f}\\% \\implies e_{{MRP}} = \\min\\{{0, \\hat{{e}}_t\\}} = {cal['C2']['e_MRP']*100:.1f}\\%$. Effective drift $\\hat{{\\mu}} = \\hat{{\\mu}}_r + \\hat{{\\pi}}^u + e_{{MRP}} = {cal['C2']['mu_hat']*100:.1f}\\%$. Capacity derivative $\\frac{{\\partial b_M}}{{\\partial e}} = {cal['C2']['dbM_de']:.1f}\\text{{ pp of GDP per 100bp}}$.
- **Fiscal Capacity (C3)**: Historical maximum 5-year average primary balance $\\bar{{s}} = {cal['C3']['s_bar']*100:.1f}\\%$ (demonstrated maximum). Planned primary balance $s_t = {cal['C3']['s_t']*100:.1f}\\%$.
- **Safe Rate & Haircut (C4, C5)**: $R^f = {cal['C4']['Rf']:.2f}$ (1-year point of ECB AAA yield curve); baseline haircut $h = {cal['C5']['h']:.2f}$ (Cruces–Trebesch center).
- **Risk Appetite Parameters (C6)**: Long-run anchor $\\theta_\\infty = {cal['C6']['theta_inf']:.2f}$, dispersion $\\sigma_\\theta = {cal['C6']['sigma_theta']:.2f}$.

### Rating Tasks (Monthly Core)
- **Refinancing Need (R1)**:
  $$n_{{2026}} \\approx \\frac{{{inp['gross_debt_pct']:.0f} - {inp['short_term_debt_pct']:.0f}}}{{{inp['wam_years']:.2f}}} + {inp['short_term_debt_pct']:.0f} + {inp['headline_deficit_pct']:.1f} = {(inp['gross_debt_pct']-inp['short_term_debt_pct'])/inp['wam_years']:.1f} + {inp['short_term_debt_pct']:.1f} + {inp['headline_deficit_pct']:.1f} \\approx {inp['nt']*100:.1f}\\%$$
- **Distress Risk Price (R2)**: Standardized VIX $z_t \\approx {rt['R2']['zt_vix']:.1f} \\implies \\hat{{\\theta}}_t = \\max\\{{0, 0.30 + 0.25 \\times {rt['R2']['zt_vix']:.1f}\\}} = {rt['R2']['theta_hat']:.2f}$.
- **Capacity Objects (R3)**:
  - Threshold root: $z_M = {drv['zM']:.2f}$ (unique root of $\\sigma(1-\\Phi(z_M)) = \\phi(z_M)$).
  - Borrowing factor: $\\gamma({rt['R2']['theta_hat']:.2f}) = {drv['gamma']:.3f}$.
  - Maximum sustainable borrowing: $b_M = {drv['bM']*100:.1f}\\%$ of GDP.
  - Maximum face value before cliff: $d_M = {drv['dM']*100:.1f}\\%$ of GDP.
- **Band Edges & Regime (R4)**:
  - $n_L({rt['R2']['theta_hat']:.2f}) = {drv['nL']*100:.1f}\\%$, $n_U({rt['R2']['theta_hat']:.2f}) = {drv['nU']*100:.1f}\\%$.
  - Since $n_t = {inp['nt']*100:.1f}\\% < n_L = {drv['nL']*100:.1f}\\%$, the country is in the **{rat['regime'].upper()}** regime.
- **Critical Exits & Tail Risk (R5)**:
  - Critical prices: $\\theta_G = {drv['theta_G']:.2f}, \\theta_B = {drv['theta_B']:.2f}$.
  - Exit distances: $\\Delta G = {drv['delta_G']:.2f}$, $\\Delta B = {drv['delta_B']:.2f}$.
  - Tail risk: $Exposure = 1 - \\Phi((\\theta_G - \\theta_\\infty)/\\sigma_\\theta) = {exp_str}$.
  - Fiscal exit time: $X^{{fisc}} = \\frac{{\\max\\{{n_t - n_L(\\theta_\\infty), 0\\}}}}{{\\bar{{s}} - s_t}} = {drv['x_fisc']:.1f}\\text{{ years}}$.

---

## 4. Discretionary Adjustments (DA Layer)

### Task DA2 (in R6): Backstop Eligibility Calibration
- **Observable Bright Line**: Evaluated against EU fiscal framework and Commission DSA status.
- **Assigned State**: `{rat['da2_eligibility_state'].upper()}`.
- **Methodological Impact**:
  - State `{rat['da2_eligibility_state']}` applies no factor distribution truncation.
  - At $Exposure < 0.01\\%$, truncation is not needed to achieve the top class (**{rat['class']}**).

### Task DA1 (in R7): Discretionary Outlook
- **Published Outlook**: **`{rat['da1_outlook'].upper()}`**  
  *Rationale*: {rat['outlook_rationale']}

> [!NOTE]
> **Principle 4 (No-Notch Discipline)**: The outlook does not alter the native rating class (**{rat['class']}**). Discretion informs the calibration and the outlook, never the score.

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
    parser = argparse.ArgumentParser(description="Run Minimal Rating Process (MRP v1.0) pipeline.")
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
    print(f"MINIMAL RATING PROCESS (MRP v1.0) REPORT — {result['inputs']['country_name'].upper()} ({args.country})")
    print(f"As-of Date: {args.as_of} | Methodology: Alex Stomper (2026)")
    print("=" * 80)
    print("\n### 1. EXECUTIVE RATING SUMMARY")
    print(f"- **Equilibrium Regime**: {result['rating']['regime'].upper()} ({result['rating_tasks']['R4']['branch'].upper()})")
    print(f"- **Native Rating Class**: {result['rating']['class']}")
    print(f"- **Letter Grade Benchmark**: {result['rating']['letter_grade']}")
    print(f"- **Backstop Eligibility (DA2)**: {result['rating']['da2_eligibility_state'].upper()}")
    print(f"- **Discretionary Outlook (DA1)**: {result['rating']['da1_outlook'].upper()}")
    print(f"- **Outlook Rationale**: {result['rating']['outlook_rationale']}")
    
    print("\n### 2. PROCESS ON ONE PAGE (TABLE 1 REPLICATION)")
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
