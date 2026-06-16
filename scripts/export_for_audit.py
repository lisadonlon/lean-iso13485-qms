#!/usr/bin/env python3
"""QMS Audit Export Script

Exports approved QMS documents as controlled-copy PDFs for external distribution
(e.g. auditor share via Google Drive read-only link).

Pattern (per CLAUDE.md and SOP-01 §6.3):
  - The vault git repo remains the §4.2.4 controlled copy (single source of truth).
  - This script produces a one-way, read-only PDF snapshot of approved docs only.
  - Drive (or any other location you point --out at) holds the snapshot.
  - Never sync the output folder back into the vault.

What it does:
  1. Walks the vault and filters for status: approved documents only.
  2. Converts each markdown doc to PDF via pandoc + weasyprint.
  3. Stamps every page footer with controlled-copy provenance:
        {doc_id} Rev {revision} — Approved {approved_date}
        Controlled copy issued {today} — Page N of M
  4. Names files {DOC-ID}_Rev{X.Y}.pdf so versioning is visible to the auditor.
  5. Mirrors the source folder structure in the output (clean navigation).
  6. On each run, moves any PDF whose revision no longer matches the vault
     to a _superseded/ subfolder so old links never point at stale content.
  7. Generates INDEX.pdf — a one-page table of every approved doc + revision.
  8. Writes a distribution manifest record under 05-records/distribution/
     (DIST-YYYY-NN.md) capturing git SHA, git tag, file SHA-256 of every
     exported PDF, and a recipient field for you to fill in when shared.

Dependencies (install once):
    brew install pandoc
    pip3 install weasyprint --break-system-packages

Usage:
    python scripts/export_for_audit.py                    # Default: ../qms-publish/
    python scripts/export_for_audit.py --out PATH         # Custom output folder
    python scripts/export_for_audit.py --dry-run          # List actions, write nothing
    python scripts/export_for_audit.py --include-drafts   # Include drafts (NEVER for auditor use)
    python scripts/export_for_audit.py --skip-record      # Skip writing the DIST record

Exit codes:
    0  Success (or dry-run completed)
    1  Missing dependency (pandoc / weasyprint)
    2  Vault structure problem
    3  Conversion failure
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

from qms_config import load_config


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

VAULT_ROOT = Path(__file__).resolve().parent.parent

CONFIG = load_config(VAULT_ROOT)

# Folders that hold controlled documents eligible for external distribution.
# Records (05-records/) are intentionally excluded — they are private QMS
# evidence and are not part of a controlled document distribution package.
CONTROLLED_DOC_FOLDERS = [
    "01-quality-manual",
    "02-procedures",
    "03-work-instructions",
    "04-forms-templates",
    "06-isms",
    "08-references",
]

# Process maps (07-process-maps/) are excluded by default because they are
# Excalidraw .md files that do not render meaningfully via pandoc. Export
# them separately as PNG/PDF from Obsidian if the auditor needs them.

# Where the DIST record lives (created on first use).
DIST_RECORD_DIR = VAULT_ROOT / "05-records" / "distribution"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class QmsDoc:
    """A single QMS document discovered in the vault."""
    doc_id: str
    title: str
    revision: str
    status: str
    approved_date: str
    source_path: Path
    relative_folder: Path  # e.g. Path("02-procedures")
    frontmatter: dict[str, str] = field(default_factory=dict)


@dataclass
class ExportResult:
    """The outcome of exporting one document."""
    doc: QmsDoc
    output_path: Path
    sha256: str
    superseded: list[Path] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Dependency checks
# ---------------------------------------------------------------------------

def check_dependency(cmd: str, install_hint: str) -> None:
    if shutil.which(cmd) is None:
        print(f"ERROR: '{cmd}' is not installed or not on PATH.", file=sys.stderr)
        print(f"  Install with: {install_hint}", file=sys.stderr)
        sys.exit(1)


def check_dependencies() -> None:
    check_dependency("pandoc", "brew install pandoc")
    check_dependency("weasyprint", "pip3 install weasyprint --break-system-packages")


# ---------------------------------------------------------------------------
# Frontmatter parsing
#
# Deliberately stdlib-only — no PyYAML dependency. Matches the simple parser
# used by validate_qms.py so behaviour stays consistent across scripts.
# ---------------------------------------------------------------------------

def parse_frontmatter(filepath: Path) -> dict[str, str] | None:
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
    for line in text[3:end].strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip().strip('"').strip("'")
    return fm


def read_body(filepath: Path) -> str:
    """Return the markdown body with frontmatter stripped."""
    text = filepath.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3:].lstrip("\n")
    return text


_WIKILINK_RE = re.compile(r'!?\[\[([^\[\]]+)\]\]')


def strip_wikilinks(md: str) -> str:
    """Convert Obsidian wikilinks to plain display text for export.

    pandoc (GFM) does not understand [[Target]] / [[Target|Alias]] syntax and
    would otherwise pass the brackets through verbatim into the issued PDF.
    Renders the alias if present, otherwise the target title (with any
    #heading shown as 'Title — Heading'). Transclusion embeds (![[...]]) are
    reduced to the same display text — the QMS docs use standard image syntax
    for figures, so no genuine transclusions are lost.
    """
    def replace(match):
        inner = match.group(1).strip()
        if "|" in inner:
            return inner.split("|", 1)[1].strip()
        if "#" in inner:
            title, _, heading = inner.partition("#")
            title, heading = title.strip(), heading.strip()
            return f"{title} — {heading}" if title else heading
        return inner

    return _WIKILINK_RE.sub(replace, md)


# ---------------------------------------------------------------------------
# Vault discovery
# ---------------------------------------------------------------------------

def discover_docs(vault: Path, include_drafts: bool) -> list[QmsDoc]:
    docs: list[QmsDoc] = []
    for folder_name in CONTROLLED_DOC_FOLDERS:
        folder = vault / folder_name
        if not folder.is_dir():
            continue
        for md in sorted(folder.glob("*.md")):
            if md.name.startswith("_"):
                continue
            fm = parse_frontmatter(md)
            if fm is None:
                continue
            status = fm.get("status", "").lower()
            if not include_drafts and status != "approved":
                continue
            docs.append(QmsDoc(
                doc_id=fm.get("doc_id", md.stem),
                title=fm.get("title", md.stem),
                revision=fm.get("revision", "0.0"),
                status=status or "unknown",
                approved_date=fm.get("approved_date", ""),
                source_path=md,
                relative_folder=Path(folder_name),
                frontmatter=fm,
            ))
    return docs


# ---------------------------------------------------------------------------
# Git context (best-effort — empty strings if not a git repo)
# ---------------------------------------------------------------------------

def run_git(*args: str, cwd: Path) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, OSError):
        pass
    return ""


def git_context(vault: Path) -> dict[str, str]:
    return {
        "sha": run_git("rev-parse", "HEAD", cwd=vault),
        "short_sha": run_git("rev-parse", "--short", "HEAD", cwd=vault),
        "branch": run_git("rev-parse", "--abbrev-ref", "HEAD", cwd=vault),
        "tags_on_head": run_git("tag", "--points-at", "HEAD", cwd=vault),
        "dirty": run_git("status", "--porcelain", cwd=vault),
    }


# ---------------------------------------------------------------------------
# PDF generation
# ---------------------------------------------------------------------------

PAGE_CSS_TEMPLATE = """
@page {{
  size: A4;
  margin: 22mm 18mm 22mm 18mm;
  @top-right {{
    content: "{header_right}";
    font-family: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 8.5pt;
    color: #444;
  }}
  @bottom-left {{
    content: "{footer_left}";
    font-family: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 8pt;
    color: #555;
  }}
  @bottom-right {{
    content: "Page " counter(page) " of " counter(pages);
    font-family: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 8pt;
    color: #555;
  }}
}}
body {{
  font-family: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 10.5pt;
  line-height: 1.45;
  color: #111;
}}
h1 {{ font-size: 18pt; border-bottom: 1px solid #999; padding-bottom: 4pt; }}
h2 {{ font-size: 14pt; margin-top: 18pt; }}
h3 {{ font-size: 12pt; margin-top: 14pt; }}
table {{ border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 9.5pt; }}
th, td {{ border: 1px solid #bbb; padding: 4pt 6pt; text-align: left; vertical-align: top; }}
th {{ background: #f0f0f0; }}
code {{ font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 9.5pt; background: #f4f4f4; padding: 1pt 3pt; }}
pre {{ background: #f4f4f4; padding: 6pt; border-left: 3px solid #888; font-size: 9.5pt; overflow-wrap: anywhere; }}
img {{ max-width: 100%; height: auto; }}
.controlled-banner {{
  border: 1pt solid #888; background: #fafafa; padding: 6pt 10pt;
  font-size: 9pt; color: #333; margin-bottom: 12pt;
}}
"""


def build_html(doc: QmsDoc, body_html: str, today: str) -> str:
    """Wrap pandoc-produced HTML body with controlled-copy framing + footer CSS."""
    footer_left = (
        f"{doc.doc_id} Rev {doc.revision} — Approved {doc.approved_date or 'n/a'} "
        f"— Controlled copy issued {today}"
    )
    header_right = f"{doc.doc_id} Rev {doc.revision}"
    css = PAGE_CSS_TEMPLATE.format(
        footer_left=_css_escape(footer_left),
        header_right=_css_escape(header_right),
    )
    banner = (
        f'<div class="controlled-banner"><strong>Controlled copy.</strong> '
        f"{doc.doc_id} Rev {doc.revision}. "
        f"Approved {doc.approved_date or 'n/a'}. "
        f"Issued {today}. "
        f"The master controlled copy is held in the {_html_escape(CONFIG['organisation'])} QMS git repository "
        f"(branch <code>main</code>, tag <code>{doc.doc_id}-v{doc.revision}</code>). "
        f"Printed or downloaded copies are uncontrolled outside the issued date.</div>"
    )
    return (
        f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>{_html_escape(doc.doc_id)} {_html_escape(doc.title)}</title>"
        f"<style>{css}</style></head><body>{banner}{body_html}</body></html>"
    )


def _css_escape(s: str) -> str:
    # CSS content strings need backslash-escaping for quotes and backslashes.
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def md_to_html(md_body: str) -> str:
    """Convert markdown body to HTML fragment via pandoc."""
    result = subprocess.run(
        ["pandoc", "--from=gfm+yaml_metadata_block", "--to=html5", "--wrap=none"],
        input=md_body,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pandoc failed: {result.stderr.strip()}")
    return result.stdout


_IMG_TAG_RE = re.compile(r'<img\b[^>]*?\bsrc="([^"]+)"', re.IGNORECASE)

_IMG_MIME_BY_EXT = {
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
}


def inline_local_images(html: str, base_dir: Path) -> str:
    """Embed local <img> sources as base64 data URIs.

    The HTML is piped to weasyprint via stdin, so relative image paths would
    otherwise resolve against the process working directory rather than the
    document folder. Inlining makes each exported PDF self-contained and lets
    a document (e.g. QM-01) embed a process-map SVG held in 07-process-maps/.
    Remote (http/https) and already-inlined (data:) sources are left as-is.
    """
    def replace(match):
        src = match.group(1)
        if src.startswith(("http://", "https://", "data:")):
            return match.group(0)
        rel = urllib.parse.unquote(src)
        img_path = (base_dir / rel).resolve()
        mime = _IMG_MIME_BY_EXT.get(img_path.suffix.lower())
        if mime is None or not img_path.is_file():
            return match.group(0)  # leave untouched; weasyprint will warn
        encoded = base64.b64encode(img_path.read_bytes()).decode("ascii")
        return match.group(0).replace(src, f"data:{mime};base64,{encoded}", 1)

    return _IMG_TAG_RE.sub(replace, html)


def html_to_pdf(html: str, out_path: Path) -> None:
    """Convert an HTML string to PDF via weasyprint."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["weasyprint", "-", str(out_path)],
        input=html,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"weasyprint failed: {result.stderr.strip()}")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Supersession handling
# ---------------------------------------------------------------------------

def move_superseded(doc: QmsDoc, output_folder: Path, current_filename: str, today: str) -> list[Path]:
    """Move any older-revision PDF for this doc into _superseded/.

    Looks for files matching {DOC-ID}_Rev*.pdf that are not the current revision.
    """
    if not output_folder.is_dir():
        return []
    moved: list[Path] = []
    superseded_dir = output_folder / "_superseded"
    for existing in output_folder.glob(f"{doc.doc_id}_Rev*.pdf"):
        if existing.name == current_filename:
            continue
        superseded_dir.mkdir(parents=True, exist_ok=True)
        # Tag the moved file with the date it was retired from active distribution.
        retired_name = f"{existing.stem}_retired-{today}.pdf"
        shutil.move(str(existing), str(superseded_dir / retired_name))
        moved.append(superseded_dir / retired_name)
    return moved


# ---------------------------------------------------------------------------
# INDEX.pdf
# ---------------------------------------------------------------------------

def build_index(docs: list[QmsDoc], today: str, git_ctx: dict[str, str]) -> str:
    rows = "\n".join(
        f"<tr><td>{_html_escape(d.doc_id)}</td>"
        f"<td>{_html_escape(d.title)}</td>"
        f"<td>{_html_escape(d.revision)}</td>"
        f"<td>{_html_escape(d.approved_date)}</td>"
        f"<td>{_html_escape(', '.join(eval_list(d.frontmatter.get('clauses', '[]'))))}</td></tr>"
        for d in docs
    )
    tag_line = f"Git tag(s) at HEAD: {git_ctx['tags_on_head'] or '(none)'}"
    sha_line = f"Git SHA: {git_ctx['short_sha'] or '(not a git repo)'}"
    dirty_warn = ""
    if git_ctx.get("dirty"):
        dirty_warn = (
            '<p style="color:#a00;"><strong>Warning:</strong> the vault working tree '
            "had uncommitted changes at export time. The exported PDFs may not match "
            "any committed state of the repository.</p>"
        )
    body = (
        f"<h1>{_html_escape(CONFIG['organisation'])} QMS — Controlled Document Index</h1>"
        f"<p>Issued: <strong>{today}</strong></p>"
        f"<p>{sha_line} &nbsp;|&nbsp; {tag_line}</p>"
        f"{dirty_warn}"
        f"<table><thead><tr><th>Doc ID</th><th>Title</th><th>Rev</th>"
        f"<th>Approved</th><th>Clauses</th></tr></thead><tbody>{rows}</tbody></table>"
        f"<p style='margin-top:18pt; font-size:9pt; color:#555;'>"
        f"This index lists every approved document included in this distribution. "
        f"For provenance, the controlled master is held in the {_html_escape(CONFIG['organisation'])} QMS git "
        f"repository (commit {_html_escape(git_ctx['short_sha'] or 'n/a')}).</p>"
    )
    css = PAGE_CSS_TEMPLATE.format(
        footer_left=_css_escape(f"QMS Document Index — issued {today}"),
        header_right=_css_escape("INDEX"),
    )
    return (
        f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>QMS Document Index</title>"
        f"<style>{css}</style></head><body>{body}</body></html>"
    )


def eval_list(raw: str) -> list[str]:
    """Best-effort conversion of frontmatter 'clauses: ["4.2.4", "5.3"]' to a list."""
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        parts = [p.strip().strip('"').strip("'") for p in inner.split(",")]
        return [p for p in parts if p]
    return [raw] if raw else []


# ---------------------------------------------------------------------------
# Distribution manifest record
# ---------------------------------------------------------------------------

def next_dist_id(today: date) -> tuple[str, Path]:
    """Allocate the next DIST-YYYY-NN id by counting existing records this year."""
    year = today.year
    DIST_RECORD_DIR.mkdir(parents=True, exist_ok=True)
    existing = sorted(DIST_RECORD_DIR.glob(f"DIST-{year}-*.md"))
    n = len(existing) + 1
    dist_id = f"DIST-{year}-{n:02d}"
    return dist_id, DIST_RECORD_DIR / f"{dist_id}.md"


def write_manifest_record(
    dist_id: str,
    record_path: Path,
    today: str,
    git_ctx: dict[str, str],
    results: list[ExportResult],
    output_folder: Path,
) -> None:
    fm = (
        "---\n"
        f"doc_id: {dist_id}\n"
        f"title: Controlled Document Distribution {dist_id}\n"
        "doc_type: record\n"
        f"standard: {CONFIG['standard']}\n"
        'clauses: ["4.2.4"]\n'
        'revision: "1.0"\n'
        "status: approved\n"
        f"effective_date: {today}\n"
        f"review_due:\n"
        "review_interval:\n"
        f"author: {CONFIG['quality_manager']}\n"
        "reviewer:\n"
        f"approver: {CONFIG['quality_manager']}\n"
        f"approved_date: {today}\n"
        'change_summary: "Auto-generated by scripts/export_for_audit.py"\n'
        "tags: [qms, record, distribution]\n"
        "supersedes:\n"
        "related: [\"SOP-01\", \"FRM-01\"]\n"
        "---\n\n"
    )
    body = [
        f"# Controlled Document Distribution — {dist_id}",
        "",
        f"**Issued:** {_dd_mm_yyyy(today)}",
        "",
        "## 1. Export context",
        "",
        f"| Field | Value |",
        f"|---|---|",
        f"| Git SHA | `{git_ctx.get('short_sha', '(n/a)')}` (`{git_ctx.get('sha', '')[:40]}`) |",
        f"| Git branch | `{git_ctx.get('branch', '(n/a)')}` |",
        f"| Git tags at HEAD | {git_ctx.get('tags_on_head') or '(none)'} |",
        f"| Working tree clean | {'no — see warning' if git_ctx.get('dirty') else 'yes'} |",
        f"| Output folder | `{output_folder}` |",
        f"| Document count | {len(results)} |",
        "",
        "## 2. Documents exported",
        "",
        "| Doc ID | Title | Rev | Approved | File | SHA-256 |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        body.append(
            f"| {r.doc.doc_id} | {r.doc.title} | {r.doc.revision} "
            f"| {r.doc.approved_date or '—'} | `{r.output_path.name}` "
            f"| `{r.sha256[:16]}…` |"
        )
    superseded_rows = [r for r in results if r.superseded]
    body += [
        "",
        "## 3. Superseded copies retired this run",
        "",
    ]
    if not superseded_rows:
        body.append("None.")
    else:
        body.append("| Doc ID | Retired file |")
        body.append("|---|---|")
        for r in superseded_rows:
            for s in r.superseded:
                body.append(f"| {r.doc.doc_id} | `{s.name}` |")
    body += [
        "",
        "## 4. Distribution recipient",
        "",
        "_Fill this section in when the package is shared. Cross-reference the matching FRM-01 entry._",
        "",
        "| Field | Value |",
        "|---|---|",
        "| FRM-01 entry # |  |",
        "| Recipient name |  |",
        "| Organisation |  |",
        "| Purpose |  |",
        "| Delivery method |  |",
        "| Link / location |  |",
        "| Link expiry date |  |",
        "| Access withdrawn date |  |",
        "",
        "## 5. Notes",
        "",
        "",
    ]
    record_path.write_text(fm + "\n".join(body) + "\n", encoding="utf-8")


def _dd_mm_yyyy(yyyy_mm_dd: str) -> str:
    try:
        d = datetime.strptime(yyyy_mm_dd, "%Y-%m-%d").date()
        return d.strftime("%d/%m/%Y")
    except ValueError:
        return yyyy_mm_dd


# ---------------------------------------------------------------------------
# CSV manifest (machine-readable companion to the markdown record)
# ---------------------------------------------------------------------------

def write_csv_manifest(output_folder: Path, results: list[ExportResult], today: str, git_ctx: dict[str, str]) -> Path:
    path = output_folder / "manifest.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "doc_id", "title", "revision", "approved_date",
            "file", "sha256", "exported_at", "git_sha", "git_tags_at_head",
        ])
        for r in results:
            w.writerow([
                r.doc.doc_id,
                r.doc.title,
                r.doc.revision,
                r.doc.approved_date,
                str(r.output_path.relative_to(output_folder)),
                r.sha256,
                today,
                git_ctx.get("sha", ""),
                git_ctx.get("tags_on_head", ""),
            ])
    return path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=VAULT_ROOT.parent / "qms-publish",
                        help="Output folder (default: ../qms-publish/ — sibling of vault, outside git)")
    parser.add_argument("--dry-run", action="store_true",
                        help="List what would be exported. Write nothing.")
    parser.add_argument("--include-drafts", action="store_true",
                        help="Include status:draft and status:review docs. NEVER use for auditor distribution.")
    parser.add_argument("--skip-record", action="store_true",
                        help="Skip writing the DIST-YYYY-NN distribution manifest record.")
    args = parser.parse_args()

    today_iso = date.today().isoformat()

    print(f"{CONFIG['organisation']} QMS Audit Export")
    print(f"Vault:  {VAULT_ROOT}")
    print(f"Output: {args.out}")
    print(f"Date:   {today_iso}")
    print()

    if not args.dry_run:
        check_dependencies()

    docs = discover_docs(VAULT_ROOT, include_drafts=args.include_drafts)
    if not docs:
        what = "approved" if not args.include_drafts else "approved/draft/review"
        print(f"No {what} documents found in vault. Nothing to export.")
        return 0

    if args.include_drafts:
        print("WARNING: --include-drafts is set. Output is NOT suitable for auditor distribution.")
        print()

    git_ctx = git_context(VAULT_ROOT)
    if git_ctx.get("dirty"):
        print("WARNING: working tree has uncommitted changes. Commit before issuing to an auditor.")
        print()

    # Show plan
    print(f"Documents to export: {len(docs)}")
    for d in docs:
        out_rel = d.relative_folder / f"{d.doc_id}_Rev{d.revision}.pdf"
        print(f"  [{d.status:>8}] {d.doc_id} Rev {d.revision}  ->  {out_rel}")
    print()

    if args.dry_run:
        print("Dry run — no files written.")
        return 0

    results: list[ExportResult] = []
    for d in docs:
        out_folder = args.out / d.relative_folder
        filename = f"{d.doc_id}_Rev{d.revision}.pdf"
        out_path = out_folder / filename
        try:
            body_html = md_to_html(strip_wikilinks(read_body(d.source_path)))
            body_html = inline_local_images(body_html, d.source_path.parent)
            html_doc = build_html(d, body_html, today_iso)
            html_to_pdf(html_doc, out_path)
        except RuntimeError as e:
            print(f"FAIL  {d.doc_id}: {e}", file=sys.stderr)
            return 3
        moved = move_superseded(d, out_folder, filename, today_iso)
        results.append(ExportResult(
            doc=d,
            output_path=out_path,
            sha256=sha256_of(out_path),
            superseded=moved,
        ))
        print(f"  wrote {out_path.relative_to(args.out)}  ({sha256_of(out_path)[:12]}…)")
        for m in moved:
            print(f"    retired -> {m.relative_to(args.out)}")

    # INDEX.pdf
    index_html = build_index(docs, today_iso, git_ctx)
    index_path = args.out / "INDEX.pdf"
    try:
        html_to_pdf(index_html, index_path)
        print(f"  wrote {index_path.relative_to(args.out)}")
    except RuntimeError as e:
        print(f"FAIL  INDEX: {e}", file=sys.stderr)
        return 3

    # Machine-readable manifest
    csv_path = write_csv_manifest(args.out, results, today_iso, git_ctx)
    print(f"  wrote {csv_path.relative_to(args.out)}")

    # QMS distribution record (inside the vault)
    if not args.skip_record:
        dist_id, record_path = next_dist_id(date.today())
        write_manifest_record(dist_id, record_path, today_iso, git_ctx, results, args.out)
        print(f"  wrote {record_path.relative_to(VAULT_ROOT)}  ({dist_id})")

    print()
    print(f"Done. {len(results)} document(s) exported to {args.out}")
    print("Next: commit the DIST record (if written), then share the output folder via")
    print("      Google Drive as Viewer-only. Log the recipient in FRM-01 and update DIST.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
