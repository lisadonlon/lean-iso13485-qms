---
doc_id: FRM-01
title: Controlled Document Distribution Log
doc_type: form
standard: ISO 13485:2016
clauses: ["4.2.4"]
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
tags: [qms, form, distribution]
supersedes:
related: ["SOP-01"]
---

# Controlled Document Distribution Log

**Document ID:** FRM-01
**Revision:** 1.0
**Parent Procedure:** [[SOP-01 Document Control]]

---

## Purpose

This form records each external distribution of controlled QMS documents (typically a PDF snapshot exported via `scripts/export_for_audit.py`). It supports ISO 13485:2016 §4.2.4 — ensuring relevant versions are available at the point of use and that obsolete documents are not used unintentionally.

Each row is one distribution event (e.g. one auditor share, one customer due-diligence package) and should cross-reference the matching `DIST-YYYY-NN` record in `05-records/distribution/`.

## How to use

1. Run `python3 scripts/export_for_audit.py` (or `make export`) to generate the controlled-copy PDF snapshot and a `DIST-YYYY-NN.md` record.
2. Share the output folder via a view-only link or agreed secure method.
3. Add a row below capturing recipient, purpose, delivery method, and the matching `DIST-YYYY-NN` ID.
4. When access ends, populate the **Access withdrawn** column.

## Distribution log

| # | Date issued (DD/MM/YYYY) | Recipient | Organisation | Email | Purpose | DIST record | Delivery method | Link / location | Link expiry | Access withdrawn | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |  |

## Controls

- Only documents with `status: approved` may be distributed externally. The export script enforces this.
- Each distributed package is a point-in-time snapshot — it does not update when the source is revised. Notify recipients if a material change is made.
- Drafts must not be shared externally except under an explicit written agreement (record in **Notes**).
- Complete the **Access withdrawn** field within 30 days of link expiry or conclusion of the engagement, whichever is sooner.

## Revision History

| Rev | Date | Author | Change Summary |
|-----|------|--------|---------------|
| 1.0 | [DD/MM/YYYY] |  | Initial draft |
