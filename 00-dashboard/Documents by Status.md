---
doc_id: DASH-003
title: Documents by Status
doc_type: reference
standard: both
clauses: ["4.2.4"]
revision: "1.0"
status: approved
tags: [dashboard]
---

# Documents by Status

## Draft

```dataview
TABLE doc_id AS "Doc ID", doc_type AS "Type", change_summary AS "Notes"
FROM ""
WHERE status = "draft" AND doc_id AND !contains(file.path, "_templates") AND !contains(file.path, "00-dashboard")
SORT doc_id ASC
```

## In Review

```dataview
TABLE doc_id AS "Doc ID", doc_type AS "Type", reviewer AS "Reviewer"
FROM ""
WHERE status = "review" AND doc_id AND !contains(file.path, "_templates") AND !contains(file.path, "00-dashboard")
SORT doc_id ASC
```

## Approved

```dataview
TABLE doc_id AS "Doc ID", doc_type AS "Type", effective_date AS "Effective", review_due AS "Review Due"
FROM ""
WHERE status = "approved" AND doc_id AND !contains(file.path, "_templates") AND !contains(file.path, "00-dashboard")
SORT doc_id ASC
```

## Obsolete

```dataview
TABLE doc_id AS "Doc ID", doc_type AS "Type", supersedes AS "Superseded By"
FROM ""
WHERE status = "obsolete" AND doc_id AND !contains(file.path, "_templates") AND !contains(file.path, "00-dashboard")
SORT doc_id ASC
```
