# Wiki Rating Method Prompt

You are an expert knowledge extraction agent. Your task is to create or merge information into a Rating Method card.

## Context

- Method Name: $VALUE

## Existing Method Content

```markdown
$EXISTING_CONTENT
```

## New Summary Context

```markdown
$SUMMARY_CONTENT
```

## Instructions

Merge the details from the summary context into the existing profile for `$VALUE`.

- If the existing profile is empty, generate a new Rating Method page from scratch matching the Target Output Format template exactly.
- If the page already exists, merge the new details, analytical components, and application steps without overwriting existing content.
- All internal links must be simple Obsidian wikilinks.
- Output ONLY the valid markdown content. Do not include markdown code block wraps.

## Target Output Format (Template)

Ensure your output matches this exact structure:

```markdown
---
$SCHEMA
---

# $VALUE

## Overview

[Brief overview of the rating methodology, including the agency that publishes it and its main target (e.g., Issuer Default Ratings)...]

## Key Pillars & Analytical Components

[Detailed description of the core pillars, quantitative models (e.g., regression/SRM), and qualitative overlays/adjustments (e.g., QO) used in the methodology...]

## Key Metrics & Variables

- **[Metric/Variable Name]**: [Description and weight/significance of the metric/variable...]

## Application

1. **[Step 1 Name]**: [Description of the first step in applying the methodology, e.g., calculating initial quantitative metrics or sub-scores...]
2. **[Step 2 Name]**: [Description of the second step, e.g., applying qualitative overlays or adjusting for specific risks...]
3. **[Step 3 Name]**: [Description of the final step, e.g., rating committee review and consensus mapping to the final rating scale...]

## Related Entities

[[Concept A]], [[Institution B]], [[Person C]]
```
