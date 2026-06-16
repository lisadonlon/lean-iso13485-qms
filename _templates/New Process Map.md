---
doc_id: PM-<% tp.system.prompt("Process map number (e.g., 01)") %>
title: <% tp.system.prompt("Process map title") %>
doc_type: process-map
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
tags: [qms, process-map]
supersedes:
related: []
excalidraw-plugin: parsed
---

# <% tp.frontmatter.title %>

**Document ID:** <% tp.frontmatter.doc_id %>
**Revision:** <% tp.frontmatter.revision %>

## Process Description

**Process owner:** [Name]
**Inputs:** [List inputs]
**Outputs:** [List outputs]
**Resources:** [List resources]
**Controls:** [List controls — SOPs, standards]

## Excalidraw Diagram

[Open in Excalidraw to edit the process map]

## Related Documents

- [[]]

## Revision History

| Rev | Date | Author | Change Summary |
|-----|------|--------|---------------|
| 1.0 | <% tp.date.now("DD/MM/YYYY") %> |  | Initial draft |
