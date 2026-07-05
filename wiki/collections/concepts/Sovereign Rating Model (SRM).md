---
timestamp: 2026-07-05T14:14:21Z
tags: [Sovereign Ratings, Credit Rating Methodology, Fitch Ratings, Sovereign Rating Model, Quantitative Analysis, OLS Regression]
---

# Sovereign Rating Model (SRM)

The **Sovereign Rating Model (SRM)** is the core quantitative framework employed by [[Fitch Ratings]] to establish the baseline creditworthiness of sovereign issuers. Effective from September 15, 2025, the SRM serves as the starting point for assigning Long-Term Foreign-Currency [[Issuer Default Rating]] (IDR) levels, calibrated on the scale from 'AAA' to 'CCC+'. It is an Ordinary Least Squares (OLS) regression model based on 18 key variables, designed to measure the capacity of sovereign issuers to honor their debt obligations through statistical analysis of historical default events and macroeconomic data.

## Methodological Framework

The SRM is not a standalone rating tool but a foundational scoring mechanism that is subsequently adjusted via the [[Qualitative Overlay]] (QO). The model generates a numerical score based on four analytical pillars, each carrying a specific weight determined by its statistical significance in predicting sovereign default and restructuring events.

### Analytical Pillars and Weighting

The SRM aggregates data across four primary categories. The weighting reflects the relative importance of structural factors versus cyclical macroeconomic conditions in determining long-term credit stability:

1.  **Structural Features (53.7%)**: The most heavily weighted pillar, reflecting the long-term foundation of a country's credit profile.
    *   *Key Variables*: [[Governance indicators]] (sourced from World Bank Worldwide Governance Indicators), GDP per capita (proxy for development level), share in world GDP (smaller economies are deemed more vulnerable to external shocks), and years since default or restructuring.
2.  **Public Finances (19.1%)**: Assesses the fiscal position and debt burden of the sovereign.
    *   *Key Variables*: Gross general government debt-to-GDP ratio, interest payments-to-revenue ratio, fiscal balance-to-GDP, and the share of foreign-currency debt in total public debt.
3.  **External Finances (17.3%)**: Evaluates the external liquidity position and vulnerability to global financial conditions.
    *   *Key Variables*: [[Reserve-currency flexibility]], sovereign net foreign assets, commodity dependence, FX reserves, external interest service costs, and the current account balance plus Foreign Direct Investment (FDI).
4.  **Macroeconomic Performance, Policies, and Prospects (9.8%)**: Measures the stability and growth trajectory of the economy.
    *   *Key Variables*: Real GDP growth volatility, consumer price inflation, and real GDP growth rates.

### Interaction with Qualitative Overlay (QO)

While the SRM provides the quantitative baseline, it does not capture all relevant credit risks. The [[Qualitative Overlay]] (QO) is applied to adjust the SRM output to account for factors such as geopolitical risk, financial sector stability, policy credibility, and [[Climate Risk]].

*   **Adjustment Limits**: The QO allows for notch adjustments of ±2 per pillar.
*   **Total Cap**: The total adjustment from the SRM output is generally capped at ±3 notches.
*   **Exceptions**: Wider adjustments may be applied in cases of sovereigns in crisis, recovering from crisis, or with a default history within the last five years.

## Significance in Credit Analysis

The SRM is critical for ensuring consistency and objectivity in sovereign credit analysis. By relying on a statistically derived model, Fitch ensures that ratings are anchored in measurable economic fundamentals. However, the model's heavy weighting of structural features (53.7%) highlights the view that long-term institutional quality and economic development are more predictive of default risk than short-term macroeconomic fluctuations.

### Integration with Other Models and Risks

The SRM operates in conjunction with several other specialized models and screening tools within Fitch's broader methodology:

*   **Climate Vulnerability Signals (Climate.VS)**: A new screening tool introduced in the 2025 criteria. Sovereigns with a Climate.VS score of 50 or higher in 2035 (aggregating physical and transition risks) undergo additional scrutiny. If climate risks are material and not sufficiently captured by the SRM or standard QO, they may trigger a notch adjustment under "Other structural factors."
*   **Macro-Prudential Monitoring**: The SRM's financial sector assumptions are supported by the [[Macro-Prudential Indicator Model]] (MPI) and [[Banking Systemic Indicator]] (BSI), which assess the health and systemic risk of the banking sector.
*   **External Liquidity**: The [[International Liquidity Ratio]] (ILR) is used alongside the SRM's external finance variables to gauge short-term external liquidity risk, particularly for short-term rating mappings.
*   **Debt Sustainability**: While the SRM uses static debt ratios, long-term sustainability is further analyzed using the [[Fitch Debt Dynamics Model]] (DDM) during the qualitative assessment phase.

## Rating Outcomes and Differentiation

The SRM output primarily informs the [[Foreign-Currency Issuer Default Rating]] (FC IDR). The model's results are mapped to the rating scale, which is then subject to the QO adjustments.

*   **Local vs. Foreign Currency**: LC and FC ratings are typically aligned. Differentiation occurs if there is an expectation of preferential treatment, driven by differences in debt burdens, domestic capital market depth, or access to foreign currency.
*   **Recovery Ratings**: For issuers rated 'B+' or below, the SRM's assessment of default probability is complemented by [[Recovery Ratings]] (RR1 to RR6) to estimate potential loss severity in the event of default. This impacts instrument ratings, which may be notched up or down from the IDR.

## Historical Context and Updates

The current iteration of the SRM, effective September 15, 2025, represents an update from the previous criteria published on October 24, 2024. Key updates include the formalization of the weighting structure (highlighting the dominance of structural features) and the enhanced integration of climate risk signals into the qualitative adjustment process. The model relies on data from institutions such as the [[World Bank]], [[International Monetary Fund]], and [[Bank for International Settlements (BIS)]].