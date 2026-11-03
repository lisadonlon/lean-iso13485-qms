---
doc_id: SVR-<% tp.date.now("YYYY") %>-<% tp.system.prompt("Software validation record number (e.g., 01)") %>
title: <% tp.system.prompt("Software and version (e.g., Obsidian Dataview 0.5.x)") %>
doc_type: record
standard: ISO 13485:2016
clauses: ["4.1.6"]
record_date: <% tp.date.now("YYYY-MM-DD") %>
author: 
tags: [qms, record, validation]
related: ["SOP-17"]
status: draft
approver: 
approved_date:
software:
software_version:
validation_approach: <% tp.system.suggester(["Use as-is", "Happy path", "Plan and report"], ["use-as-is", "happy-path", "plan-and-report"]) %>
---

# Software Validation: <% tp.frontmatter.title %>

**Record ID:** <% tp.frontmatter.doc_id %>
**Date:** <% tp.date.now("DD/MM/YYYY") %>
**Procedure:** [[SOP-17 Software Validation]]

> Complete section 1 for every approach. Then complete section 2 for the happy-path approach, or sections 3 and 4 for the plan-and-report approach. Delete the sections that do not apply.

## 1. Intended Use and Validation Approach

| Item | Detail |
|------|--------|
| Software and version | [name, version or commit] |
| Intended use in the QMS | [what you rely on it to do] |
| Risk if it fails | [what would go wrong, and whether another control would catch it] |
| Validation approach | [Use as-is / Happy path / Plan and report] |
| Rationale | [why this approach, with reference to the criteria in SOP-17] |
| Reason for this validation | [first use / new version / change in intended use / problem found in use] |

**Use as-is:** confirm the software is installed, is the expected version, and is fit for the intended use above. No testing is required.

**Confirmed by:** _________________________ **Date:** ___/___/______

## 2. Happy Path Test

Run the main workflow you rely on, end to end, with ordinary inputs.

| Step | Action | Expected result | Actual result | Pass/Fail |
|------|--------|-----------------|---------------|-----------|
| 1 | | | | |
| 2 | | | | |

**Conclusion:** ☐ Fit for intended use / ☐ Not fit — raise a CAPA

## 3. Validation Plan (plan and report)

> Complete and approve this section **before** testing starts, and commit it. The commit date is the evidence that the acceptance criteria were set first.

**Scope:** [functions in scope; functions explicitly out of scope]

| Criterion ID | Requirement (what the software must do) | Test method | Acceptance criterion |
|--------------|------------------------------------------|-------------|----------------------|
| AC-01 | | | |
| AC-02 | | | |

**Plan approved by:** _________________________ **Date:** ___/___/______

## 4. Validation Report (plan and report)

| Criterion ID | Actual result | Evidence (file, screenshot, commit) | Met? |
|--------------|---------------|-------------------------------------|------|
| AC-01 | | | |
| AC-02 | | | |

**Deviations:**

| # | Criterion | Deviation | Disposition | CAPA ref |
|---|-----------|-----------|-------------|----------|
| 1 | | | | |

**Conclusion:** ☐ All criteria met — validated for the intended use above / ☐ Not validated — do not rely on the software until resolved

**Report approved by:** _________________________ **Date:** ___/___/______

## 5. Corrections

> Records are made once and are not revised. If an entry above is wrong, leave it as it is and add a dated, attributed correction here.

| Date | By | Correction |
|------|----|-----------|
| | | |
