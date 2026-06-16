---
doc_id: ISMS-<% tp.system.prompt("ISMS number (e.g., 01)") %>
title: <% tp.system.prompt("ISMS document title") %>
doc_type: isms
standard: ISO 27001:2022
clauses: [<% tp.system.prompt("Clause references (e.g., \"4.3\", \"6.1.2\")") %>]
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
tags: [qms, isms, iso27001]
supersedes:
related: []
---

# <% tp.frontmatter.title %>

**Document ID:** <% tp.frontmatter.doc_id %>
**Revision:** <% tp.frontmatter.revision %>
**Effective Date:** [DD/MM/YYYY]

## 1. Purpose

[Purpose of this ISMS document]

## 2. Scope

[Scope of applicability]

## 3. References

| Standard | Clause | Title |
|----------|--------|-------|
| ISO 27001:2022 | | |
| ISO 27002:2022 | | |

## 4. Definitions

| Term | Definition |
|------|-----------|
| | |

## 5. Policy / Content

[Main document content]

## 6. Roles and Responsibilities

| Role | Responsibility |
|------|---------------|
| | |

## 7. Review and Monitoring

[How this document is reviewed and monitored for effectiveness]

## 8. Revision History

| Rev | Date | Author | Change Summary |
|-----|------|--------|---------------|
| 1.0 | <% tp.date.now("DD/MM/YYYY") %> |  | Initial draft |
