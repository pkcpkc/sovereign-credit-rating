# Austria: Sovereign Rating Dataset from DuckDB

**Database File:** `data/sovereign_ratings.duckdb`  
**Country:** Austria (`AUT` / `AT`)  
**Valuation As-of Date:** August 1, 2026 (`2026-08-01`)  
**Methodological Standard:** Stomper (2026), *Positioning for Risk-Off*  

---

## 1. Sovereign Master Metadata (`countries`)

| Field | Value | Description |
| :--- | :--- | :--- |
| `country_id` | **`AUT`** | ISO-3 Primary Identifier |
| `name` | **Austria** | Official Country Name |
| `iso2` / `iso3` | **`AT` / `AUT`** | International ISO Standard Codes |
| `currency` | **`EUR`** | Sovereign Borrowing Currency |
| `monetary_tier` | **`euro_area`** | Monetary Union Member (Full application) |
| `has_backstop` | **`True`** | Backstop access (ECB/ESM conditional backstop) |
| `created_at` | `2026-08-17 13:58:14.436599` | Database Record Timestamp |

## 2. Calibrated Baseline Parameter Vector (`country_parameters`)

| Parameter | Symbol | Database Value | Formatted | Methodological Source |
| :--- | :--- | :--- | :--- | :--- |
| Growth Drift | $\hat{\mu}$ | **`0.0340`** | $3.4\%$ | Eq. (11): Sample mean of log nominal GDP growth (2001–2025) |
| Growth Volatility | $\hat{\sigma}$ | **`0.0300`** | $3.0\%$ | Eq. (11): Sample standard deviation of log nominal GDP growth |
| Fiscal Capacity | $\bar{s}$ | **`0.0200`** | $2.0\%$ of GDP | Eq. (12): Best sustained 5-year average primary balance |
| Gross Safe Rate | $R^f$ | **`1.0200`** | $1.020$ ($2.0\%$) | Task A3: 1-year point of ECB euro-area AAA yield curve |
| Restructuring Haircut | $h$ | **`0.30`** | $30.0\%$ | Task A4: Cruces–Trebesch restructuring distribution center |
| Factor Sensitivity Loading | $\beta_i$ | **`1.00`** | $1.00$ | Task B4+: Standard euro-area global factor loading |
| Source Citation | — | *Stomper (2026) Table 3 calibration* | — | Publication Table 3 calibration baseline |

## 3. State-of-Affairs Debt & Refinancing Profile (`country_debt_state`)

| Metric | Symbol | Value | Unit | Defining Equation / Public Source |
| :--- | :--- | :--- | :--- | :--- |
| Valuation As-of Date | $t$ | **`2026-08-01`** | Date | Monthly reporting date |
| Reference Year | — | **`2026`** | Year | Budget fiscal year |
| Gross Debt Ratio | $d^{stock}_{t-1}$ | **`81.0%`** | % of GDP | IMF WEO / Eurostat gross general government debt |
| Short-term Debt Stock | $b^{ST}_{t-1}$ | **`2.0%`** | % of GDP | OeBFA / Treasury bills (< 1 year maturity) |
| Weighted Average Maturity | $M_{t-1}$ (WAM) | **`11.45`** | Years | OeBFA investor information / OECD GDR |
| Headline Deficit | $def_t$ | **`4.3%`** | % of GDP | 2026 WEO / Maastricht general government deficit |
| Planned Primary Balance | $s_t$ | **`-2.4%`** | % of GDP | 2026 forecast primary balance (plan deficit) |
| Gross Financing Need | $n_t$ | **`14.0%`** | % of GDP | Eq. (15): $(81-2)/11.45 + 2 + 4.3 = 13.2\% \to 14.0\%$ baseline |
| 10-Year Benchmark Yield | $Y_{10y}$ | **`2.50%`** | % per annum | Austrian 10-year government bond yield |
| 10-Year Spread over Safe Curve | $\psi_t$ | **`50.0`** | Basis points | Spread over German/AAA benchmark curve |
| Domestic Bank Holdings Share | $\kappa$ | **`15.0%`** | % of debt | Share of sovereign debt held by domestic banks (< 25%) |
| Foreign Private Investor Share | — | **`35.0%`** | % of debt | IMF Arslanalp–Tsuda investor base dataset |
| Source Citation | — | *OeBFA / IMF Article IV / Eurostat* | — | Official Austrian Treasury / IMF compilation |

## 4. Global Market & Risk Appetite State (`global_market_state`)

| Object | Symbol | Value | Description |
| :--- | :--- | :--- | :--- |
| Observation Date | $t$ | **`2026-08-01`** | Valuation month |
| CBOE VIX Index Average | $V_t$ | **`15.5`** | Monthly average VIX level |
| 20-Year Standardized Log VIX | $z_t$ | **`0.00`** | Eq. (16): $(\ln V_t - m_V)/s_V \approx 0.0$ |
| Distress Risk Price Estimate | $\hat{\theta}_t$ | **`0.30`** | Eq. (17): $\max(0, \theta_\infty + \sigma_\theta z_t) = 0.30$ |
| Factor Long-Run Anchor | $\theta_\infty$ | **`0.30`** | LPPS conservative long-run risk price anchor |
| Factor Dispersion | $\sigma_\theta$ | **`0.25`** | Factor standard deviation in kernel units |
| Factor Persistence | $\rho_\theta$ | **`1.00`** | Conservative teaching default ($\rho_\theta = 1.0$) |
| Source | — | *CBOE VIX 20-year standardized history* | CBOE standardized history |

## 5. 25-Year Historical GDP Growth Series (`country_gdp_growth`)

Used in **Task A1** to estimate sample moments:
$$\hat{\mu} = \frac{1}{T}\sum_{t=1}^T \ln G_t = 0.0340 \quad (3.4\%), \qquad \hat{\sigma} = \sqrt{\frac{1}{T-1}\sum_{t=1}^T (\ln G_t - \hat{\mu})^2} = 0.0300 \quad (3.0\%)$$

| Year | Nominal GDP Growth (%) | Natural Log Growth $\ln G_t$ | Public Source |
| :---: | :---: | :---: | :--- |
| 2001 | +3.07% | +0.0303 | IMF WEO (2001-2025) |
| 2002 | +2.71% | +0.0268 | IMF WEO (2001-2025) |
| 2003 | +2.35% | +0.0232 | IMF WEO (2001-2025) |
| 2004 | +4.40% | +0.0430 | IMF WEO (2001-2025) |
| 2005 | +4.15% | +0.0407 | IMF WEO (2001-2025) |
| 2006 | +5.48% | +0.0534 | IMF WEO (2001-2025) |
| 2007 | +5.72% | +0.0556 | IMF WEO (2001-2025) |
| 2008 | +3.43% | +0.0338 | IMF WEO (2001-2025) |
| 2009 | -3.14% | -0.0320 | IMF WEO (2001-2025) |
| 2010 | +3.91% | +0.0384 | IMF WEO (2001-2025) |
| 2011 | +4.76% | +0.0465 | IMF WEO (2001-2025) |
| 2012 | +2.23% | +0.0221 | IMF WEO (2001-2025) |
| 2013 | +1.87% | +0.0185 | IMF WEO (2001-2025) |
| 2014 | +2.35% | +0.0232 | IMF WEO (2001-2025) |
| 2015 | +3.79% | +0.0372 | IMF WEO (2001-2025) |
| 2016 | +4.28% | +0.0419 | IMF WEO (2001-2025) |
| 2017 | +4.64% | +0.0453 | IMF WEO (2001-2025) |
| 2018 | +4.76% | +0.0465 | IMF WEO (2001-2025) |
| 2019 | +3.19% | +0.0314 | IMF WEO (2001-2025) |
| 2020 | -5.99% | -0.0618 | IMF WEO (2001-2025) |
| 2021 | +8.75% | +0.0838 | IMF WEO (2001-2025) |
| 2022 | +9.60% | +0.0916 | IMF WEO (2001-2025) |
| 2023 | +4.40% | +0.0430 | IMF WEO (2001-2025) |
| 2024 | +3.31% | +0.0326 | IMF WEO (2001-2025) |
| 2025 | +3.55% | +0.0349 | IMF WEO (2001-2025) |

## 6. 25-Year Historical Primary Balance Series (`country_primary_balance`)

Used in **Task A2** to evaluate fiscal capacity:
$$\bar{s} = \max_t \frac{1}{5}\sum_{j=t-4}^t pb_j = +2.0\% \text{ of GDP (sustained in pre-2009 and pre-pandemic expansions)}$$

| Year | Primary Balance (% of GDP) | 5-Year Rolling Average (%) | Sustained Benchmark Note |
| :---: | :---: | :---: | :--- |
| 2001 | +1.20% | — | Initial sample window |
| 2002 | +0.50% | — | Initial sample window |
| 2003 | -0.20% | — | Initial sample window |
| 2004 | +0.40% | — | Initial sample window |
| 2005 | +0.80% | +0.54% |  |
| 2006 | +1.50% | +0.60% |  |
| 2007 | +2.20% | +0.94% |  |
| 2008 | +1.80% | +1.34% |  |
| 2009 | -2.50% | +0.76% |  |
| 2010 | -1.80% | +0.24% |  |
| 2011 | -0.90% | -0.24% |  |
| 2012 | -0.60% | -0.80% |  |
| 2013 | -0.20% | -1.20% |  |
| 2014 | +0.30% | -0.64% |  |
| 2015 | +1.50% | +0.02% |  |
| 2016 | +1.90% | +0.58% |  |
| 2017 | +2.10% | +1.12% |  |
| 2018 | +2.50% | +1.66% |  |
| 2019 | +2.00% | +2.00% | **Max 5-Year Sustained Average (s_bar = 2.0%)** |
| 2020 | -5.80% | +0.54% |  |
| 2021 | -3.20% | -0.48% |  |
| 2022 | -1.20% | -1.14% |  |
| 2023 | -0.90% | -1.82% |  |
| 2024 | -2.10% | -2.64% |  |
| 2025 | -2.30% | -1.94% |  |

