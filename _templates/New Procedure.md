---
doc_id: SOP-<% tp.system.prompt("SOP number (e.g., 01)") %>
title: <% tp.system.prompt("Procedure title") %>
doc_type: procedure
standard: <% tp.system.suggester(["ISO 13485:2016", "ISO 27001:2022", "both"], ["ISO 13485:2016", "ISO 27001:2022", "both"]) %>
clauses: [<% tp.system.prompt("Clause references (e.g., \"4.2.4\", \"8.5.2\")") %>]
revision: "1.0"
status: draft
effective_date:
review_due:
review_interval: 12
author: 
reviewer:
approver: 
approved_date:
change_summary: "Initial draft"
tags: [qms, procedure]
supersedes:
related: []
---

# <% tp.frontmatter.title %>

**Document ID:** <% tp.frontmatter.doc_id %>
**Revision:** <% tp.frontmatter.revision %>
**Effective Date:** [DD/MM/YYYY]

## 1. Purpose

[State the purpose of this procedure]

## 2. Scope

[Define the scope and applicability]

## 3. References

| Standard | Clause | Title |
|----------|--------|-------|
| | | |

## 4. Definitions

| Term | Definition |
|------|-----------|
| | |

## 5. Responsibilities

| Role | Responsibility |
|------|---------------|
| | |

## 6. Procedure

### 6.1 [Step/Section]

[Procedure details]

## 7. Records

| Record | Retention | Location |
|--------|-----------|----------|
| | | |

## 8. Revision History

| Rev | Date | Author | Change Summary |
|-----|------|--------|---------------|
| 1.0 | <% tp.date.now("DD/MM/YYYY") %> |  | Initial draft |
