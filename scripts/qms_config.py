"""Shared QMS configuration loader (stdlib only).

Reads qms.config.json from the vault root so the organisation name and
quality-manager name are not hard-coded in the tooling. Returns safe
defaults if the file is absent or unreadable.
"""
from __future__ import annotations

import json
from pathlib import Path

_DEFAULTS = {
    "organisation": "Your Organisation",
    "quality_manager": "",
    "standard": "ISO 13485:2016",
    "github_repo": "",
}


def load_config(vault_root) -> dict:
    """Return the merged config dict (defaults + qms.config.json overrides)."""
    cfg = dict(_DEFAULTS)
    path = Path(vault_root) / "qms.config.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            cfg.update({k: v for k, v in data.items() if v is not None})
    except (OSError, json.JSONDecodeError, ValueError):
        pass
    return cfg
