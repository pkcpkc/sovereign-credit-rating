---
fields:
  - sovereign-credit-rating-factors
---
# Wiki Sovereign Credit Rating Factors Prompt

You are an expert knowledge extraction agent. Your task is to create or merge information into a Sovereign Credit Rating Factors card.

## Context

- Country Name: $VALUE

## Existing Sovereign Credit Rating Factors Content

```markdown
$EXISTING_CONTENT
```

## New Summary Context

```markdown
$SUMMARY_CONTENT
```

## Instructions

Merge the details from the summary context into the existing sovereign credit rating factors profile for `$VALUE`.

- If the existing sovereign credit rating factors profile is empty, generate a new Sovereign Credit Rating Factors page from scratch matching the Target Output Format template exactly.
- If the page already exists, merge the new details, strengths, and threats without overwriting existing content.
- All internal links must be simple Obsidian wikilinks (e.g. `[[European Commission]]`).
  - **Internal Link Normalization Rules (CRITICAL to avoid duplicates):**
    When linking to other concepts, persons, or entities, format the link text using strict normalization:
    - **Case Normalization:** Always use Title Case (e.g., `[[Sovereign Debt]]`, not `[[sovereign debt]]`).
    - **Singularization:** Always link to the singular form of the noun/concept (e.g., `[[Neural Network]]`, not `[[Neural Networks]]`), unless the term is inherently plural (e.g., `[[United States]]`).
    - **Punctuation & Spacing:** Use standard spaces, not hyphens or underscores (e.g., `[[Deep Learning]]`, not `[[Deep-Learning]]`).
- Output ONLY the valid markdown content. Do not include markdown code block wraps.

## Target Output Format (Template)

Ensure your output matches this exact structure:

```markdown
---
$SCHEMA
---

# $VALUE

## Political and Geopolitical Risk

### Strengths

[Geopolitical stability, peaceful regional relations, low conflict risk, stable government, durable political consensus, or low domestic unrest...]

### Threats

[External security risks, war exposure, sanctions, regional instability, domestic unrest, political fragmentation, government instability, or regime risk...]

## Institutional and Governance Strength

### Strengths

[Strong institutions, credible governance, rule of law, transparency, low corruption, independent courts, effective oversight, strong checks and balances, and high administrative capacity...]

### Threats

[Weak institutions, poor rule of law, corruption, weak checks and balances, limited transparency, weak accountability, judicial weakness, poor governance, or low administrative capacity...]

## Policy Predictability and Reform Continuity

### Strengths

[Stable policy formation, predictable government behavior, transparent decision-making, durable reform agendas, and strong policy continuity...]

### Threats

[Abrupt policy reversals, weak coalition discipline, unclear policy direction, populist pressure, inconsistent reform implementation, or unstable policymaking...]

## Debt Payment Culture

### Strengths

[Strong record of timely debt repayment, creditor-friendly behavior, established commitment to honoring obligations, and low willingness-to-pay risk...]

### Threats

[Weak willingness to pay, default history, arrears, coercive restructuring behavior, creditor-unfriendly treatment, or political resistance to debt service...]

## Economic Strength and Tax Base

### Strengths

[High GDP per capita, broad taxable income base, productive economy, high formalization, strong revenue capacity, and resilient household or corporate income base...]

### Threats

[Weak GDP per capita, low income levels, narrow or informal tax base, weak productivity, limited formal economic activity, or constrained revenue-generating capacity...]

## Growth Prospects

### Strengths

[Resilient growth, favorable demographics, productivity gains, strong investment, competitiveness, innovation, and structural reform benefits...]

### Threats

[Weak medium- or long-term growth, low investment, poor productivity, adverse demographics, weak competitiveness, reform stagnation, or declining output potential...]

## Economic Diversity

### Strengths

[Diversified output, multiple export sectors, resilient domestic demand, low commodity dependence, and broad economic structure...]

### Threats

[Commodity dependence, tourism dependence, narrow economic structure, sector concentration, climate-sensitive output, or vulnerability to sector-specific shocks...]

## External Position and Liquidity

### Strengths

[Strong FX reserves, ample external liquidity, durable market access, low short-term external debt, resilient balance of payments, net external assets, favorable international investment position, low external debt, or creditor-nation status...]

### Threats

[Weak FX reserves, limited external funding access, balance-of-payments pressure, high short-term external debt, weak reserve adequacy, external refinancing pressure, net external liabilities, or dependence on foreign creditors...]

## Currency and Exchange Rate Flexibility

### Strengths

[Reserve-currency status, high international currency use, deep local-currency markets, credible currency framework, monetary flexibility, stable exchange-rate regime, and low FX mismatch risk...]

### Threats

[Weak international currency use, dollarization, currency substitution, limited monetary flexibility, exchange-rate instability, unsustainable pegs, FX intervention pressure, devaluation risk, currency mismatches, or loss of external competitiveness...]

## Financial Sector Health

### Strengths

[Well-capitalized banks, strong supervision, low nonperforming loans, stable funding, resilient credit markets, and low systemic financial risk...]

### Threats

[Banking-sector weakness, asset-quality deterioration, credit bubbles, liquidity stress, weak supervision, financial instability, or potential banking-sector support costs...]

## Fiscal Performance and Flexibility

### Strengths

[Prudent fiscal management, budget surpluses, expenditure flexibility, reliable revenue, credible budgeting, and strong capacity for fiscal adjustment...]

### Threats

[Weak fiscal balance, poor revenue performance, weak expenditure control, limited fiscal flexibility, poor budget credibility, or constrained ability to adjust taxes and spending...]

## Debt Burden

### Strengths

[Low government debt, declining debt ratios, affordable interest costs, long maturities, local-currency debt, diversified investor base, and favorable debt structure...]

### Threats

[High government debt, rising debt ratios, heavy interest burden, refinancing pressure, unfavorable debt structure, short maturities, FX debt exposure, or weak debt affordability...]

## Fiscal Sustainability

### Strengths

[Sustainable debt dynamics, strong fiscal rules, long-term budget discipline, manageable aging costs, durable primary balances, and credible medium-term fiscal framework...]

### Threats

[Persistent deficits, aging costs, pension liabilities, healthcare spending pressure, weak revenue base, structural expenditure pressure, or limited long-term adjustment capacity...]

## Contingent Liabilities

### Strengths

[Low off-budget risks, transparent guarantees, limited SOE liabilities, strong public-sector governance, contained financial-sector backstop risk, and clear fiscal risk reporting...]

### Threats

[Off-budget obligations, state-owned enterprise liabilities, public guarantees, public-private partnership risks, local government debt, bank recapitalization risk, or other implicit liabilities...]

## Monetary Policy and Price Stability

### Strengths

[Low and stable inflation, credible inflation targeting, anchored expectations, effective monetary transmission, independent central bank, strong monetary-policy governance, and strong anti-inflation record...]

### Threats

[High or volatile inflation, deflation, loss of price anchor, unanchored inflation expectations, monetary financing, weak monetary transmission, political interference with the central bank, fiscal dominance, or weakened monetary-policy credibility...]

## Related Entities

[[Concept A]], [[Country B]], [[Person C]]
```
