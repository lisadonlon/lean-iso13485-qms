#!/usr/bin/env python3
"""Personalise the QMS template for your organisation.

Sets qms.config.json (organisation, quality manager, standard) and replaces
{{TOKEN}} placeholders throughout the Markdown documents. Tokens whose value
is not present in the config are left in place, so the script is safe to
re-run as the config grows (e.g. after the Micro QMS plugin setup wizard or
the qms-interview skill has added company and scope details).

Stdlib only.

Usage:
    python3 scripts/init_qms.py
    python3 scripts/init_qms.py --org "Acme Medical Ltd" --quality-manager "Jane Doe"
    python3 scripts/init_qms.py --org "Acme Medical Ltd" --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ORG = "Your Organisation Ltd"
SKIP_TOP = {".git", "_archive", ".obsidian", "scripts", "plugin", "skills"}

ROLE_LABELS = {
    "legal_manufacturer": "legal manufacturer",
    "own_brand_labeller": "own-brand labeller",
    "contract_manufacturer": "contract manufacturer",
    "distributor": "distributor",
    "importer": "importer",
}


def build_token_map(cfg: dict) -> dict:
    """Map {{TOKEN}} names to values from the config.

    Tokens with no usable value are omitted (left untouched in documents).
    """
    company = cfg.get("company") or {}
    tokens: dict = {}

    def put(name: str, value) -> None:
        if isinstance(value, str):
            value = value.strip()
        if value:
            tokens[name] = value

    put("ORGANISATION_NAME", cfg.get("organisation")
        if cfg.get("organisation") not in (DEFAULT_ORG, None) else "")
    put("QUALITY_MANAGER", cfg.get("quality_manager"))
    put("COMPANY_REGISTRATION", company.get("registration_number"))
    put("REGISTERED_OFFICE", company.get("registered_office"))
    put("REGULATORY_ROLE", ROLE_LABELS.get(company.get("regulatory_role", ""),
                                           company.get("regulatory_role")))
    sites = [s for s in (company.get("operating_sites") or []) if isinstance(s, dict)]
    site_parts = []
    for s in sites:
        addr = (s.get("address") or "").strip()
        acts = (s.get("activities") or "").strip()
        if addr:
            site_parts.append(f"{addr} ({acts})" if acts else addr)
    put("OPERATING_SITES", "; ".join(site_parts))
    put("DEVICE_TYPES", ", ".join(company.get("device_types") or []))
    put("MARKETS", ", ".join(company.get("markets") or []))
    put("QMS_ACTIVITIES", ", ".join(company.get("activities") or []))
    return tokens


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        value = input(f"{prompt}{suffix}: ").strip()
    except EOFError:
        value = ""
    return value or default


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--org", help="Organisation name")
    ap.add_argument("--quality-manager", default=None, help="Quality manager name")
    ap.add_argument("--standard", default=None, help="Primary standard (default ISO 13485:2016)")
    ap.add_argument("--dry-run", action="store_true", help="Show what would change; write nothing")
    args = ap.parse_args()

    cfg_path = ROOT / "qms.config.json"
    cfg: dict = {}
    if cfg_path.is_file():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            cfg = {}

    existing_org = cfg.get("organisation", "")
    org_default = "" if existing_org in (DEFAULT_ORG, "", None) else existing_org
    org = args.org or ask("Organisation name", org_default)
    if not org:
        print("ERROR: organisation name is required.", file=sys.stderr)
        return 1

    if args.quality_manager is not None:
        qm = args.quality_manager
    else:
        qm = ask("Quality manager name (optional)", cfg.get("quality_manager", "") or "")
    standard = args.standard or cfg.get("standard") or "ISO 13485:2016"

    tokens = build_token_map({**cfg, "organisation": org, "quality_manager": qm})

    # Find markdown files containing any resolvable token
    changed = []
    for md in sorted(ROOT.rglob("*.md")):
        rel = md.relative_to(ROOT)
        if rel.parts and rel.parts[0] in SKIP_TOP:
            continue
        try:
            text = md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        new_text = text
        for name, value in tokens.items():
            new_text = new_text.replace("{{" + name + "}}", value)
        if new_text != text:
            changed.append(rel)
            if not args.dry_run:
                md.write_text(new_text, encoding="utf-8")

    print(f"Organisation:    {org}")
    print(f"Quality manager: {qm or '(blank)'}")
    print(f"Standard:        {standard}")
    print(f"Resolvable tokens: {', '.join(sorted(tokens)) or '(none)'}")
    print(f"Files with resolvable tokens: {len(changed)}")
    for rel in changed:
        print(f"  {'would update' if args.dry_run else 'updated'}: {rel}")

    if args.dry_run:
        print("\n[DRY RUN] qms.config.json not written, no files changed.")
        return 0

    cfg.update({"organisation": org, "quality_manager": qm, "standard": standard})
    cfg.setdefault("github_repo", "")
    cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {cfg_path.relative_to(ROOT)}")
    print("Done. Review the changes with `git diff`, then commit when ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
