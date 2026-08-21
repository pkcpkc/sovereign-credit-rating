# Rating Engine & Script Architecture (MRP v1.0)

This document describes the design and implementation of the Python calculation engine (`src/mrp/engine.py`) and CLI script (`scripts/run_rating.py`) for the Minimal Rating Process (MRP v1.0).

---

## 1. Codebase Structure

```
sovereign-credit-rating/
├── data/
│   └── sovereign_ratings.duckdb       # DuckDB read-only input store
├── src/
│   └── mrp/
│       ├── __init__.py
│       └── engine.py                  # Core MRP mathematical equations & analytical solvers
├── scripts/
│   ├── init_duckdb.py                 # Pure DDL table initialization script
│   ├── insert_austria.py              # Dedicated Austria data ingestion / seed script
│   └── run_rating.py                  # CLI runner for quantitative MRP evaluation
├── dist/
│   └── mrp/
│       ├── austria.md                 # Generated publication sheet (markdown)
│       └── austria.pdf                # Generated publication sheet (PDF)
└── docs/
    ├── mrp-skill.md                   # Skill documentation (MRP v1.0)
    ├── duckdb-schema.md               # DuckDB schema specification
    ├── how-to.md                      # Quickstart guide
    └── rating-engine-script.md        # Engine and script details (this file)
```

---

## 2. Mathematical Solver & Optimization Details

The funding curve is given by Eq. (5):
$$\xi_\theta(d) = \frac{d (1 - h P_\theta(d))}{R^f}$$
where:
$$P_\theta(d) = \Phi\left(\frac{\ln d - \ln(\bar{s} + b_M(\theta)) - (\mu - \theta \sigma)}{\sigma}\right)$$

### Stationary Points Analytical Transformation
Stationary points of the funding curve satisfy $\xi'_\theta(d) = 0$:
$$1 - h P_\theta(d) - h d P'_\theta(d) = 0$$
Using the substitution $z = \frac{\ln d - \ln(\bar{s} + b_M(\theta)) - (\mu - \theta \sigma)}{\sigma}$, the stationary condition simplifies to:
$$1 - h \Phi(z) - \frac{h}{\sigma} \phi(z) = 0$$

> [!TIP]
> **Performance Optimization**: This equation depends **only on $(h, \sigma)$** and is independent of $(\mu, \theta, \bar{s}, R^f)$!
> This allows solving for the two stationary roots $z_U < z_L$ instantly via Brent's method (`scipy.optimize.brentq`), after which:
> $$d_U(\theta) = (\bar{s} + b_M(\theta)) \exp(\mu - \theta \sigma + \sigma z_U)$$
> $$d_L(\theta) = (\bar{s} + b_M(\theta)) \exp(\mu - \theta \sigma + \sigma z_L)$$
> $$n_U(\theta) = \frac{d_U(\theta) (1 - h \Phi(z_U))}{R^f}, \quad n_L(\theta) = \frac{d_L(\theta) (1 - h \Phi(z_L))}{R^f}$$
> This closed-form representation evaluates the entire 81-corner sensitivity grid in **under 10 milliseconds**.

---

## 3. Function Reference in `src/mrp/engine.py`

### Calibration Tasks (C1–C6)
- **`calibrate_inflation_differential(mu_r, pi_u, e_hat=0.0) -> (e_hat, e_mrp, mu)`**:
  Implements Task C2: $e_{\text{MRP}} = \min\{0, \hat{e}_t\}$ and $\hat{\mu} = \hat{\mu}_r + \hat{\pi}^u + e_{\text{MRP}}$.
- **`compute_inflation_capacity_derivative(gamma, s_bar, Rf) -> float`**:
  Evaluates $\frac{\partial b_M}{\partial e} = \frac{\gamma \bar{s} R^f}{(R^f - \gamma)^2}$ (capacity lost per 100bp of inflation differential).

### Rating Tasks (R1–R7)
- **`compute_refinancing_need(debt_stock_pct, short_term_debt_pct, wam_years, deficit_pct) -> float`**:
  Implements Task R1: $n_t \approx \frac{d^{stock} - b^{ST}}{\text{WAM}} + b^{ST} + def$.
- **`estimate_distress_risk_price(vix_monthly, mV=2.70, sV=0.40, theta_inf=0.30, sigma_theta=0.25) -> (zt, theta_hat)`**:
  Implements Task R2: $z_t = (\ln V_t - m_V)/s_V \implies \hat{\theta}_t = \max\{0, \theta_\infty + \sigma_\theta z_t\}$.
- **`solve_zM(sigma: float) -> float`**:
  Solves $\sigma(1 - \Phi(z_M)) = \phi(z_M)$ for the unique negative threshold root $z_M$.
- **`compute_capacity_objects(mu, sigma, s_bar, Rf, theta, zM=None) -> (zM, gamma, bM, dM)`**:
  Implements Task R3: $\gamma(\theta), b_M(\theta), d_M(\theta)$.
- **`compute_band_edges(mu, sigma, s_bar, Rf, h, theta, zM=None) -> (dU, dL, nL, nU)`**:
  Implements Task R4: stationary points $d_U < d_L$ and band edges $n_L(\theta), n_U(\theta)$.
- **`solve_critical_risk_prices(nt, mu, sigma, s_bar, Rf, h, zM=None) -> (theta_G, theta_B)`**:
  Implements Task R5: solves $n_U(\theta_G) = n_t$ and $n_L(\theta_B) = n_t$.
- **`classify_rating(regime, exposure, x_fisc, p_theta_B=None, d3_flag=False, branch='good') -> (class, letter_grade)`**:
  Implements Task R6: native thresholds with probability semantics (S1-S3, F1-F4, D1-D3) under No-Notch discipline.
- **`compute_sensitivity_grid(...) -> Dict[str, Any]`**:
  Implements Task R7: evaluates all 81 parameter corners $(\bar{s} \times h \times \hat{\theta}_t \times n_t)$.
- **`run_mrp_pipeline(country_data, global_data, da2_state='watch', da1_qualitative_outlook=None, da1_rationale=None) -> Dict[str, Any]`**:
  Main orchestrator returning complete MRP specification v1.0 payload.

---

## 4. CLI Runner (`scripts/run_rating.py`)

### Usage:
```bash
./.venv/bin/python scripts/run_rating.py \
  --country AUT \
  --as-of 2026-08-01 \
  --da2-state watch \
  --outlook negative \
  --outlook-rationale "Projected n-path expansion from deficits + EDP watch state." \
  --export-md dist/mrp/austria.md
```
