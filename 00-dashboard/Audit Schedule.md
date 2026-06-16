---
doc_id: DASH-005
title: Audit Schedule
doc_type: reference
standard: ISO 13485:2016
clauses: ["8.2.4"]
revision: "1.0"
status: approved
tags: [dashboard, audit]
---

# Audit Schedule

## Planned Audits

```dataview
TABLE
  doc_id AS "Audit ID",
  title AS "Audit Title",
  audit_type AS "Type",
  audit_date AS "Scheduled Date",
  audit_scope AS "Scope",
  auditor AS "Auditor"
FROM "05-records/audits"
WHERE audit_status = "planned"
SORT audit_date ASC
```

## In Progress

```dataview
TABLE
  doc_id AS "Audit ID",
  title AS "Audit Title",
  audit_date AS "Date",
  auditor AS "Auditor"
FROM "05-records/audits"
WHERE audit_status = "in-progress"
SORT audit_date ASC
```

## Completed Audits

```dataview
TABLE
  doc_id AS "Audit ID",
  title AS "Audit Title",
  audit_type AS "Type",
  audit_date AS "Date",
  auditor AS "Auditor"
FROM "05-records/audits"
WHERE audit_status = "completed" OR status = "approved"
SORT audit_date DESC
```

## Annual Coverage

All clauses should be audited at least once per 12-month cycle. Track coverage via the audit scope field.
