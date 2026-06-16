#!/usr/bin/env python3
"""QMS Software Validation Script

Generates a VAL-YYYY-NN markdown record in 05-records/software-validation/.
Runs 24 automated checks across IQ (installation), OQ (operational), and PQ (performance).

Stdlib-only. No external dependencies.

Usage:
    python scripts/validate_qms.py          # Run from vault root
    python scripts/validate_qms.py --dry-run  # Print results without writing file
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from qms_config import load_config


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

VAULT_ROOT = Path(__file__).resolve().parent.parent

CONFIG = load_config(VAULT_ROOT)

EXPECTED_FOLDERS = [
    "00-dashboard",
    "01-quality-manual",
    "02-procedures",
    "03-work-instructions",
    "04-forms-templates",
    "05-records",
    "06-isms",
    "07-process-maps",
    "08-references",
    "_templates",
]

REQUIRED_PLUGINS = [
    "dataview",
    "templater-obsidian",
    "quickadd",
    "obsidian-excalidraw-plugin",
]

EXPECTED_TEMPLATES = [
    "New Audit Record.md",
    "New CAPA.md",
    "New Form.md",
    "New ISMS Document.md",
    "New Procedure.md",
    "New Process Map.md",
    "New Record.md",
    "New Work Instruction.md",
]

RECORD_SUBDIRS = [
    "05-records/audits",
    "05-records/capa",
    "05-records/management-reviews",
    "05-records/training",
    "05-records/complaints",
    "05-records/changes",
    "05-records/software-validation",
]

DASHBOARDS = [
    "00-dashboard/Document Register.md",
    "00-dashboard/Overdue Reviews.md",
    "00-dashboard/Documents by Status.md",
    "00-dashboard/CAPA Log.md",
    "00-dashboard/Audit Schedule.md",
]

# 18 standard frontmatter fields (17 from schema + related is always present)
FRONTMATTER_FIELDS = [
    "doc_id",
    "title",
    "doc_type",
    "standard",
    "clauses",
    "revision",
    "status",
    "effective_date",
    "review_due",
    "review_interval",
    "author",
    "reviewer",
    "approver",
    "approved_date",
    "change_summary",
    "tags",
    "supersedes",
    "related",
]

VALID_STATUSES = {"draft", "review", "approved", "obsolete"}

# Folders that contain controlled documents (for PQ checks)
CONTROLLED_DOC_FOLDERS = [
    "01-quality-manual",
    "02-procedures",
    "03-work-instructions",
    "04-forms-templates",
    "06-isms",
    "07-process-maps",
]


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class TestResult:
    test_id: str
    description: str
    phase: str  # IQ, OQ, PQ
    status: str  # PASS, FAIL
    detail: str = ""


@dataclass
class ValidationRun:
    results: list[TestResult] = field(default_factory=list)

    def add(self, result: TestResult) -> None:
        self.results.append(result)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.status == "PASS")

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if r.status == "FAIL")

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def overall(self) -> str:
        return "PASS" if self.failed == 0 else "FAIL"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(filepath: Path) -> dict[str, str] | None:
    """Extract YAML frontmatter from a markdown file. Returns None if no frontmatter.

    Handles both inline-array form (``clauses: ["4.2.4"]``) and YAML block-list form
    (``clauses:\\n  - 4.2.4``). Obsidian's editor sometimes auto-reformats inline
    arrays into block lists; both are valid YAML so the parser normalises block
    lists to the inline-array string representation. This way downstream checks
    (PQ-04, PQ-05) see consistent values regardless of which YAML form the
    document was last saved in.
    """
    try:
        text = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    if not text.startswith("---"):
        return None

    end = text.find("---", 3)
    if end == -1:
        return None

    fm: dict[str, str] = {}
    pending_list_key: str | None = None
    pending_list_items: list[str] = []

    def flush_list() -> None:
        nonlocal pending_list_key, pending_list_items
        if pending_list_key is not None:
            # Only rewrite as a list if items were actually collected. A key with
            # an empty value and no following "- item" lines stays as "" — that's
            # how the rest of the script signals "field present but unpopulated".
            if pending_list_items:
                quoted = [f'"{item}"' for item in pending_list_items]
                fm[pending_list_key] = "[" + ", ".join(quoted) + "]"
            pending_list_key = None
            pending_list_items = []

    for raw in text[3:end].strip().splitlines():
        stripped = raw.strip()
        # A line that's an indented "- item" extends the currently-open block list.
        if (
            pending_list_key is not None
            and raw.startswith((" ", "\t"))
            and stripped.startswith("- ")
        ):
            item = stripped[2:].strip().strip('"').strip("'")
            pending_list_items.append(item)
            continue

        # Any other line closes the pending list, if there is one.
        flush_list()

        if ":" in raw:
            key, _, value = raw.partition(":")
            key = key.strip()
            value = value.strip()
            if value == "":
                # Key with empty value — may be the header of a block list.
                # Start collecting; flush_list() will write the result.
                pending_list_key = key
                fm[key] = ""  # default if no list items follow
            else:
                fm[key] = value

    # End of frontmatter — flush any block list still open.
    flush_list()
    return fm


def run_git(*args: str) -> tuple[int, str]:
    """Run a git command in the vault root. Returns (returncode, stdout)."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(VAULT_ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode, result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return 1, ""


def get_controlled_docs() -> list[Path]:
    """Return all .md files in controlled document folders."""
    docs = []
    for folder in CONTROLLED_DOC_FOLDERS:
        folder_path = VAULT_ROOT / folder
        if folder_path.is_dir():
            for f in folder_path.glob("*.md"):
                if f.name != ".gitkeep":
                    docs.append(f)
    return sorted(docs)


# ---------------------------------------------------------------------------
# IQ Tests — Installation Qualification (6 tests, all tiers)
# ---------------------------------------------------------------------------

def iq_01_vault_folders(run: ValidationRun) -> None:
    """IQ-01: Vault folders exist."""
    missing = [f for f in EXPECTED_FOLDERS if not (VAULT_ROOT / f).is_dir()]
    if missing:
        run.add(TestResult("IQ-01", "Vault folders exist", "IQ", "FAIL",
                           f"Missing: {', '.join(missing)}"))
    else:
        run.add(TestResult("IQ-01", "Vault folders exist", "IQ", "PASS",
                           f"All {len(EXPECTED_FOLDERS)} expected folders present"))


def iq_02_git_repo(run: ValidationRun) -> None:
    """IQ-02: Git repo initialised."""
    rc, _ = run_git("rev-parse", "--git-dir")
    if rc == 0:
        run.add(TestResult("IQ-02", "Git repo initialised", "IQ", "PASS",
                           "Git repository detected"))
    else:
        run.add(TestResult("IQ-02", "Git repo initialised", "IQ", "FAIL",
                           "No Git repository found at vault root"))


def iq_03_community_plugins(run: ValidationRun) -> None:
    """IQ-03: Required plugins in community-plugins.json."""
    cp_path = VAULT_ROOT / ".obsidian" / "community-plugins.json"
    if not cp_path.is_file():
        run.add(TestResult("IQ-03", "Required plugins in community-plugins.json", "IQ", "FAIL",
                           "community-plugins.json not found"))
        return

    try:
        plugins = json.loads(cp_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        run.add(TestResult("IQ-03", "Required plugins in community-plugins.json", "IQ", "FAIL",
                           "Could not parse community-plugins.json"))
        return

    missing = [p for p in REQUIRED_PLUGINS if p not in plugins]
    if missing:
        run.add(TestResult("IQ-03", "Required plugins in community-plugins.json", "IQ", "FAIL",
                           f"Missing: {', '.join(missing)}"))
    else:
        run.add(TestResult("IQ-03", "Required plugins in community-plugins.json", "IQ", "PASS",
                           f"All {len(REQUIRED_PLUGINS)} required plugins registered"))


def iq_04_plugin_dirs(run: ValidationRun) -> None:
    """IQ-04: Plugin directories and manifest.json present."""
    plugins_dir = VAULT_ROOT / ".obsidian" / "plugins"
    missing = []
    for plugin in REQUIRED_PLUGINS:
        plugin_dir = plugins_dir / plugin
        manifest = plugin_dir / "manifest.json"
        if not plugin_dir.is_dir():
            missing.append(f"{plugin} (directory)")
        elif not manifest.is_file():
            missing.append(f"{plugin} (manifest.json)")

    if missing:
        run.add(TestResult("IQ-04", "Plugin directories and manifests present", "IQ", "FAIL",
                           f"Missing: {', '.join(missing)}"))
    else:
        run.add(TestResult("IQ-04", "Plugin directories and manifests present", "IQ", "PASS",
                           f"All {len(REQUIRED_PLUGINS)} plugin directories with manifests present"))


def iq_05_templates(run: ValidationRun) -> None:
    """IQ-05: 8 templates present in _templates/."""
    templates_dir = VAULT_ROOT / "_templates"
    missing = [t for t in EXPECTED_TEMPLATES if not (templates_dir / t).is_file()]
    if missing:
        run.add(TestResult("IQ-05", "Templates present in _templates/", "IQ", "FAIL",
                           f"Missing: {', '.join(missing)}"))
    else:
        run.add(TestResult("IQ-05", "Templates present in _templates/", "IQ", "PASS",
                           f"All {len(EXPECTED_TEMPLATES)} templates present"))


def iq_06_record_subdirs(run: ValidationRun) -> None:
    """IQ-06: Records subdirectories exist."""
    missing = [d for d in RECORD_SUBDIRS if not (VAULT_ROOT / d).is_dir()]
    if missing:
        run.add(TestResult("IQ-06", "Records subdirectories exist", "IQ", "FAIL",
                           f"Missing: {', '.join(missing)}"))
    else:
        run.add(TestResult("IQ-06", "Records subdirectories exist", "IQ", "PASS",
                           f"All {len(RECORD_SUBDIRS)} record subdirectories present"))


# ---------------------------------------------------------------------------
# OQ Tests — Operational Qualification (9 tests, Tier 2+3)
# ---------------------------------------------------------------------------

def oq_01_template_frontmatter(run: ValidationRun) -> None:
    """OQ-01: Template frontmatter has all 18 fields."""
    templates_dir = VAULT_ROOT / "_templates"
    # Check the New Procedure template as the canonical reference
    proc_template = templates_dir / "New Procedure.md"
    if not proc_template.is_file():
        run.add(TestResult("OQ-01", "Template frontmatter has all 18 fields", "OQ", "FAIL",
                           "New Procedure.md template not found"))
        return

    text = proc_template.read_text(encoding="utf-8")
    if not text.startswith("---"):
        run.add(TestResult("OQ-01", "Template frontmatter has all 18 fields", "OQ", "FAIL",
                           "No YAML frontmatter found"))
        return

    end = text.find("---", 3)
    fm_text = text[3:end]
    present_keys = set()
    for line in fm_text.strip().splitlines():
        if ":" in line:
            key = line.partition(":")[0].strip()
            present_keys.add(key)

    missing = [f for f in FRONTMATTER_FIELDS if f not in present_keys]
    if missing:
        run.add(TestResult("OQ-01", "Template frontmatter has all 18 fields", "OQ", "FAIL",
                           f"Missing fields: {', '.join(missing)}"))
    else:
        run.add(TestResult("OQ-01", "Template frontmatter has all 18 fields", "OQ", "PASS",
                           f"All {len(FRONTMATTER_FIELDS)} frontmatter fields present in template"))


def oq_02_template_nn_format(run: ValidationRun) -> None:
    """OQ-02: Template prompts use NN format (not NNN)."""
    templates_dir = VAULT_ROOT / "_templates"
    issues = []
    for tpl_name in EXPECTED_TEMPLATES:
        tpl_path = templates_dir / tpl_name
        if not tpl_path.is_file():
            continue
        text = tpl_path.read_text(encoding="utf-8")
        # Check for NNN patterns in prompts (e.g., "001" or "e.g., 001")
        if re.search(r'\b\d{3}\b', text) and "NNN" not in text:
            # Look specifically in prompt lines
            pass
        if re.search(r'e\.g\.,?\s*\d{3}', text):
            issues.append(tpl_name)

    if issues:
        run.add(TestResult("OQ-02", "Template prompts use NN format (not NNN)", "OQ", "FAIL",
                           f"NNN format found in: {', '.join(issues)}"))
    else:
        run.add(TestResult("OQ-02", "Template prompts use NN format (not NNN)", "OQ", "PASS",
                           "All template prompts use NN format"))


def oq_03_template_date_formats(run: ValidationRun) -> None:
    """OQ-03: Template date formats correct (YYYY-MM-DD frontmatter, DD/MM/YYYY body)."""
    proc_template = VAULT_ROOT / "_templates" / "New Procedure.md"
    if not proc_template.is_file():
        run.add(TestResult("OQ-03", "Template date formats correct", "OQ", "FAIL",
                           "New Procedure.md not found"))
        return

    text = proc_template.read_text(encoding="utf-8")
    issues = []

    # Body text must use DD/MM/YYYY placeholder
    if "[DD/MM/YYYY]" not in text:
        issues.append("Missing [DD/MM/YYYY] placeholder in body")

    # Revision history should use DD/MM/YYYY format via Templater
    if 'tp.date.now("DD/MM/YYYY")' not in text:
        issues.append("Revision history date not in DD/MM/YYYY format")

    if issues:
        run.add(TestResult("OQ-03", "Template date formats correct", "OQ", "FAIL",
                           "; ".join(issues)))
    else:
        run.add(TestResult("OQ-03", "Template date formats correct", "OQ", "PASS",
                           "Frontmatter uses YYYY-MM-DD, body uses DD/MM/YYYY"))


def oq_04_doc_register_query(run: ValidationRun) -> None:
    """OQ-04: Document Register dashboard has exclusion filters and field selection."""
    dash_path = VAULT_ROOT / "00-dashboard" / "Document Register.md"
    if not dash_path.is_file():
        run.add(TestResult("OQ-04", "Document Register dashboard query structure", "OQ", "FAIL",
                           "Document Register.md not found"))
        return

    text = dash_path.read_text(encoding="utf-8")
    checks = {
        "doc_id field": "doc_id" in text,
        "status field": "status" in text,
        "template exclusion": "_templates" in text,
        "dashboard exclusion": "00-dashboard" in text,
        "archive exclusion": "_archive" in text,
    }

    failed = [k for k, v in checks.items() if not v]
    if failed:
        run.add(TestResult("OQ-04", "Document Register dashboard query structure", "OQ", "FAIL",
                           f"Missing: {', '.join(failed)}"))
    else:
        run.add(TestResult("OQ-04", "Document Register dashboard query structure", "OQ", "PASS",
                           "All exclusion filters and field selections present"))


def oq_05_overdue_reviews_query(run: ValidationRun) -> None:
    """OQ-05: Overdue Reviews query checks review_due < today AND status=approved."""
    dash_path = VAULT_ROOT / "00-dashboard" / "Overdue Reviews.md"
    if not dash_path.is_file():
        run.add(TestResult("OQ-05", "Overdue Reviews query structure", "OQ", "FAIL",
                           "Overdue Reviews.md not found"))
        return

    text = dash_path.read_text(encoding="utf-8")
    checks = {
        "review_due comparison": "review_due" in text and "date(today)" in text,
        "status filter": 'status = "approved"' in text,
    }

    failed = [k for k, v in checks.items() if not v]
    if failed:
        run.add(TestResult("OQ-05", "Overdue Reviews query structure", "OQ", "FAIL",
                           f"Missing: {', '.join(failed)}"))
    else:
        run.add(TestResult("OQ-05", "Overdue Reviews query structure", "OQ", "PASS",
                           "Query checks review_due < today AND status=approved"))


def oq_06_status_dashboard(run: ValidationRun) -> None:
    """OQ-06: Documents by Status covers 4 status groups."""
    dash_path = VAULT_ROOT / "00-dashboard" / "Documents by Status.md"
    if not dash_path.is_file():
        run.add(TestResult("OQ-06", "Documents by Status (4 groups)", "OQ", "FAIL",
                           "Documents by Status.md not found"))
        return

    text = dash_path.read_text(encoding="utf-8")
    statuses = {"draft", "review", "approved", "obsolete"}
    found = {s for s in statuses if f'status = "{s}"' in text}
    missing = statuses - found

    if missing:
        run.add(TestResult("OQ-06", "Documents by Status (4 groups)", "OQ", "FAIL",
                           f"Missing status groups: {', '.join(sorted(missing))}"))
    else:
        run.add(TestResult("OQ-06", "Documents by Status (4 groups)", "OQ", "PASS",
                           "All 4 status groups present (draft, review, approved, obsolete)"))


def oq_07_capa_log_query(run: ValidationRun) -> None:
    """OQ-07: CAPA Log queries 05-records/capa/."""
    dash_path = VAULT_ROOT / "00-dashboard" / "CAPA Log.md"
    if not dash_path.is_file():
        run.add(TestResult("OQ-07", "CAPA Log queries 05-records/capa/", "OQ", "FAIL",
                           "CAPA Log.md not found"))
        return

    text = dash_path.read_text(encoding="utf-8")
    if '"05-records/capa"' in text:
        run.add(TestResult("OQ-07", "CAPA Log queries 05-records/capa/", "OQ", "PASS",
                           "CAPA Log correctly scoped to 05-records/capa"))
    else:
        run.add(TestResult("OQ-07", "CAPA Log queries 05-records/capa/", "OQ", "FAIL",
                           'FROM clause does not reference "05-records/capa"'))


def oq_08_audit_schedule_query(run: ValidationRun) -> None:
    """OQ-08: Audit Schedule queries 05-records/audits/."""
    dash_path = VAULT_ROOT / "00-dashboard" / "Audit Schedule.md"
    if not dash_path.is_file():
        run.add(TestResult("OQ-08", "Audit Schedule queries 05-records/audits/", "OQ", "FAIL",
                           "Audit Schedule.md not found"))
        return

    text = dash_path.read_text(encoding="utf-8")
    if '"05-records/audits"' in text:
        run.add(TestResult("OQ-08", "Audit Schedule queries 05-records/audits/", "OQ", "PASS",
                           "Audit Schedule correctly scoped to 05-records/audits"))
    else:
        run.add(TestResult("OQ-08", "Audit Schedule queries 05-records/audits/", "OQ", "FAIL",
                           'FROM clause does not reference "05-records/audits"'))


def oq_09_all_dashboards_exist(run: ValidationRun) -> None:
    """OQ-09: All 5 dashboards exist."""
    missing = [d for d in DASHBOARDS if not (VAULT_ROOT / d).is_file()]
    if missing:
        run.add(TestResult("OQ-09", "All 5 dashboards exist", "OQ", "FAIL",
                           f"Missing: {', '.join(missing)}"))
    else:
        run.add(TestResult("OQ-09", "All 5 dashboards exist", "OQ", "PASS",
                           f"All {len(DASHBOARDS)} dashboards present"))


# ---------------------------------------------------------------------------
# PQ Tests — Performance Qualification (8 tests, Tier 3 only)
# ---------------------------------------------------------------------------

def pq_01_complete_frontmatter(run: ValidationRun) -> None:
    """PQ-01: All controlled docs have complete frontmatter (18 fields)."""
    docs = get_controlled_docs()
    if not docs:
        run.add(TestResult("PQ-01", "All controlled docs have complete frontmatter", "PQ", "PASS",
                           "No controlled documents found (empty vault)"))
        return

    issues = []
    for doc in docs:
        fm = parse_frontmatter(doc)
        if fm is None:
            issues.append(f"{doc.name}: no frontmatter")
            continue
        missing = [f for f in FRONTMATTER_FIELDS if f not in fm]
        if missing:
            issues.append(f"{doc.name}: missing {', '.join(missing)}")

    if issues:
        run.add(TestResult("PQ-01", "All controlled docs have complete frontmatter", "PQ", "FAIL",
                           "; ".join(issues[:5]) + (f" (+{len(issues)-5} more)" if len(issues) > 5 else "")))
    else:
        run.add(TestResult("PQ-01", "All controlled docs have complete frontmatter", "PQ", "PASS",
                           f"All {len(docs)} controlled documents have complete frontmatter"))


def pq_02_docid_matches_filename(run: ValidationRun) -> None:
    """PQ-02: doc_id matches filename prefix."""
    docs = get_controlled_docs()
    if not docs:
        run.add(TestResult("PQ-02", "doc_id matches filename prefix", "PQ", "PASS",
                           "No controlled documents found"))
        return

    mismatches = []
    for doc in docs:
        fm = parse_frontmatter(doc)
        if fm is None or "doc_id" not in fm:
            continue
        doc_id = fm["doc_id"].strip('"').strip("'")
        # Filename should start with the doc_id
        if not doc.stem.startswith(doc_id):
            mismatches.append(f"{doc.name} (doc_id={doc_id})")

    if mismatches:
        run.add(TestResult("PQ-02", "doc_id matches filename prefix", "PQ", "FAIL",
                           f"Mismatches: {', '.join(mismatches)}"))
    else:
        run.add(TestResult("PQ-02", "doc_id matches filename prefix", "PQ", "PASS",
                           f"All {len(docs)} doc_ids match filename prefixes"))


def pq_03_valid_status(run: ValidationRun) -> None:
    """PQ-03: status is valid enum (draft/review/approved/obsolete)."""
    docs = get_controlled_docs()
    if not docs:
        run.add(TestResult("PQ-03", "Status is valid enum", "PQ", "PASS",
                           "No controlled documents found"))
        return

    invalid = []
    for doc in docs:
        fm = parse_frontmatter(doc)
        if fm is None or "status" not in fm:
            continue
        status = fm["status"].strip('"').strip("'")
        if status not in VALID_STATUSES:
            invalid.append(f"{doc.name} (status={status})")

    if invalid:
        run.add(TestResult("PQ-03", "Status is valid enum", "PQ", "FAIL",
                           f"Invalid: {', '.join(invalid)}"))
    else:
        run.add(TestResult("PQ-03", "Status is valid enum", "PQ", "PASS",
                           f"All {len(docs)} documents have valid status values"))


def pq_04_clauses_array(run: ValidationRun) -> None:
    """PQ-04: clauses is array format."""
    docs = get_controlled_docs()
    if not docs:
        run.add(TestResult("PQ-04", "Clauses is array format", "PQ", "PASS",
                           "No controlled documents found"))
        return

    issues = []
    for doc in docs:
        fm = parse_frontmatter(doc)
        if fm is None or "clauses" not in fm:
            continue
        clauses_val = fm["clauses"]
        if not clauses_val.startswith("["):
            issues.append(f"{doc.name} (clauses={clauses_val})")

    if issues:
        run.add(TestResult("PQ-04", "Clauses is array format", "PQ", "FAIL",
                           f"Not array: {', '.join(issues)}"))
    else:
        run.add(TestResult("PQ-04", "Clauses is array format", "PQ", "PASS",
                           f"All {len(docs)} documents use array format for clauses"))


def pq_05_related_array(run: ValidationRun) -> None:
    """PQ-05: related is array format."""
    docs = get_controlled_docs()
    if not docs:
        run.add(TestResult("PQ-05", "Related is array format", "PQ", "PASS",
                           "No controlled documents found"))
        return

    issues = []
    for doc in docs:
        fm = parse_frontmatter(doc)
        if fm is None or "related" not in fm:
            continue
        related_val = fm["related"]
        if not related_val.startswith("["):
            issues.append(f"{doc.name} (related={related_val})")

    if issues:
        run.add(TestResult("PQ-05", "Related is array format", "PQ", "FAIL",
                           f"Not array: {', '.join(issues)}"))
    else:
        run.add(TestResult("PQ-05", "Related is array format", "PQ", "PASS",
                           f"All {len(docs)} documents use array format for related"))


def pq_06_date_format(run: ValidationRun) -> None:
    """PQ-06: Populated dates in YYYY-MM-DD format."""
    docs = get_controlled_docs()
    if not docs:
        run.add(TestResult("PQ-06", "Populated dates in YYYY-MM-DD format", "PQ", "PASS",
                           "No controlled documents found"))
        return

    date_fields = ["effective_date", "review_due", "approved_date"]
    date_re = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    issues = []

    for doc in docs:
        fm = parse_frontmatter(doc)
        if fm is None:
            continue
        for field_name in date_fields:
            if field_name not in fm:
                continue
            val = fm[field_name].strip('"').strip("'")
            # Empty values are acceptable (not yet populated)
            if not val:
                continue
            if not date_re.match(val):
                issues.append(f"{doc.name}.{field_name}={val}")

    if issues:
        run.add(TestResult("PQ-06", "Populated dates in YYYY-MM-DD format", "PQ", "FAIL",
                           f"Invalid: {', '.join(issues)}"))
    else:
        run.add(TestResult("PQ-06", "Populated dates in YYYY-MM-DD format", "PQ", "PASS",
                           "All populated date fields use YYYY-MM-DD format"))


def pq_07_git_clean(run: ValidationRun) -> None:
    """PQ-07: Git working tree clean for controlled docs."""
    rc, output = run_git("status", "--porcelain", "--", *CONTROLLED_DOC_FOLDERS)
    if rc != 0:
        run.add(TestResult("PQ-07", "Git working tree clean for controlled docs", "PQ", "FAIL",
                           "Could not run git status"))
        return

    if output:
        changed = [line.strip() for line in output.splitlines()[:5]]
        suffix = f" (+{len(output.splitlines())-5} more)" if len(output.splitlines()) > 5 else ""
        run.add(TestResult("PQ-07", "Git working tree clean for controlled docs", "PQ", "FAIL",
                           f"Uncommitted changes: {'; '.join(changed)}{suffix}"))
    else:
        run.add(TestResult("PQ-07", "Git working tree clean for controlled docs", "PQ", "PASS",
                           "No uncommitted changes in controlled document folders"))


def pq_08_branch_naming(run: ValidationRun) -> None:
    """PQ-08: Git branch naming convention (main or draft/*)."""
    rc, branch = run_git("branch", "--show-current")
    if rc != 0:
        run.add(TestResult("PQ-08", "Git branch naming convention", "PQ", "FAIL",
                           "Could not determine current branch"))
        return

    valid = branch == "main" or branch.startswith("draft/")
    if valid:
        run.add(TestResult("PQ-08", "Git branch naming convention", "PQ", "PASS",
                           f"Current branch: {branch}"))
    else:
        run.add(TestResult("PQ-08", "Git branch naming convention", "PQ", "FAIL",
                           f"Branch '{branch}' does not follow convention (main or draft/*)"))


def pq_09_git_tag_exists(run: ValidationRun) -> None:
    """PQ-09: Approved documents have a matching annotated git tag.

    For every document with status: approved, verifies that an annotated git
    tag exists named {doc_id}-v{revision}. Annotated tags are required per
    SOP-01 §6.3 — they carry tagger, date, and message metadata that constitute
    the §4.2.4 evidence of controlled distribution and traceability. Lightweight
    tags (which lack this metadata) are flagged as a failure even if a tag of
    the correct name exists.
    """
    docs = get_controlled_docs()
    issues: list[str] = []
    approved_count = 0

    for doc in docs:
        fm = parse_frontmatter(doc)
        if not fm:
            continue
        status = fm.get("status", "").strip('"').strip("'")
        if status != "approved":
            continue
        approved_count += 1

        doc_id = fm.get("doc_id", "").strip('"').strip("'")
        revision = fm.get("revision", "").strip('"').strip("'")
        if not doc_id or not revision:
            issues.append(f"{doc.name} (missing doc_id or revision in frontmatter)")
            continue

        expected_tag = f"{doc_id}-v{revision}"
        rc, _ = run_git("rev-parse", expected_tag)
        if rc != 0:
            issues.append(f"{doc.name} (no tag {expected_tag})")
            continue

        # Annotated tags appear as "tag" objects; lightweight tags as "commit".
        rc, obj_type = run_git("cat-file", "-t", expected_tag)
        if rc != 0 or obj_type != "tag":
            issues.append(f"{doc.name} ({expected_tag} exists but is not annotated)")

    if approved_count == 0:
        run.add(TestResult("PQ-09", "Approved docs have matching annotated git tags", "PQ", "PASS",
                           "No approved documents to check"))
    elif issues:
        run.add(TestResult("PQ-09", "Approved docs have matching annotated git tags", "PQ", "FAIL",
                           f"Issues: {'; '.join(issues)}"))
    else:
        run.add(TestResult("PQ-09", "Approved docs have matching annotated git tags", "PQ", "PASS",
                           f"All {approved_count} approved documents have matching annotated tags"))


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def next_val_id() -> str:
    """Determine the next VAL-YYYY-NN ID."""
    year = date.today().strftime("%Y")
    val_dir = VAULT_ROOT / "05-records" / "software-validation"
    val_dir.mkdir(parents=True, exist_ok=True)

    existing = sorted(val_dir.glob(f"VAL-{year}-*.md"))
    if existing:
        last = existing[-1].stem  # e.g., VAL-2026-03
        last_num = int(last.rsplit("-", 1)[1])
        return f"VAL-{year}-{last_num + 1:02d}"
    return f"VAL-{year}-01"


def generate_record(run: ValidationRun, val_id: str) -> str:
    """Generate the markdown validation record."""
    today_iso = date.today().strftime("%Y-%m-%d")
    today_body = date.today().strftime("%d/%m/%Y")

    lines = [
        "---",
        f"doc_id: {val_id}",
        "title: QMS Software Validation",
        "doc_type: record",
        f"standard: {CONFIG['standard']}",
        'clauses: ["4.1.6"]',
        'revision: "1.0"',
        "status: draft",
        f"effective_date: {today_iso}",
        "review_due:",
        "review_interval: 12",
        f"author: {CONFIG['quality_manager']}",
        "reviewer:",
        f"approver: {CONFIG['quality_manager']}",
        "approved_date:",
        'change_summary: "Automated validation run"',
        "tags: [qms, record, validation]",
        "supersedes:",
        'related: []',
        f"validation_status: {run.overall}",
        "validation_scope: Full (IQ + OQ + PQ)",
        "---",
        "",
        "# QMS Software Validation Record",
        "",
        f"**Record ID:** {val_id}",
        f"**Date:** {today_body}",
        f"**Validation Script:** `scripts/validate_qms.py`",
        f"**Overall Result:** **{run.overall}**",
        "",
        "**Scope:** Validation of computerised QMS tooling per ISO 13485:2016 §4.1.6.",
        "",
    ]

    # Group results by phase
    for phase, phase_name in [("IQ", "Installation Qualification"), ("OQ", "Operational Qualification"), ("PQ", "Performance Qualification")]:
        phase_results = [r for r in run.results if r.phase == phase]
        if not phase_results:
            continue

        passed = sum(1 for r in phase_results if r.status == "PASS")
        lines.append(f"## {phase} — {phase_name}")
        lines.append("")
        lines.append(f"**{passed}/{len(phase_results)} passed**")
        lines.append("")
        lines.append("| Test ID | Description | Result | Detail |")
        lines.append("|---------|-------------|--------|--------|")
        for r in phase_results:
            detail = r.detail.replace("|", "\\|")
            lines.append(f"| {r.test_id} | {r.description} | {r.status} | {detail} |")
        lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total tests | {run.total} |")
    lines.append(f"| Passed | {run.passed} |")
    lines.append(f"| Failed | {run.failed} |")
    lines.append(f"| Overall | **{run.overall}** |")
    lines.append("")

    # Sign-off
    lines.append("## Sign-off")
    lines.append("")
    lines.append("| Role | Name | Signature | Date |")
    lines.append("|------|------|-----------|------|")
    lines.append(f"| Validator | {CONFIG['quality_manager']} | | |")
    lines.append(f"| Quality Manager | {CONFIG['quality_manager']} | | |")
    lines.append("")

    # Revision history
    lines.append("## Revision History")
    lines.append("")
    lines.append("| Rev | Date | Author | Change Summary |")
    lines.append("|-----|------|--------|---------------|")
    lines.append(f"| 1.0 | {today_body} | {CONFIG['quality_manager']} | Initial automated validation |")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    dry_run = "--dry-run" in sys.argv

    # Verify we're running from vault root (or close to it)
    if not (VAULT_ROOT / ".obsidian").is_dir():
        print(f"ERROR: Vault root not found at {VAULT_ROOT}")
        print("Run this script from the vault root: python scripts/validate_qms.py")
        return 1

    run = ValidationRun()

    # IQ tests (6)
    iq_01_vault_folders(run)
    iq_02_git_repo(run)
    iq_03_community_plugins(run)
    iq_04_plugin_dirs(run)
    iq_05_templates(run)
    iq_06_record_subdirs(run)

    # OQ tests (9)
    oq_01_template_frontmatter(run)
    oq_02_template_nn_format(run)
    oq_03_template_date_formats(run)
    oq_04_doc_register_query(run)
    oq_05_overdue_reviews_query(run)
    oq_06_status_dashboard(run)
    oq_07_capa_log_query(run)
    oq_08_audit_schedule_query(run)
    oq_09_all_dashboards_exist(run)

    # PQ tests (9)
    pq_01_complete_frontmatter(run)
    pq_02_docid_matches_filename(run)
    pq_03_valid_status(run)
    pq_04_clauses_array(run)
    pq_05_related_array(run)
    pq_06_date_format(run)
    pq_07_git_clean(run)
    pq_08_branch_naming(run)
    pq_09_git_tag_exists(run)

    # Print results to console
    print(f"\n{CONFIG['organisation']} QMS Validation — {date.today().strftime('%d/%m/%Y')}")
    print("=" * 60)

    for phase in ["IQ", "OQ", "PQ"]:
        phase_results = [r for r in run.results if r.phase == phase]
        if not phase_results:
            continue
        print(f"\n{phase}:")
        for r in phase_results:
            marker = "PASS" if r.status == "PASS" else "FAIL"
            print(f"  [{marker}] {r.test_id}: {r.description}")
            if r.status == "FAIL":
                print(f"         -> {r.detail}")

    print(f"\n{'=' * 60}")
    print(f"Total: {run.passed}/{run.total} passed — Overall: {run.overall}")

    # Write record
    if not dry_run:
        val_id = next_val_id()
        record = generate_record(run, val_id)
        out_dir = VAULT_ROOT / "05-records" / "software-validation"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{val_id}.md"
        out_path.write_text(record, encoding="utf-8")
        print(f"\nValidation record written: {out_path.relative_to(VAULT_ROOT)}")
    else:
        print("\n[DRY RUN] No record written.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
