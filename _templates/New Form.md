---
doc_id: FRM-<% tp.system.prompt("Form number (e.g., 01)") %>
title: <% tp.system.prompt("Form title") %>
doc_type: form
standard: <% tp.system.suggester(["ISO 13485:2016", "ISO 27001:2022", "both"], ["ISO 13485:2016", "ISO 27001:2022", "both"]) %>
clauses: [<% tp.system.prompt("Clause references") %>]
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
tags: [qms, form]
supersedes:
related: []
---

# <% tp.frontmatter.title %>

**Document ID:** <% tp.frontmatter.doc_id %>
**Revision:** <% tp.frontmatter.revision %>
**Parent Procedure:** [[]]

---

| Field | Value |
|-------|-------|
| Date: | |
| Completed by: | |
| | |

## Form Content

[Form fields and structure]

---

**Reviewed by:** _________________________ **Date:** ___/___/______

**Approved by:** _________________________ **Date:** ___/___/______
