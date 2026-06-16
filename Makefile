# QMS — common commands
#
# Run from the vault root (where this file lives). Works equally well from
# a standard macOS terminal or the Obsidian Terminal plugin pane.
#
# Type `make help` to list available targets.

.DEFAULT_GOAL := help
.PHONY: help validate validate-dry export export-test status log tags \
        approve push draft approved dirty-check

# Override with `make approve APPROVER="Someone Else"` if delegated.
APPROVER ?= Quality Manager
TODAY    := $(shell date +%Y-%m-%d)

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------

help:  ## Show available targets
	@echo "QMS — common commands"
	@echo ""
	@echo "Validation:"
	@echo "  make validate              Run QMS validation, write VAL record"
	@echo "  make validate-dry          Dry-run validation, no record written"
	@echo ""
	@echo "Audit export (auditor PDF snapshot):"
	@echo "  make export                Generate PDFs + DIST record (for a real share)"
	@echo "  make export-test           Generate PDFs only, no DIST record (for testing)"
	@echo ""
	@echo "Git workflow:"
	@echo "  make status                Branch + dirty files + last commit + tags at HEAD"
	@echo "  make log                   Last 10 commits"
	@echo "  make tags                  List every tag"
	@echo "  make approved              List documents with status: approved"
	@echo "  make push                  Push commits + annotated tags"
	@echo "  make dirty-check           Fail if working tree has uncommitted changes"
	@echo ""
	@echo "Document control ceremonies:"
	@echo "  make draft DOC=SOP-01 REV=1.1"
	@echo "                             Create branch draft/SOP-01-v1.1 and switch to it"
	@echo "  make approve DOC=SOP-01 REV=1.0"
	@echo "                             Create annotated tag SOP-01-v1.0 on HEAD"
	@echo ""
	@echo "Tip: target arguments use uppercase NAME=value form, e.g."
	@echo "     make approve DOC=SOP-02 REV=1.0"

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

validate:
	python3 scripts/validate_qms.py

validate-dry:
	python3 scripts/validate_qms.py --dry-run

# ---------------------------------------------------------------------------
# Audit export
# ---------------------------------------------------------------------------

export:
	python3 scripts/export_for_audit.py

export-test:
	python3 scripts/export_for_audit.py --skip-record

# ---------------------------------------------------------------------------
# Git workflow
# ---------------------------------------------------------------------------

status:
	@echo "Branch and status:"
	@git status -sb
	@echo ""
	@echo "Last commit:"
	@git log -1 --oneline
	@echo ""
	@echo "Tags at HEAD:"
	@git tag --points-at HEAD || true

log:
	@git log --oneline -10

tags:
	@git tag --list | sort

approved:
	@echo "Documents with status: approved (per frontmatter):"
	@grep -l "^status: approved$$" \
	    01-quality-manual/*.md \
	    02-procedures/*.md \
	    03-work-instructions/*.md \
	    04-forms-templates/*.md \
	    06-isms/*.md 2>/dev/null | sort || echo "  (none)"

push:
	git push --follow-tags

dirty-check:
	@if [ -n "$$(git status --porcelain)" ]; then \
	    echo "ERROR: working tree has uncommitted changes:"; \
	    git status -s; \
	    exit 1; \
	fi
	@echo "Working tree clean."

# ---------------------------------------------------------------------------
# Document control ceremonies
# ---------------------------------------------------------------------------

draft:
	@if [ -z "$(DOC)" ] || [ -z "$(REV)" ]; then \
	    echo "Usage: make draft DOC=SOP-XX REV=X.Y"; \
	    echo "Example: make draft DOC=SOP-01 REV=1.1"; \
	    exit 1; \
	fi
	git checkout -b draft/$(DOC)-v$(REV)
	@echo ""
	@echo "Now on branch draft/$(DOC)-v$(REV). When ready to release:"
	@echo "  1. Edit the document, bump revision in frontmatter, update revision history"
	@echo "  2. git add <file> && git commit -m \"$(DOC): approve - Rev $(REV) ...\""
	@echo "  3. git checkout main && git merge --no-ff draft/$(DOC)-v$(REV)"
	@echo "  4. make approve DOC=$(DOC) REV=$(REV)"
	@echo "  5. make push"

approve:
	@if [ -z "$(DOC)" ] || [ -z "$(REV)" ]; then \
	    echo "Usage: make approve DOC=SOP-XX REV=X.Y"; \
	    echo "Example: make approve DOC=SOP-01 REV=1.0"; \
	    exit 1; \
	fi
	@echo "About to tag HEAD as: $(DOC)-v$(REV)"
	@echo "Approver: $(APPROVER)"
	@echo "Date:     $(TODAY)"
	@echo "Commit being tagged:"
	@git log -1 --oneline
	@echo ""
	git tag -a $(DOC)-v$(REV) -m "$(DOC) Rev $(REV) approved by $(APPROVER) on $(TODAY)"
	@echo ""
	@echo "Tag created. Push with: make push"
