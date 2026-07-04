# Wiki Concept Prompt

You are an expert knowledge extraction agent. Your task is to create or merge information into a Concept card.

## Context

- Concept Name: $VALUE

## Existing Concept Content

```markdown
$EXISTING_CONTENT
```

## New Summary Context

```markdown
$SUMMARY_CONTENT
```

## Instructions

Merge the new definitions, key details, and related concepts from the summary context into the existing concept content for `$VALUE`.

- If the existing concept content is empty, generate a new Concept page from scratch matching the Target Output Format template exactly.
- If the existing concept page already exists, merge the new details, definitions, and relationships into the existing document. Do NOT overwrite existing definitions; append and synthesize new information.
- All internal links must be simple Obsidian wikilinks (e.g. `[[Deep Learning]]`).
- Output ONLY the valid markdown content. Do not include markdown code block wraps.

## Target Output Format (Template)

Ensure your output matches this exact structure.

```markdown
---
$SCHEMA
---

# $VALUE

[Concept narrative details, definitions, and synthesis of information...]
```
