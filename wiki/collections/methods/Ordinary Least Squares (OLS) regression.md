---
agency: Fitch Ratings
last_updated: 2025-09-15
timestamp: 2026-07-05T15:42:32Z
tags:
  - Sovereign Ratings
  - Quantitative Model
  - Credit Rating Methodology
  - Fitch Ratings
  - Sovereign Rating Model
---

# Ordinary Least Squares (OLS) regression

## Overview

In the context of **Fitch Ratings**' Sovereign Credit Rating methodology, **Ordinary Least Squares (OLS) regression** serves as the statistical foundation for the **Sovereign Rating Model (SRM)**. This quantitative model generates a baseline score calibrated to the Long-Term Foreign-Currency Issuer Default Rating (IDR) scale ('AAA' to 'CCC+'). The SRM acts as the starting point for rating assessments, capturing the primary economic and structural drivers of sovereign creditworthiness before qualitative adjustments are applied.

## Key Pillars & Analytical Components

The SRM is constructed using an OLS regression of **18 key variables** grouped into four analytical pillars. The model assigns specific weights to these pillars based on their statistical significance in predicting default risk.

### Analytical Pillars and Weighting

1.  **Structural Features (53.7%)**: The most heavily weighted pillar, reflecting long-term development and governance.
2.  **Public Finances (19.1%)**: Assesses fiscal health, debt levels, and revenue capacity.
3.  **External Finances (17.3%)**: Evaluates external liquidity, debt sustainability, and reserve adequacy.
4.  **Macroeconomic Performance (9.8%)**: Captures short-to-medium term economic volatility and growth trends.

## Key Metrics & Variables

The OLS model incorporates the following specific variables within their respective pillars:

-   **Governance Indicators**: Derived from the World Bank Worldwide Governance Indicators; part of Structural Features.
-   **GDP per Capita**: Used as a proxy for economic development; part of Structural Features.
-   **Share in World GDP**: Measures economic size and vulnerability (small economies are more vulnerable); part of Structural Features.
-   **Years Since Default/Restructuring**: Historical credit performance; part of Structural Features.
-   **Gross General Government Debt/GDP**: Primary measure of fiscal leverage; part of Public Finances.
-   **Interest Payments/Revenue**: Assesses fiscal burden; part of Public Finances.
-   **Fiscal Balance/GDP**: Measures overall fiscal position; part of Public Finances.
-   **Foreign-Currency Debt Share**: Exposure to currency risk; part of Public Finances.
-   **Reserve-Currency Flexibility**: Based on IMF COFER data; part of External Finances.
-   **Sovereign Net Foreign Assets**: External wealth position; part of External Finances.
-   **Commodity Dependence**: Exposure to terms-of-trade shocks; part of External Finances.
-   **FX Reserves**: Liquidity buffer; part of External Finances.
-   **External Interest Service**: Cost of external debt; part of External Finances.
-   **Current Account Balance + FDI**: External financing position; part of External Finances.
-   **Real GDP Growth Volatility**: Economic stability; part of Macroeconomic Performance.
-   **Consumer Price Inflation**: Price stability; part of Macroeconomic Performance.
-   **Real GDP Growth**: Economic expansion trend; part of Macroeconomic Performance.

## Application

1.  **Quantitative Scoring (SRM Calculation)**:
    Fitch calculates the initial quantitative score by inputting the 18 key variables into the OLS-based Sovereign Rating Model. The output is a numerical score that is calibrated to correspond to a specific Long-Term Foreign-Currency IDR rating.

2.  **Qualitative Overlay (QO) Adjustment**:
    The initial SRM score is adjusted using a Qualitative Overlay to account for factors not captured by the regression. Analysts can adjust the rating by **+2 to -2 notches** for each of the four pillars. The total adjustment is generally **capped at +3/-3 notches** from the SRM output. Exceptions for wider adjustments are made for countries in crisis, recovering from crisis, or with a default history within the last five years. Factors include geopolitical risk, financial sector stability (via BSI and MPI), and policy credibility.

3.  **Climate and Special Risk Screening**:
    Before finalizing the rating, Fitch applies screening tools such as the **Sovereign Climate Vulnerability Signals (Climate.VS)**. If a sovereign has a Climate.VS score of 50 or higher in 2035, additional analysis is triggered. If material climate risks are identified that are not already reflected in the SRM or QO, further notch adjustments may be applied under "Other structural factors."

4.  **Final Rating Determination**:
    The adjusted score is mapped to the final rating scale. For issuers rated 'B+' or below, **Recovery Ratings (RR)** may be assigned to notch instrument ratings up or down from the IDR based on expected loss severity in default. Local-Currency (LC) and Foreign-Currency (FC) ratings are typically aligned but may differentiate if there is an expectation of preferential treatment.

## Related Entities

[[Fitch Ratings]], [[Sovereign Rating Model (SRM)]], [[Qualitative Overlay (QO)]], [[World Bank]], [[International Monetary Fund]], [[James Longsdon]], [[Ed Parker]], [[Carlos Masip]], [[Rob Shearman]], [[Climate Vulnerability Signals]], [[Sovereign Climate Risk Model]]