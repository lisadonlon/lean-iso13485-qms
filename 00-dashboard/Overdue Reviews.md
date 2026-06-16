---
doc_id: DASH-002
title: Overdue Reviews
doc_type: reference
standard: both
clauses: ["4.2.4"]
revision: "1.0"
status: approved
tags: [dashboard]
---

# Overdue Reviews

Documents where `review_due` has passed and status is still `approved` (not yet reviewed/updated).

## Overdue

```dataview
TABLE
  doc_id AS "Doc ID",
  title AS "Title",
  review_due AS "Review Due",
  author AS "Owner",
  review_interval AS "Interval (months)"
FROM ""
WHERE review_due AND review_due < date(today) AND status = "approved" AND !contains(file.path, "_templates") AND !contains(file.path, "00-dashboard")
SORT review_due ASC
```

## Due Within 30 Days

```dataview
TABLE
  doc_id AS "Doc ID",
  title AS "Title",
  review_due AS "Review Due",
  author AS "Owner"
FROM ""
WHERE review_due AND review_due >= date(today) AND review_due <= date(today) + dur(30 days) AND status = "approved" AND !contains(file.path, "_templates") AND !contains(file.path, "00-dashboard")
SORT review_due ASC
```
