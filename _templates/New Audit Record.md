---
doc_id: AUD-<% tp.date.now("YYYY") %>-<% tp.system.prompt("Audit number (e.g., 01)") %>
title: <% tp.system.prompt("Audit title (e.g., Internal Audit - Document Control)") %>
doc_type: record
standard: ISO 13485:2016
clauses: ["8.2.4"]
record_date: <% tp.date.now("YYYY-MM-DD") %>
author: 
tags: [qms, audit, record]
related: []
status: draft
approver: 
approved_date:
audit_type:
audit_date:
audit_scope:
auditor:
audit_status: planned
---

# <% tp.frontmatter.title %>

**Audit ID:** <% tp.frontmatter.doc_id %>
**Type:** ☐ Internal / ☐ Supplier / ☐ External
**Date:** [DD/MM/YYYY]
**Auditor:** [Name]

## 1. Audit Scope

**Processes/Clauses audited:**

| Clause | Process | Auditee |
|--------|---------|---------|
| | | |

## 2. Audit Criteria

- ISO 13485:2016 clauses [list]
- Relevant SOPs: [[]]

## 3. Findings

### Nonconformances

| # | Clause | Finding | Classification | CAPA Ref |
|---|--------|---------|---------------|----------|
| 1 | | | ☐ Major / ☐ Minor | |

### Observations

| # | Area | Observation |
|---|------|------------|
| 1 | | |

### Opportunities for Improvement

| # | Area | Suggestion |
|---|------|-----------|
| 1 | | |

## 4. Audit Conclusion

[Overall assessment of conformity and QMS effectiveness]

## 5. Sign-off

**Auditor:** _________________________ **Date:** ___/___/______
**Auditee:** _________________________ **Date:** ___/___/______

## 6. Corrections

> Records are made once and are not revised. If an entry above is wrong, leave it as it is and add a dated, attributed correction here.

| Date | By | Correction |
|------|----|-----------|
| | | |
