---
doc_id: DASH-004
title: CAPA Log
doc_type: reference
standard: ISO 13485:2016
clauses: ["8.5.2", "8.5.3"]
revision: "1.0"
status: approved
tags: [dashboard, capa]
---

# CAPA Log

Live log of all Corrective and Preventive Actions.

## Open CAPAs

```dataview
TABLE
  doc_id AS "CAPA ID",
  title AS "Description",
  capa_type AS "Type",
  capa_source AS "Source",
  capa_priority AS "Priority",
  effective_date AS "Date Raised",
  target_date AS "Target Date"
FROM "05-records/capa"
WHERE capa_status = "open" OR status = "draft" OR status = "review"
SORT capa_priority DESC, effective_date ASC
```

## In Verification

```dataview
TABLE
  doc_id AS "CAPA ID",
  title AS "Description",
  target_date AS "Target Date"
FROM "05-records/capa"
WHERE capa_status = "verification"
SORT target_date ASC
```

## Closed CAPAs

```dataview
TABLE
  doc_id AS "CAPA ID",
  title AS "Description",
  capa_type AS "Type",
  closure_date AS "Closed",
  effective_date AS "Raised"
FROM "05-records/capa"
WHERE capa_status = "closed" OR status = "approved"
SORT closure_date DESC
```

## Summary

```dataview
TABLE length(rows) AS "Count"
FROM "05-records/capa"
WHERE doc_id
GROUP BY capa_status AS "Status"
```
