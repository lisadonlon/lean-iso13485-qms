# Lean ISO 13485 QMS Template

> ⚠️ **This is a scaffold, not a compliant QMS — and not regulatory advice.** Every document is a skeleton with `[placeholders]` you must complete for your own devices, processes and scope. Used as-is, it will not pass an audit. Read [`DISCLAIMER.md`](DISCLAIMER.md) before relying on it.

A lightweight, **git-controlled** Quality Management System scaffold for medical device organisations, built in plain Markdown and [Obsidian](https://obsidian.md). Git *is* the document-control mechanism (ISO 13485:2016 §4.2.4): the `main` branch is the controlled copy and annotated tags mark approved versions.

This is the open scaffold behind a QMS I built for my own company. It gives you the **machinery** — structure, conventions, dashboards, validation and controlled-copy export — as a starting point. **You supply the content.**

## Why this exists

Most QMS tooling is heavyweight, proprietary, and hides your own documents behind a vendor. This approach keeps everything in **plain text you own**:

- **Diffable & auditable** — every change is a git commit; approvals are annotated tags. The change history *is* the §4.2.4 evidence.
- **Lightweight** — Markdown + a couple of stdlib Python scripts. No database, no lock-in.
- **Live dashboards** — Obsidian Dataview gives you a document register, overdue-review tracker, CAPA log and audit schedule with no manual upkeep.
- **Controlled-copy export** — one command produces footer-stamped, version-tagged PDFs plus a distribution record for sharing with an auditor or customer.

## What's included

| Path | Contents |
|------|----------|
| `00-dashboard/` | Dataview dashboards (register, overdue reviews, status, CAPA, audits) |
| `01-quality-manual/` | QM-01–04 skeletons (manual, policy, objectives, scope & exclusions) |
| `02-procedures/` | 16 SOP skeletons covering the ISO 13485 manufacturer scope |
| `03-work-instructions/` | (empty — add your device-specific WIs) |
| `04-forms-templates/` | FRM-01 controlled-document distribution log |
| `05-records/` | Record folders (audits, CAPA, reviews, training, complaints, changes, validation, distribution) |
| `06-isms/` | (optional — add ISO 27001 docs here if in scope) |
| `07-process-maps/` | (add Excalidraw process maps here) |
| `08-references/` | REF-01 ISO 13485 clause-to-document map |
| `_templates/` | Templater templates for every document type |
| `scripts/` | `validate_qms.py` (24-check IQ/OQ/PQ validator), `export_for_audit.py` (controlled-copy PDFs), `init_qms.py` (personalise), `qms_config.py` (config loader) |
| `qms.config.json` | Your organisation name, quality manager, standard — the one place to configure |

The SOP set is **manufacturer-aware**: it includes design & development (7.3), risk management (7.1 / ISO 14971), production (7.5) and vigilance (8.2.3) — the clauses a device manufacturer needs and that a service-provider QMS would exclude. Mark anything you don't do as N/A in `QM-04` with a justification.

## Quick start

1. **Use this template** (green button on GitHub) or `git clone` it, then `cd` into the folder.
2. Install [Obsidian](https://obsidian.md) and open the folder as a vault. Install the community plugins listed in `.obsidian/community-plugins.json` (Dataview, Templater, QuickAdd, Excalidraw, Obsidian Git, Tag Wrangler, Omnisearch).
3. **Personalise it:**
   ```bash
   python3 scripts/init_qms.py --org "Your Company Ltd" --quality-manager "Your Name"
   ```
   This sets `qms.config.json` and fills your organisation name into the document skeletons.
4. Check the machinery works:
   ```bash
   make validate-dry        # 24 checks; IQ-04 will fail until plugins are installed — expected
   ```
5. Start filling in the skeletons, beginning with `QM-04 Scope and Exclusions` (decide what applies to you) and `SOP-01 Document Control`.
6. Approve documents using the workflow in [`HOWTO.md`](HOWTO.md).

See [`HOWTO.md`](HOWTO.md) for the day-to-day operations and [`AGENTS.md`](AGENTS.md) for the conventions (also used by AI coding agents). [`CLAUDE.md`](CLAUDE.md) is a symlink to `AGENTS.md`.

## Licence

Code and templates are released under the [MIT Licence](LICENSE). You may use, adapt and redistribute the scaffold freely. The licence covers the **template** — it does not make the resulting QMS compliant; that is your responsibility.

## Maintained by

[Donlon Life Science Consulting](https://donlonlsc.com) — Lisa Donlon. Contributions and issues welcome. This template is provided as-is under the disclaimer in [`DISCLAIMER.md`](DISCLAIMER.md).
