---
doc_id: WI-<% tp.system.prompt("WI number (e.g., 01)") %>
title: <% tp.system.prompt("Work instruction title") %>
doc_type: work-instruction
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
tags: [qms, work-instruction]
supersedes:
related: []
---

# <% tp.frontmatter.title %>

**Document ID:** <% tp.frontmatter.doc_id %>
**Revision:** <% tp.frontmatter.revision %>
**Effective Date:** [DD/MM/YYYY]
**Parent Procedure:** [[]]

## 1. Purpose

[What this work instruction achieves]

## 2. Prerequisites

- [Required before starting]

## 3. Instructions

### Step 1: [Action]

[Detailed step]

### Step 2: [Action]

[Detailed step]

## 4. Expected Output

[What the completed task looks like]

## 5. Revision History

| Rev | Date | Author | Change Summary |
|-----|------|--------|---------------|
| 1.0 | <% tp.date.now("DD/MM/YYYY") %> |  | Initial draft |
