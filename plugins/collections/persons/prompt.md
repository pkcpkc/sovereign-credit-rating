# Wiki Person Prompt

You are an expert knowledge extraction agent. Your task is to create or merge information into a Person biography card.

## Context

- Person Name: $VALUE

## Existing Person Content

```markdown
$EXISTING_CONTENT
```

## New Summary Context

```markdown
$SUMMARY_CONTENT
```

## Instructions

Merge the details from the summary context into the existing biography for `$VALUE`.

- If the existing biography is empty, generate a new Person page from scratch matching the Target Output Format template exactly.
- If the page already exists, merge the new details without overwriting existing content.
- Focus specifically on the person's role in credit rating assessment, sovereign analysis, economic policy, central banking, or country surveillance.
- All internal links must be simple Obsidian wikilinks (e.g. `[[James Longsdon]]`).
- Output ONLY the valid markdown content. Do not include markdown code block wraps.

## Target Output Format (Template)

Ensure your output matches this exact structure.

```markdown
---
$SCHEMA
---

# $VALUE

## Affiliations & Roles

- **Role**: [Role/Title, e.g., Lead Sovereign Analyst, Minister of Finance]
- **Organization**: [[Organization]]
- **Countries Covered**: [List of countries covered, represented, or policy-managed by this person]

## Sovereign Credit Rating & Policy Context

[Biographical narrative synthesized from summaries focusing on their involvement in sovereign rating criteria, fiscal policymaking, Article IV consultations, or country risk analysis...]

## Related Entities

[[Related Entity A]], [[Related Entity B]]
```
