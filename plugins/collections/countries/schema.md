---
type: "Schema"
title: "Country Schema"
description: "Defines the custom fields extracted into summary frontmatter for Country entities."
---

# Country Schema

## Summary Extension Specification

These fields are dynamically injected into the summary frontmatter under the root schema name key.

| Key         | Type  | Requirement  | Description                                                                                                            |
| :---------- | :---- | :----------- | :--------------------------------------------------------------------------------------------------------------------- |
| `countries` | Array | **Required** | List of sovereign nations mentioned in the text (e.g. Austria, France, Italy).                                         |
| `ratings`   | Array | **Required** | List of credit rating actions (e.g. countryName, agency, rating, outlook, date) associated with extracted countries.    |
