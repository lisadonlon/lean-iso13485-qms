---
doc_id: AUD-<% tp.date.now("YYYY") %>-<% tp.system.prompt("Audit number (e.g., 01)") %>
title: <% tp.system.prompt("Audit title (e.g., Internal Audit - Document Control)") %>
doc_type: record
standard: ISO 13485:2016
clauses: ["8.2.4"]
revision: "1.0"
status: draft
effective_date: <% tp.date.now("YYYY-MM-DD") %>
review_due:
review_interval: 12
author: 
reviewer:
approver: 
approved_date:
change_summary: "Audit record created"
tags: [qms, audit, record]
supersedes:
related: []
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

## 6. Revision History

| Rev | Date | Author | Change Summary |
|-----|------|--------|---------------|
| 1.0 | <% tp.date.now("DD/MM/YYYY") %> |  | Audit record created |
