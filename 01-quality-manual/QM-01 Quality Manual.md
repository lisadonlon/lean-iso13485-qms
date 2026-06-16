---
doc_id: QM-01
title: Quality Manual
doc_type: manual
standard: ISO 13485:2016
clauses: ["4.2.2"]
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
tags: [qms, manual]
supersedes:
related: ["QM-02", "QM-03", "QM-04"]
---

# Quality Manual

**Document ID:** QM-01
**Revision:** 1.0
**Effective Date:** [DD/MM/YYYY]

> **How to use this skeleton.** This is the keystone document required by ISO 13485:2016 §4.2.2. Replace every `[bracketed]` prompt and `{{ORGANISATION_NAME}}` token with your own content. Keep it specific to your organisation — a generic manual is an audit finding waiting to happen. The mandatory parts a manual must contain are the **scope** (with justified exclusions), the **documented procedures** (or references to them), and a **description of the interaction between the QMS processes**; those sections are flagged below.

## 1. Introduction and Purpose

This manual describes the Quality Management System (QMS) of {{ORGANISATION_NAME}}, established to meet the requirements of ISO 13485:2016 and the regulatory requirements applicable to our medical devices. [State the manual's purpose and intended audience.]

## 2. Organisation and Context

| Item | Detail |
|------|--------|
| Legal entity | {{ORGANISATION_NAME}} |
| Company registration | [number] |
| Registered office | [address] |
| Operating site(s) | [address(es) and the activities performed at each] |
| Regulatory role | [e.g. legal manufacturer / own-brand labeller / contract manufacturer] |

[Describe what the organisation does, the devices it places on the market, the markets/jurisdictions it serves, and a brief history relevant to the QMS scope.]

## 3. Scope and Exclusions (mandatory — §4.2.2 / §1.2)

The scope of this QMS, and the clauses determined as not applicable together with their justification, are defined in [[QM-04 Scope and Exclusions]]. [Summarise the scope in one or two sentences here and reference QM-04 for the detail.]

## 4. Quality Policy and Objectives

The quality policy is defined in [[QM-02 Quality Policy]] and the measurable quality objectives in [[QM-03 Quality Objectives]].

## 5. QMS Process Model and Interaction (mandatory — §4.2.2c)

The QMS is operated as a set of interacting processes. [Describe each process: its owner, inputs, outputs, and the controlling procedure. Adjust the list to your organisation — remove processes you do not perform and mark the corresponding clause N/A in QM-04.]

| Process | Controlling procedure | Clause |
|---------|----------------------|--------|
| Document and record control | [[SOP-01 Document Control]], [[SOP-02 Control of Records]] | 4.2 |
| Management responsibility and review | [[SOP-03 Management Review]] | 5 |
| Resource and competence management | [[SOP-04 Human Resources and Competence]] | 6 |
| Risk management | [[SOP-06 Risk Management]] | 7.1 |
| Design and development | [[SOP-07 Design and Development Control]] | 7.3 |
| Purchasing and supplier control | [[SOP-08 Purchasing and Supplier Control]] | 7.4 |
| Production and service provision | [[SOP-09 Production and Service Provision]] | 7.5 |
| Measurement, analysis and improvement | [[SOP-12 Internal Audit]], [[SOP-14 Corrective and Preventive Action]] | 8 |
| Vigilance and regulatory reporting | [[SOP-16 Vigilance and Regulatory Reporting]] | 8.2.3 |

**Process interaction diagram:** [Insert a process-interaction (turtle) diagram here — see `07-process-maps/`. Embed it as an image, e.g. `![Process interaction](../07-process-maps/PM-01-process-interaction.svg)`.]

## 6. Documentation Structure (mandatory — §4.2.1)

| Tier | Content | Location |
|------|---------|----------|
| 1 — Manual & policy | This manual, quality policy, objectives, scope | `01-quality-manual/` |
| 2 — Procedures | What is done and who does it | `02-procedures/` |
| 3 — Work instructions / forms | How specific tasks are performed; blank forms | `03-work-instructions/`, `04-forms-templates/` |
| 4 — Records | Evidence that the QMS is operating | `05-records/` |

Document control is operated through Git per [[SOP-01 Document Control]]: the `main` branch is the controlled copy and annotated tags mark approved versions.

## 7. Conformity to ISO 13485:2016 (clause-by-clause)

[Provide a clause-by-clause statement of how each applicable clause is met, referencing the controlling procedure. A starting map is maintained in [[REF-01 ISO 13485 Clause-to-Document Map]]. Exclusions are justified in [[QM-04 Scope and Exclusions]].]

## 8. Management Responsibility

[Identify top management, the appointed management representative (§5.5.2), and the responsibilities and authorities for quality (§5.5.1).]

## 9. Revision History

| Rev | Date | Author | Change Summary |
|-----|------|--------|---------------|
| 1.0 | [DD/MM/YYYY] |  | Initial draft |
