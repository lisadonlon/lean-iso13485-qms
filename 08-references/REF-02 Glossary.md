---
doc_id: REF-02
title: Glossary
doc_type: reference
standard: ISO 13485:2016
clauses: ["3"]
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
tags: [qms, reference]
supersedes:
related: ["QM-01", "SOP-01", "SOP-02", "SOP-17"]
---

# Glossary

**Document ID:** REF-02
**Revision:** 1.0
**Effective Date:** [DD/MM/YYYY]

> **Start here, before writing the procedures.** Every QMS document uses the role names and terms exactly as they are defined in this glossary. That way the same thing has the same name everywhere: in procedures, forms, records, contracts and the software you use. When a document needs a new term, add it here first instead of defining it inside that document. Renaming a role or term later means revising every document that uses it, so settle the names early. Be wary of generic ranking words such as *tier*, *level*, *grade* or *class*. They are easily reused for different things in different documents, and some already have a regulatory meaning (device *class*, for example). Prefer a name that says what the thing is, and define every use here.

## 1. Roles

> List roles, not people. Record who holds each role separately, for example in an organisation chart or appointment records, so a change of staff does not force a revision of every procedure. Delete the roles you do not have and add your own. One person may hold several roles, but where independence is required (for example, an internal auditor does not audit their own work) check that the combination allows it.

| Role name (use exactly this in documents) | Responsible for | Required by | Notes |
|-------------------------------------------|-----------------|-------------|-------|
| Top management | [e.g. quality policy, quality objectives, resources, management review] | ISO 13485:2016 §5 | [Who makes up top management in {{ORGANISATION_NAME}}] |
| Management representative | [e.g. making sure QMS processes are documented, reporting on QMS effectiveness, promoting awareness of regulatory requirements] | ISO 13485:2016 §5.5.2 | Often the same person as the Quality Manager in a small company |
| Quality Manager | [e.g. running the QMS day to day: document control, records, CAPA, internal audit programme] | Your own role name | The procedure skeletons use this name. If you call the role something else, rename it here and in every document |
| Person responsible for regulatory compliance (PRRC) | [responsibilities as set out in the regulation] | EU MDR Article 15, if you place devices on the EU market | Small and micro enterprises have different options for how the PRRC is provided |
| Process owner | [e.g. owns a process, its procedure and its performance measures] | Your own role name | |
| Internal auditor | [e.g. plans and carries out internal audits, reports findings] | ISO 13485:2016 §8.2.4 | Does not audit their own work |
| Document author | Drafts and revises controlled documents | SOP-01 | |
| Document reviewer | Reviews controlled documents for adequacy before approval | SOP-01 | |
| Document approver | Approves controlled documents for release | SOP-01 | [State who may approve which document types] |
| [Your own roles, e.g. Design Lead, Regulatory Affairs Lead, Production Supervisor] | | | |

## 2. Company Terms

> Your own vocabulary: product and service names, internal process names, abbreviations and the names of the software you use. Where your customers, contracts or software already use a term, use the same one here. The terms already listed are the ones this template uses for its own machinery; keep them or rename them consistently.

| Term | Meaning in {{ORGANISATION_NAME}} | Used in |
|------|----------------------------------|---------|
| Controlled document | A document that says what is done: manual, policy, procedure, work instruction, form, process map or reference. It is approved, takes effect on a date, is reviewed on a cycle and is changed only by issuing a new revision. | SOP-01 |
| Record | Evidence that something was done. It is made once and kept, and is never revised. A wrong entry is corrected by a dated, attributed correction that leaves the original visible. | SOP-02 |
| Revision | A numbered, approved version of a controlled document (1.0, 1.1, 2.0). Records do not have revisions. | SOP-01 |
| Effective date | The date an approved revision takes effect. | SOP-01 |
| Review due | The date by which an approved document is reviewed to confirm it is still suitable. | SOP-01 |
| Approval tag | The annotated git tag (`{DOC-ID}-v{revision}`) created when a revision is approved. | SOP-01, `HOWTO.md` |
| Controlled copy | A PDF export of approved documents, stamped with revision and git version and issued under a distribution record. | SOP-01, FRM-01 |
| Validation approach | How rigorously a piece of software is validated, chosen by the risk of using it: use as-is, happy path, or plan and report. | SOP-17 |
| Intended use (of software) | What {{ORGANISATION_NAME}} relies on a piece of software to do within the QMS or a process. | SOP-17 |
| Acceptance criterion | A pass/fail condition set before testing starts. | SOP-17 |
| [Your product, device and service names] | | |
| [Your abbreviations] | | |

## 3. Regulatory Terms

> These terms have formal definitions in standards and regulations, and those definitions are not reproduced here: standards are copyright, and regulations should be read in their current official text. The source column says where each definition is. The note is a plain-language reading for orientation only. It is not the definition and must not be quoted as one. ISO 13485:2016 uses the terms of ISO 9000:2015 as well as its own clause 3. Remove terms that do not apply to you and add the ones your markets need (for example, FDA terms). [verify: every clause and article reference below against the current official text before approval]

| Term | Formal definition in | Plain-language note (not the definition) |
|------|---------------------|-------------------------------------------|
| Medical device | ISO 13485:2016 §3.11; EU MDR Article 2 | Defined by what the manufacturer intends the product to be used for, not by the technology. |
| Intended purpose | EU MDR Article 2 | What the manufacturer says the device is for. It drives classification and the evidence needed. |
| Manufacturer | ISO 13485:2016 §3.10; EU MDR Article 2 | The party responsible for a device placed on the market under its name, whether or not it makes the device itself. |
| Authorized representative | ISO 13485:2016 §3.2; EU MDR Article 2 | Acts on behalf of a manufacturer based outside the jurisdiction, for specified tasks. |
| Importer | ISO 13485:2016 §3.7; EU MDR Article 2 | Places a device from outside the jurisdiction on its market. |
| Distributor | ISO 13485:2016 §3.5; EU MDR Article 2 | Makes a device available further down the supply chain. |
| Economic operator | EU MDR Article 2 | Collective term covering the manufacturer, authorised representative, importer, distributor and certain others. |
| Notified body | EU MDR Article 2 | A body designated to assess conformity of devices under the regulation. |
| Labelling | ISO 13485:2016 §3.8 | The label, instructions for use and other information supplied with the device. Wider than the label alone. |
| Life-cycle | ISO 13485:2016 §3.9 | Every phase of a device, from first concept to final disposal. |
| Product | ISO 13485:2016 §3.15 | The result of a process. In ISO 13485 the requirements for product also apply to services. |
| Purchased product | ISO 13485:2016 §3.16 | Product, including services, supplied by an outside party. |
| Medical device family | ISO 13485:2016 §3.12 | A group of devices that share basic design and performance characteristics. |
| Complaint | ISO 13485:2016 §3.4 | Any communication alleging a deficiency in a device after release. Much wider than a formal customer complaint. |
| Advisory notice | ISO 13485:2016 §3.1 | A notice issued after delivery giving extra information or saying what action to take. |
| Post-market surveillance | ISO 13485:2016 §3.14; EU MDR Article 2 | Systematic gathering and analysis of experience from devices on the market. |
| Incident; serious incident | EU MDR Article 2 | The events that may trigger vigilance reporting (SOP-16). |
| Field safety corrective action; field safety notice | EU MDR Article 2 | Action taken on devices already on the market for safety reasons, and the notice that communicates it. |
| Clinical evaluation | ISO 13485:2016 §3.3; EU MDR Article 2 | Assessment of clinical data to show safety and performance. |
| Performance evaluation | ISO 13485:2016 §3.13 | The equivalent assessment for in vitro diagnostic devices. |
| Risk | ISO 13485:2016 §3.17; ISO 14971 | Relates to the probability of harm and its severity. |
| Risk management | ISO 13485:2016 §3.18; ISO 14971 | The systematic process for identifying, evaluating, controlling and monitoring risk. |
| Sterile barrier system; sterile medical device | ISO 13485:2016 §3.19, §3.20 | Relevant only if you supply sterile devices. |
| Medical device file; technical documentation | ISO 13485:2016 §4.2.3; EU MDR Annexes II and III | The documentation for each device type or family. |
| Unique Device Identification (UDI) | EU MDR Article 2 and Article 27 | The identification system for devices on the market (SOP-10). |
| Nonconformity | ISO 9000:2015 §3.6.9 | A requirement not met. |
| Correction | ISO 9000:2015 §3.12.3 | Fixing a detected nonconformity, that is, the instance. |
| Corrective action | ISO 9000:2015 §3.12.2 | Removing the cause of a nonconformity so it does not happen again. |
| Preventive action | ISO 9000:2015 §3.12.1 | Removing the cause of a potential nonconformity before it happens. |
| Verification | ISO 9000:2015 §3.8.12 | Confirming that specified requirements have been met. |
| Validation | ISO 9000:2015 §3.8.13 | Confirming that the requirements for a specific intended use have been met. |

## 4. Revision History

| Rev | Date | Author | Change Summary |
|-----|------|--------|---------------|
| 1.0 | [DD/MM/YYYY] |  | Initial draft |
