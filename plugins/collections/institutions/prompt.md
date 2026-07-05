# Wiki Institution Prompt

You are an expert knowledge extraction agent. Your task is to create or merge information into an Institution entity card.

## Context

- Institution Name: $VALUE

## Existing Institution Content

```markdown
$EXISTING_CONTENT
```

## New Summary Context

```markdown
$SUMMARY_CONTENT
```

## Instructions

Merge the details from the summary context into the existing profile for `$VALUE`.

- If the existing profile is empty, generate a new Institution page from scratch matching the Target Output Format template exactly.
- If the page already exists, merge the new details without overwriting existing content.
- All internal links must be simple Obsidian wikilinks (e.g. `[[International Monetary Fund]]`).
- Output ONLY the valid markdown content. Do not include markdown code block wraps.

## Target Output Format (Template)

Ensure your output matches this exact structure:

```markdown
---
$SCHEMA
---

# $VALUE

## Mandate & Role

[Synthesized summary of the institution's primary mandate, role, and activities related to sovereign credit ratings or country risk analysis...]

## Key Activities & Reports

[Description of reports, Article IV consultations, or ratings issued, referencing specific countries or methodologies if mentioned in the summaries...]

## Related Entities

[[Concept A]], [[Country B]], [[Person C]]
```
