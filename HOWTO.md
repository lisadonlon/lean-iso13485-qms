# QMS — How To Guide

Everyday-language walkthrough of the routine operations. Pair this with `AGENTS.md` (schema and rules) and `SOP-01 Document Control` (the formal procedure this implements).

---

## Contents

1. [One-time setup](#1-one-time-setup)
2. [Daily rhythm](#2-daily-rhythm)
3. [Approving a new document (Rev 1.0)](#3-approving-a-new-document-rev-10)
4. [Revising an approved document (Rev 1.0 → 1.1)](#4-revising-an-approved-document)
5. [Sharing controlled documents with an auditor](#5-sharing-with-an-auditor)
6. [When something goes wrong](#6-when-something-goes-wrong)

---

## 1. One-time setup

### Tools

| Tool | Purpose | Install |
|---|---|---|
| Git | Version control / document control | Pre-installed on macOS/Linux, or via your package manager |
| Python 3.9+ | Validation and export scripts | Usually pre-installed |
| Make | Workflow shortcuts | Usually pre-installed |
| Pandoc | Markdown → HTML during PDF export | `brew install pandoc` |
| WeasyPrint | HTML → PDF | `pip3 install weasyprint --break-system-packages` |
| Obsidian | Authoring environment | [obsidian.md](https://obsidian.md) |

### Obsidian plugins (Settings → Community plugins → Browse)

Dataview, Templater, QuickAdd, Excalidraw, Obsidian Git, Tag Wrangler, Omnisearch. The list lives in `.obsidian/community-plugins.json`. Until they're installed, the validator's IQ-04 check will fail — that's expected.

In **Obsidian Git** settings, set all auto-commit / auto-push / auto-pull intervals to `0` so the plugin doesn't fight your manual git work.

### Personalise the template

```bash
python3 scripts/init_qms.py --org "Your Company Ltd" --quality-manager "Your Name"
```

### Load the shell aliases (optional)

```bash
echo '[ -f "'"$PWD"'/qms-aliases.zsh" ] && source "'"$PWD"'/qms-aliases.zsh"' >> ~/.zshrc
source ~/.zshrc
qms-help
```

---

## 2. Daily rhythm

Most days you're just writing or editing. No ceremony needed.

1. Edit notes in Obsidian; save as normal.
2. Check git state periodically: `make status` (or `qms-status`).
3. Commit work-in-progress on a draft branch if you want incremental history.

Remember while editing:
- Frontmatter dates are `YYYY-MM-DD`; body-text dates are `DD/MM/YYYY`.
- Write procedures as statements of what is done — avoid "shall" (use "must", or just state the fact). "Shall" is the standard's verb, not yours.
- Don't leave `[placeholder]` markers in a document you're about to approve.

---

## 3. Approving a new document (Rev 1.0)

The full §4.2.4 ceremony, for releasing a document at Rev 1.0. Allow ~10 minutes. Fully quit Obsidian first if its Git plugin is active.

1. **Check it's ready** — all sections filled, no leftover `[placeholders]`, revision-history row present.
2. **Set the frontmatter for approval:**
   ```yaml
   status: approved
   effective_date: 2026-01-15      # today, YYYY-MM-DD
   review_due: 2027-01-15          # + review_interval months
   approved_date: 2026-01-15
   change_summary: Initial release
   ```
3. **Update the revision-history table** (body date `DD/MM/YYYY`).
4. **Check the working tree** — `make status` should show only the doc you're approving. Commit anything unrelated separately first.
5. **Commit the document alone:**
   ```bash
   git add "02-procedures/SOP-XX Title.md"
   git commit -m "SOP-XX: approve - Rev 1.0 initial release"
   ```
6. **Tag the approval:**
   ```bash
   make approve DOC=SOP-XX REV=1.0
   ```
   This creates an annotated tag `SOP-XX-v1.0` carrying approver, date and message.
7. **Push** commit + tag: `make push`.
8. **Run validation** to produce the VAL record: `make validate` (expect 24/24, allowing for IQ-04 if plugins aren't installed on this machine).
9. **Commit the VAL record:**
   ```bash
   git add 05-records/software-validation/
   git commit -m "record: VAL-YYYY-NN validation evidence for SOP-XX Rev 1.0"
   make push
   ```

The document is now the controlled, approved version. The tag captures its exact state; the VAL record shows the QMS was healthy at approval time.

---

## 4. Revising an approved document

Change an approved document by creating a new revision, never by editing the approved version in place.

- **Minor** (wording, clarification): 1.0 → 1.1
- **Significant** (new sections, changed scope/process): 1.0 → 2.0

1. **Start a draft branch:** `make draft DOC=SOP-XX REV=1.1`
2. **Edit** the document; set `revision: "1.1"`, `status: draft`, blank the dates, update `change_summary`, and add a revision-history row.
3. **Commit work-in-progress** on the draft branch as you go.
4. **Merge to main** when ready:
   ```bash
   git checkout main
   git merge --no-ff draft/SOP-XX-v1.1 -m "SOP-XX: merge draft for Rev 1.1 approval"
   ```
5. **Follow the approval ceremony** (§3 from step 2): set approved, populate dates, commit alone, `make approve DOC=SOP-XX REV=1.1`, push, validate.

The old `SOP-XX-v1.0` tag still points at the original; the new `SOP-XX-v1.1` tag is the current controlled version.

---

## 5. Sharing with an auditor

Don't give external parties git access. Generate a PDF snapshot instead.

1. **Get your house in order:** `make status` (clean tree) and `make validate-dry` (passing).
2. **Export:** `make export`. This produces:
   - a folder of PDFs at `../qms-publish/` — one per approved document, organised by folder, plus `INDEX.pdf` and `manifest.csv`;
   - a distribution record at `05-records/distribution/DIST-YYYY-NN.md` with git SHA, tags, file hashes, and a recipient block.
3. **Upload** the `qms-publish/` folder to a view-only location (e.g. a Google Drive folder set to Viewer). Copy the link.
4. **Log it** in `04-forms-templates/FRM-01 Controlled Document Distribution Log.md` and fill in section 4 of the matching `DIST-YYYY-NN.md`.
5. **Commit** the updated records.
6. **When access ends**, revoke the link and record the **Access withdrawn** date in FRM-01.

---

## 6. When something goes wrong

**"Another git process seems to be running" / stale lock** — quit Obsidian fully, then `find .git -name "*.lock"` and remove any that exist, then retry.

**`command not found: qms-...`** — the aliases aren't loaded: `source ~/.zshrc` or open a new terminal.

**Validation failures** — read each `->` detail line:

| Check | Meaning | Fix |
|---|---|---|
| IQ-04 | A required plugin directory is missing | Install the plugin in Obsidian (expected on a fresh clone) |
| PQ-01 | A document is missing frontmatter fields | Open it, complete the 18 fields |
| PQ-06 | A date isn't `YYYY-MM-DD` | Fix the frontmatter date |
| PQ-07 | Working tree has uncommitted changes | Commit or stash, re-run |
| PQ-09 | An approved doc has no matching annotated tag | `make approve DOC=... REV=...` |

Real, persistent failures should be raised as CAPAs — that's the audit-quality way to track them.

**PDF export dependency errors** — the script tells you what's missing: `brew install pandoc`, `pip3 install weasyprint --break-system-packages`, and on some systems `brew install pango libffi`.
