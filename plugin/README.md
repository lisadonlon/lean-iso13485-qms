# Micro QMS - Obsidian plugin

Build a lean ISO 13485:2016 quality management system in an Obsidian vault,
on a shared drive or under git. The plugin scaffolds the vault from the
document skeletons in this repository, personalises them through a guided
setup wizard, and manages the document lifecycle (draft, review, approved,
obsolete) without requiring a terminal.

This plugin is tooling for the QMS template, not a controlled document. Read
`../DISCLAIMER.md`: the output is a scaffold to be completed by your
organisation, not a compliant QMS.

## What it does

- **Setup wizard** - asks about your company (organisation, quality manager,
  sites, device types, regulatory role, markets) and your scope (design,
  sterilisation, process validation, contamination control, customer
  property, preservation, measuring equipment, installation, servicing,
  software, outsourcing, ISMS). Answers are stored in `qms.config.json`, so
  the wizard can be re-run at any time without losing work.
- **Scaffolding** - creates the folder tree and all template documents,
  fills the `{{TOKEN}}` placeholders, and completes the QM-04 applicability
  table. Clauses answered "no" are recorded as not applicable with your
  justification; the corresponding documents are still created and carry an
  applicability callout, because ISO 13485 section 1.2 exclusions are
  documented, never hidden.
- **Document lifecycle** - commands to submit for review, approve (setting
  approver, approved date, effective date, and the computed review-due
  date), start a new revision (archiving the superseded revision to
  `_archive/`), and mark obsolete.
- **Two document-control modes** - on a shared drive the plugin manages
  status and archiving itself. In a git vault, approval remains the
  annotated-tag ceremony: the approve command shows the exact `make`
  commands instead of changing files silently.
- **Health check** - an in-vault subset of the repository's 24-check
  validation (folders, frontmatter schema, dates, approved-document
  completeness, overdue reviews). The Python validator
  (`../scripts/validate_qms.py`) remains the authoritative, record-producing
  validation.

## Build

Requires Node 18+.

```bash
cd plugin
npm install
npm run build
```

The build first harvests the repository's documents into
`src/generated/templates.ts` (gitignored), then bundles `main.js`. The
harvest commit is shown in the plugin's settings tab so you can trace which
template revision scaffolded a vault.

## Install into a vault (sideload)

Copy three files into the target vault:

```bash
mkdir -p "<vault>/.obsidian/plugins/micro-qms"
cp manifest.json main.js styles.css "<vault>/.obsidian/plugins/micro-qms/"
```

Then in Obsidian: Settings, Community plugins, enable "Micro QMS", and run
"Micro QMS: Run setup wizard" from the command palette.

For dashboards, install Dataview (and Templater for the document templates);
the health check will remind you.

## Companion Claude skill

`../skills/qms-interview/` goes beyond the wizard: a structured interview
about your devices and processes that drafts the document content itself,
section by section, under your review. See its `SKILL.md`.
