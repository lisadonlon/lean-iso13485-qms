---
doc_id: DASH-001
title: Document Register
doc_type: reference
standard: both
clauses: ["4.2.4"]
revision: "1.0"
status: approved
tags: [dashboard]
---

# Document Register

Live register of all controlled QMS documents.

## All Documents

```dataview
TABLE
  doc_id AS "Doc ID",
  doc_type AS "Type",
  standard AS "Standard",
  revision AS "Rev",
  status AS "Status",
  effective_date AS "Effective",
  review_due AS "Review Due"
FROM ""
WHERE doc_id AND doc_type != "reference" AND !contains(file.path, "_templates") AND !contains(file.path, "00-dashboard") AND !contains(file.path, "_archive")
SORT doc_id ASC
```

## Summary by Type

```dataview
TABLE length(rows) AS "Count"
FROM ""
WHERE doc_id AND !contains(file.path, "_templates") AND !contains(file.path, "00-dashboard") AND !contains(file.path, "_archive")
GROUP BY doc_type AS "Document Type"
SORT doc_type ASC
```
