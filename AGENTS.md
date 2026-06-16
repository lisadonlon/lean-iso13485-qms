# AGENTS.md — conventions for this QMS (humans and AI agents)

Project context and rules for anyone — or any AI coding agent (Claude Code, Codex, Cursor, Aider, etc.) — working in this repository. If you are an AI agent and you didn't read this before acting, stop and read it now.

The QMS owner / Quality Manager (named in `qms.config.json`) is the sole authority for all controlled-document decisions. An agent is an assistant, not an approver.

---

## What this repo is

A lightweight ISO 13485:2016 Quality Management System, authored in Obsidian, where **git is the document-control system** per §4.2.4. The `main` branch holds approved, controlled documents. Annotated tags of the form `{DOC-ID}-v{revision}` mark approved versions.

## What this repo is NOT

- Not a software project — it's documentation under version control. The Python in `scripts/` is tooling for the vault, not a product.
- Not a place to "improve" content unprompted. Wording and structure are deliberate. Treat approved documents as authoritative.
- Not a finished or compliant QMS — see `DISCLAIMER.md`. The documents are skeletons to be completed by the organisation.

---

## Hard rules — do not violate

1. **Never fabricate regulatory content.** Clause numbers, standard wording, guidance citations — do not invent or paraphrase. Standard text is copyright and is not stored here. If unsure, leave a `[verify: ...]` placeholder for a human to check against the source standard.

2. **Never edit a document with `status: approved`** without explicit, scoped human instruction. Approved documents change only via a Rev N+1 ceremony (see `HOWTO.md` §4). If asked to change an approved doc, confirm a revision bump is intended.

3. **Never write into these folders:**
   - `05-records/software-validation/` — written only by `scripts/validate_qms.py`
   - `05-records/distribution/` — written only by `scripts/export_for_audit.py`
   - `_archive/` — only the supersession workflow writes here
   - `.git/` — never touch directly; always go via git commands

4. **Never run state-changing operations autonomously:** `git push`, `git tag`, `git merge`, `git rebase`, `git reset`, or any `make` target that mutates state. Show the command, explain what it does, wait for confirmation.

5. **Write procedures as statements of fact — no "shall".** "Shall" is the normative verb of the *standard*, not of your own documents. State what is actually done ("The Quality Manager reviews...") or use "must". "Shall" in an SOP reads as copied-in boilerplate and invites an auditor to doubt the document is yours. Terminology otherwise follows your scope: this template is for a device **manufacturer**, so "product" and "device" are correct words (adjust if you adapt it for a service provider).

6. **Date conventions:**
   - Frontmatter: `YYYY-MM-DD` (Dataview parses this)
   - Body text: `DD/MM/YYYY`
   - Don't mix them; don't reformat existing dates.

7. **No emojis in QMS content, scripts, or tooling.**

8. **Use one consistent spelling convention** (e.g. UK or US English) across the QMS and keep to it.

---

## File map

| Folder | Contents | Edit freely? |
|---|---|---|
| `00-dashboard/` | Dataview dashboards | Yes |
| `01-quality-manual/` | QM-NN: manual, policy, objectives, scope | Only if `status: draft` |
| `02-procedures/` | SOP-NN: procedures | Only if `status: draft` |
| `03-work-instructions/` | WI-NN: work instructions | Only if `status: draft` |
| `04-forms-templates/` | FRM-NN: blank forms | Only if `status: draft` |
| `05-records/` | Completed records | See per-subfolder rules in `05-records/README.md` |
| `06-isms/` | ISMS-NN: optional ISO 27001 docs | Only if `status: draft` |
| `07-process-maps/` | Excalidraw diagrams | Don't edit binary content |
| `08-references/` | Clause maps, glossary, references | Yes, with caution on clause text |
| `_templates/` | Templater templates | Yes, with care |
| `_archive/` | Obsolete docs | Never write |
| `scripts/` | Python tooling | Yes |
| `.obsidian/` | Obsidian config | Baseline config is tracked; per-user state is gitignored |

## Doc ID prefixes

| Prefix | Folder | Type |
|---|---|---|
| QM-NN | `01-quality-manual/` | Manual, policy, objectives, scope |
| SOP-NN | `02-procedures/` | Procedures |
| WI-NN | `03-work-instructions/` | Work instructions |
| FRM-NN | `04-forms-templates/` | Blank forms |
| ISMS-NN | `06-isms/` | ISO 27001 documents |
| PM-NN | `07-process-maps/` | Process maps |
| REF-NN | `08-references/` | Reference documents |
| VAL-YYYY-NN | `05-records/software-validation/` | Validation records (script-written) |
| DIST-YYYY-NN | `05-records/distribution/` | Distribution records (script-written) |
| CAPA-YYYY-NN | `05-records/capa/` | CAPA records |

NN is a zero-padded two-digit counter. The validator enforces NN, not NNN.

---

## Frontmatter schema (18 fields, all required)

Every controlled document needs this frontmatter. The `_templates/` files generate it correctly — prefer the template over writing from memory.

```yaml
---
doc_id: SOP-01
title: Document Control
doc_type: procedure              # procedure|work-instruction|form|record|policy|manual|isms|reference|process-map
standard: ISO 13485:2016         # ISO 13485:2016|ISO 27001:2022|both
clauses: ["4.2.4"]               # array — inline preferred
revision: "1.0"
status: draft                    # draft|review|approved|obsolete
effective_date:                  # YYYY-MM-DD; blank until approved
review_due:                      # YYYY-MM-DD; blank until approved
review_interval: 12              # months
author:
reviewer:
approver:
approved_date:                   # YYYY-MM-DD; blank until approved
change_summary: "Initial draft"
tags: [qms, procedure]
supersedes:                      # doc_id of replaced version, or blank
related: []                      # array of related doc_ids
---
```

Conventions:
- `status: approved` requires `effective_date`, `review_due` and `approved_date` all populated.
- `revision` is a string (`"1.0"` not `1.0`) — YAML reads bare `1.0` as a float.
- `clauses` and `related` must be arrays; inline form is canonical.

---

## Tooling — use these, don't reinvent

| Command | Purpose |
|---|---|
| `make validate` | Run the 24-check validation, write a VAL record |
| `make validate-dry` | Same without writing the record |
| `make export` | Generate controlled-copy PDFs + a DIST record |
| `make export-test` | Same without the DIST record |
| `make status` | Branch + dirty files + last commit + tags at HEAD |
| `make approved` | List documents with `status: approved` |
| `make draft DOC=SOP-XX REV=1.1` | Create a draft branch for a revision |
| `make approve DOC=SOP-XX REV=1.0` | Create an annotated tag on HEAD |
| `make push` | `git push --follow-tags` |
| `python3 scripts/init_qms.py` | Personalise the template (org name etc.) |

Python tooling in `scripts/` is stdlib-only by design (`export_for_audit.py` shells out to pandoc/weasyprint rather than importing them). Maintain that discipline. Organisation/quality-manager names come from `qms.config.json` via `qms_config.py` — don't hard-code them.

The 24 checks are split IQ (installation: folders, git, plugins, templates), OQ (operational: template/dashboard configuration), PQ (performance: live content matches schema, working tree clean, approved docs tagged). When adding a check, classify it as IQ/OQ/PQ, follow the `iq_NN_*`/`oq_NN_*`/`pq_NN_*` naming, place it in numeric order within its phase, and update the count in the docstring and `main()`.

---

## Commit and tag conventions

| Situation | Format | Example |
|---|---|---|
| Draft work | `{doc_id}: draft - {description}` | `SOP-01: draft - section 6 wording` |
| Approval | `{doc_id}: approve - Rev {x.y} {description}` | `SOP-01: approve - Rev 1.0 initial release` |
| Obsoleting | `{doc_id}: obsolete - {reason}` | `SOP-07: obsolete - superseded by Rev 2.0` |
| Records | `record: {doc-id} {description}` | `record: VAL-2026-01 validation evidence` |
| Tooling | `tooling: {description}` | `tooling: add export script` |
| Housekeeping | `chore: {description}` | `chore: gitignore per-user config` |

Tags: `{DOC-ID}-v{revision}` (e.g. `SOP-01-v1.0`). Always annotated (`git tag -a`), never lightweight — annotated tags carry the tagger, date and message that constitute approval evidence.

---

## Anti-patterns (don't)

- Don't "improve" wording in approved documents — that's a deliberate, human-initiated revision.
- Don't add new Python dependencies — keep the validator stdlib-only.
- Don't generate fictional clause text or standard quotes — name the clause, don't quote it.
- Don't run git operations autonomously — show, explain, wait.
- Don't write large documents end-to-end without review — section by section.
- Don't reformat existing files as a side effect of an edit — match the existing style.

When stuck: read the relevant SOP, read `HOWTO.md` for operations, and ask the human. A `[verify: ...]` placeholder beats a confident guess.
