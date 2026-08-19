# Rating Engine & Script Architecture

This document describes the design and implementation of the Python calculation engine (`src/mrp/engine.py`) and CLI script (`scripts/run_rating.py`) for the Sovereign Credit Rating Minimal Rating Process (MRP).

---

## 1. Codebase Structure

```
sovereign-credit-rating/
├── data/
│   └── sovereign_ratings.duckdb       # DuckDB persistent database
├── src/
│   └── mrp/
│       ├── __init__.py
│       └── engine.py                  # Core MRP mathematical equations & solvers
├── scripts/
│   ├── init_duckdb.py                 # DB schema initialization & seed script
│   └── run_rating.py                  # CLI runner for quantitative evaluation
└── docs/
    ├── mrp-skill.md                   # Skill documentation
    ├── duckdb-schema.md               # DuckDB schema specification
    └── rating-engine-script.md        # Engine and script details (this file)
```

---

## 2. Mathematical Solver & Optimization Details

The funding curve is given by:
$$\xi_\theta(d) = \frac{d (1 - h P_\theta(d))}{R^f}$$
where:
$$P_\theta(d) = \Phi\left(\frac{\ln d - \ln(\bar{s} + b_M(\theta)) - (\mu - \theta \sigma)}{\sigma}\right)$$

### Stationary Points Analytical Transformation
Stationary points of the funding curve satisfy $\xi'_\theta(d) = 0$:
$$1 - h P_\theta(d) - h d P'_\theta(d) = 0$$
Using the substitution $z = \frac{\ln d - \ln(\bar{s} + b_M(\theta)) - (\mu - \theta \sigma)}{\sigma}$, the stationary condition simplifies to:
$$1 - h \Phi(z) - \frac{h}{\sigma} \phi(z) = 0$$

> [!TIP]
> **Performance Optimization**: Notice that this equation depends **only on $(h, \sigma)$** and is independent of $(\mu, \theta, \bar{s}, R^f)$!
> This allows solving for the two stationary roots $z_U < z_L$ instantly via Brent's method (`scipy.optimize.brentq`), after which:
> $$d_U(\theta) = (\bar{s} + b_M(\theta)) \exp(\mu - \theta \sigma + \sigma z_U)$$
> $$d_L(\theta) = (\bar{s} + b_M(\theta)) \exp(\mu - \theta \sigma + \sigma z_L)$$
> $$n_U(\theta) = \frac{d_U(\theta) (1 - h \Phi(z_U))}{R^f}, \quad n_L(\theta) = \frac{d_L(\theta) (1 - h \Phi(z_L))}{R^f}$$
> This closed-form representation reduces the solve time of the entire 81-corner sensitivity grid from seconds to **under 10 milliseconds**.

---

## 3. Function Reference in `src/mrp/engine.py`

### `solve_zM(sigma: float) -> float`
Solves $\sigma(1 - \Phi(z_M)) = \phi(z_M)$ for the unique negative threshold root $z_M$.

### `compute_capacity_objects(mu, sigma, s_bar, Rf, theta, zM=None) -> (zM, gamma, bM, dM)`
Computes:
- $\gamma(\theta) = (1 - \Phi(z_M)) e^{\mu - \theta \sigma + \sigma z_M}$
- $b_M(\theta) = \frac{\bar{s} \gamma(\theta)}{R^f - \gamma(\theta)}$
- $d_M(\theta) = (\bar{s} + b_M(\theta)) e^{\mu - \theta \sigma + \sigma z_M}$

### `compute_band_edges(mu, sigma, s_bar, Rf, h, theta, zM=None) -> (dU, dL, nL, nU)`
Computes the two interior stationary points $d_U < d_L$ and corresponding proceeds $n_L(\theta), n_U(\theta)$.

### `solve_critical_risk_prices(nt, mu, sigma, s_bar, Rf, h, zM=None) -> (theta_G, theta_B)`
Solves for critical risk prices where band edges equal the refinancing need $n_t$:
- $\theta_G(n_t): n_U(\theta_G) = n_t$
- $\theta_B(n_t): n_L(\theta_B) = n_t$

### `compute_sensitivity_grid(...) -> Dict[str, Any]`
Evaluates the 81-corner sensitivity grid over:
- $\bar{s} \in \{1.5\%, 2.0\%, 2.5\%\}$
- $h \in \{0.20, 0.30, 0.50\}$
- $\hat{\theta}_t \in \{0.0, 0.30, 0.60\}$
- $n_t \in \{12\%, 14\%, 16\%\}$

Returns safe/fragile/distressed counts and worst-corner coordinates.

---

## 4. CLI Runner: `scripts/run_rating.py`

### Command-Line Arguments

| Flag | Default | Description |
| :--- | :--- | :--- |
| `--country` | `AUT` | ISO-3 country identifier |
| `--as-of` | `2026-08-01` | As-of date (`YYYY-MM-DD`) |
| `--db` | `data/sovereign_ratings.duckdb` | Path to DuckDB file |
| `--da2-state` | `watch` | Backstop eligibility state (`eligible`, `watch`, `ineligible`) |
| `--outlook` | `negative` | Qualitative discretionary outlook (`positive`, `stable`, `negative`) |
| `--outlook-rationale` | `None` | Written justification for outlook |
| `--json` | `False` | Output structured JSON response |
| `--save` | `False` | Persist rating run to `rating_runs` table |

### Example CLI Invocations

```bash
# Standard publication run
./.venv/bin/python scripts/run_rating.py --country AUT --as-of 2026-08-01 --save

# Structured JSON for agent integrations
./.venv/bin/python scripts/run_rating.py --country AUT --as-of 2026-08-01 --json
```

---

## 5. Audit Trail Verification (Table 3 Reproduction)

When run on the Austria baseline dataset, `scripts/run_rating.py` reproduces Table 3 of Stomper (2026) exactly:

| Object | Defined in | Inputs (source) | Country Value |
| :--- | :--- | :--- | :--- |
| $\hat{\mu}, \hat{\sigma}$ | eq. (11) | WEO nominal GDP, 2001–2025 | 3.4%, 3.0% |
| $\bar{s}$ | eq. (12) | WEO/FM primary balances | 2.0% |
| $R^f$ | Task A3 | ECB AAA curve, 1y point | 1.02 |
| $h$ | Task A4 | Cruces–Trebesch center | 0.30 |
| $z_t; \hat{\theta}_t$ | eqs. (16), (17) | VIX monthly avg. vs. 20y history | $\approx 0.0; 0.30$ |
| $z_M$ | eq. (13) | $\hat{\sigma}$ | -2.28 |
| $\gamma(\hat{\theta}_t)$ | eq. (13) | $\hat{\mu}, \hat{\sigma}, \hat{\theta}_t$ | 0.947 |
| $b_M, d_M$ | eq. (13) | $\bar{s}, \gamma, R^f$ | 25.8%, 26.7% |
| $n_t$ | eq. (15) | debt 81%, bills 2%, WAM 11.45y, deficit 4.3% | 14.0% |
| $d_{t-1}/G_t$ | eq. (2) | $n_t + s_t$ | 11.6% |
| $P_\theta(d_t)$; model $\psi$ | eqs. (14), (3) | $d_t \approx n_t R^f$; Block-A objects | $\approx 0; \approx 0.0$ bp |
| $n_L, n_U$ | eq. (6) | funding curve (4) at Block-A objects | 21.0%, 26.2% |
| regime | Tasks B4/C1 | $n_t$ vs. $[n_L, n_U]$ | **safe** |
| $\theta_G, \theta_B$ | eq. (8) | invert edges at $n_t$ | 2.33, 1.47 |
| $\Delta G$ | eq. (9) | $\theta_G - \hat{\theta}_t$ | 2.03 |
| Exposure | eq. (10) | $\theta_G; \mathcal{N}(0.3, 0.25^2)$ | < 0.01% |
| $X^{fisc}$ | eq. (18) | $n_t, n_L(\theta_\infty), \bar{s}, s_t$ | 0.0 y |
| **Rating Class** | Task C2 | Exposure threshold table | **S1 (AAA/AA+)** |
| Eligibility State | DA2 (in C2) | EDP status / EU framework | **watch** |
| Outlook | Task C4 (DA1) | $n$-path direction; qualitative signals | **negative** |
