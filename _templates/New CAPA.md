---
doc_id: CAPA-<% tp.date.now("YYYY") %>-<% tp.system.prompt("CAPA number (e.g., 01)") %>
title: <% tp.system.prompt("CAPA title (brief description of issue)") %>
doc_type: record
standard: ISO 13485:2016
clauses: ["8.5.2", "8.5.3"]
revision: "1.0"
status: draft
effective_date: <% tp.date.now("YYYY-MM-DD") %>
review_due:
review_interval: 12
author: 
reviewer:
approver: 
approved_date:
change_summary: "CAPA initiated"
tags: [qms, capa, record]
supersedes:
related: []
capa_type:
capa_source:
capa_status: open
capa_priority:
target_date:
closure_date:
---

# CAPA: <% tp.frontmatter.title %>

**CAPA ID:** <% tp.frontmatter.doc_id %>
**Date Raised:** <% tp.date.now("DD/MM/YYYY") %>
**Type:** ☐ Corrective / ☐ Preventive
**Source:** ☐ Audit / ☐ Complaint / ☐ Nonconformance / ☐ Management Review / ☐ Other
**Priority:** ☐ High / ☐ Medium / ☐ Low

## 1. Description of Issue

[Describe the nonconformance, complaint, or potential issue]

## 2. Immediate Action (if applicable)

| Action | Responsible | Date | Status |
|--------|------------|------|--------|
| | | | |

## 3. Root Cause Analysis

**Method used:** ☐ 5 Why / ☐ Fishbone / ☐ Other

[Root cause analysis details]

## 4. Corrective/Preventive Action Plan

| # | Action | Responsible | Target Date | Status |
|---|--------|------------|-------------|--------|
| 1 | | | | |

## 5. Effectiveness Verification

**Verification method:** [How will effectiveness be measured?]
**Verification date:** [DD/MM/YYYY]
**Result:** ☐ Effective / ☐ Not effective — escalate

## 6. Closure

**Closed by:** _________________________ **Date:** ___/___/______
**Approved by:** _________________________ **Date:** ___/___/______

## 7. Revision History

| Rev | Date | Author | Change Summary |
|-----|------|--------|---------------|
| 1.0 | <% tp.date.now("DD/MM/YYYY") %> |  | CAPA initiated |
