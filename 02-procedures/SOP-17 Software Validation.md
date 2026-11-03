---
doc_id: SOP-17
title: Software Validation
doc_type: procedure
standard: ISO 13485:2016
clauses: ["4.1.6", "7.5.6"]
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
related: ["SOP-02", "SOP-09", "SOP-14"]
---

# Software Validation

**Document ID:** SOP-17
**Revision:** 1.0
**Effective Date:** [DD/MM/YYYY]

> **Scope note.** ISO 13485:2016 requires software used in the QMS (§4.1.6), and in production and service provision (§7.5.6), to be validated for its intended use before first use and after changes, with an approach proportionate to the risk of using it [verify: §4.1.6 and §7.5.6 against the official text]. The three validation approaches in section 6.2 are one simple, risk-based way to do that. Adapt the criteria to your organisation. Software that is part of, or is itself, a medical device is outside this procedure: it falls under design and development ([[SOP-07 Design and Development Control]]) and IEC 62304.

## 1. Purpose

[State the purpose of this procedure — i.e. how software used in the QMS and in production and service provision is identified, assigned a validation approach, validated before use and re-validated after change.]

## 2. Scope

[Define what this procedure covers — e.g. QMS tooling, spreadsheets with calculations, eQMS or e-signature services, cloud storage, production or test software — and anything excluded.]

## 3. References

| Standard | Clause | Title |
|----------|--------|-------|
| ISO 13485:2016 | 4.1.6 | Validation of software used in the QMS |
| ISO 13485:2016 | 7.5.6 | Validation of processes for production and service provision |

## 4. Definitions

Terms used in this procedure are defined in [[REF-02 Glossary]], and role names in section 5 are taken from REF-02 section 1. Add any new term or role to REF-02; do not define it here.

## 5. Responsibilities

| Role | Responsibility |
|------|---------------|
| Quality Manager | [e.g. maintains the software inventory, assigns the validation approach for each piece of software, approves validation records] |
|  |  |

## 6. Procedure

### 6.1 Software Inventory

Every piece of software in scope is listed here with its intended use, the validation approach assigned to it and the reason. The rows below are examples taken from this template's own tooling. Assigning the approach is your decision; the template does not make it for you.

| Software | Version | Intended use | Risk if it fails | Validation approach | Rationale | Record |
|----------|---------|--------------|------------------|-----------------|-----------|--------|
| Git | [version] | Document control: change history, approval tags | [e.g. untraceable change history] | [use as-is / happy path / plan and report] | | [SVR-YYYY-NN] |
| Obsidian and community plugins | [versions] | Authoring; Dataview dashboards | | [use as-is / happy path / plan and report] | | |
| `scripts/validate_qms.py` | [commit] | Checks the vault against preset criteria; writes VAL records | | [use as-is / happy path / plan and report] | | |
| `scripts/export_for_audit.py` | [commit] | Produces controlled-copy PDFs and DIST records | | [use as-is / happy path / plan and report] | | |
| [add your own tools] | | | | | | |

### 6.2 Validation Approaches

Choose the approach by asking what happens if the software fails at its intended use. When in doubt, choose the more rigorous approach.

| Approach | When it applies | What is done | Record |
|-----------------|-----------------|--------------|--------|
| Use as-is | A failure would not realistically affect product conformity or the integrity of QMS records, or would be obvious at once and caught by other controls. | Confirm the software is installed, is the expected version and is fit for the intended use. No testing. | Inventory entry with rationale; section 1 of an SVR record. |
| Happy path | A failure could affect QMS records or outputs, but other controls or later review would detect it. | Run the main workflow you rely on, end to end, with ordinary inputs, and confirm the expected output. | SVR record, sections 1–2. |
| Plan and report | The software creates, changes, approves or controls QMS records, or affects product conformity, and a failure might go unnoticed. | Write a plan with acceptance criteria and approve it before testing. Test against every criterion, record and disposition any deviation, and approve the report before relying on the software. | SVR record, sections 1, 3 and 4. |

### 6.3 Re-validation

[State the triggers — e.g. a new version or update, a change in intended use, a problem found in use (raise a CAPA per [[SOP-14 Corrective and Preventive Action]]) — and that re-validation uses the same approach unless the change alters the risk. Review the inventory at management review.]

### 6.4 This Vault's Own Tooling

`make validate` runs the preset checks in `scripts/validate_qms.py` and writes a VAL record with the result. If you assign the vault tooling the plan-and-report approach, the checks in the script are the acceptance criteria (fixed before the run, and under change control in git) and the VAL record is the report. Record that decision and its rationale in section 6.1. A VAL record does not validate any other software.

## 7. Records

| Record | Retention | Location |
|--------|-----------|----------|
| Software validation records (SVR-YYYY-NN), made by hand from the template | [per SOP-02] | `05-records/software-validation/` |
| Validation script records (VAL-YYYY-NN), written by `scripts/validate_qms.py` | [per SOP-02] | `05-records/software-validation/` |

## 8. Revision History

| Rev | Date | Author | Change Summary |
|-----|------|--------|---------------|
| 1.0 | [DD/MM/YYYY] |  | Initial draft |
