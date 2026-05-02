#!/usr/bin/env python3
"""Bundle YAML preset sources into a single catalog.json.

Reads:
- categories.yaml      — list of categories with stable UUIDs
- presets/<cat>/*.yaml — one file per preset, frontmatter + template body

Writes:
- catalog.json         — v4 schema, consumed by Vibalos's CatalogSyncService

Usage:
    python3 bundle.py [--check]

  --check   Validate only; do not write catalog.json. Useful for CI gates.

Schema reference: Vibalos/Models/PresetCatalog.swift in moinsen-dev/prompt_polish.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

try:
    import yaml
except ImportError:
    print("error: PyYAML is required. Install with: pip3 install pyyaml", file=sys.stderr)
    sys.exit(2)


SCHEMA_VERSION = 4
ROOT = Path(__file__).resolve().parent
CATEGORIES_FILE = ROOT / "categories.yaml"
PRESETS_DIR = ROOT / "presets"
OUTPUT_FILE = ROOT / "catalog.json"


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def parse_uuid(value: str, label: str) -> str:
    try:
        return str(uuid.UUID(value))
    except (ValueError, TypeError):
        fail(f"{label}: not a valid UUID — {value!r}")
        return ""  # unreachable


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Split a YAML-frontmatter Markdown-ish file into (frontmatter, body).

    Format:
        ---
        key: value
        ---
        body text with {{text}}
    """
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm = yaml.safe_load(parts[1]) or {}
    body = parts[2].lstrip("\n")
    # Strip trailing newlines but keep internal whitespace
    return fm, body.rstrip()


def load_categories() -> list[dict]:
    if not CATEGORIES_FILE.exists():
        fail(f"missing {CATEGORIES_FILE}")
    raw = yaml.safe_load(CATEGORIES_FILE.read_text()) or []
    if not isinstance(raw, list):
        fail("categories.yaml must be a YAML list at the top level")
    out = []
    seen_ids: set[str] = set()
    seen_slugs: set[str] = set()
    for entry in raw:
        if not isinstance(entry, dict):
            fail(f"category entry is not a mapping: {entry!r}")
        cat_id = parse_uuid(entry.get("id", ""), f"category {entry.get('slug', '?')}")
        slug = entry.get("slug")
        name = entry.get("name")
        if not slug or not isinstance(slug, str):
            fail(f"category {cat_id}: missing slug")
        if slug in seen_slugs:
            fail(f"duplicate category slug: {slug}")
        if cat_id in seen_ids:
            fail(f"duplicate category UUID: {cat_id}")
        if not name or not isinstance(name, str):
            fail(f"category {slug}: missing name")
        seen_ids.add(cat_id)
        seen_slugs.add(slug)
        out.append(
            {
                "id": cat_id,
                "name": name,
                "modifierBank": entry.get("modifierBank"),
                "sortOrder": int(entry.get("sortOrder", 0)),
                "isEnabled": bool(entry.get("isEnabled", True)),
                "source": entry.get("source", "community"),
                "_slug": slug,
            }
        )
    return out


def load_presets(categories_by_slug: dict[str, dict]) -> list[dict]:
    if not PRESETS_DIR.exists():
        return []
    out: list[dict] = []
    seen_ids: set[str] = set()
    for cat_dir in sorted(PRESETS_DIR.iterdir()):
        if not cat_dir.is_dir():
            continue
        cat_slug = cat_dir.name
        category = categories_by_slug.get(cat_slug)
        if not category:
            fail(f"presets/{cat_slug}/ exists but no matching category in categories.yaml")
        for preset_file in sorted(cat_dir.glob("*.yaml")):
            fm, body = split_frontmatter(preset_file.read_text())
            preset_id = parse_uuid(fm.get("id", ""), f"preset {preset_file}")
            if preset_id in seen_ids:
                fail(f"duplicate preset UUID: {preset_id} ({preset_file})")
            seen_ids.add(preset_id)
            name = fm.get("name")
            if not name or not isinstance(name, str):
                fail(f"{preset_file}: missing name")
            template = body.strip()
            if not template:
                fail(f"{preset_file}: empty template body")
            if "{{text}}" not in template:
                fail(f"{preset_file}: template must include {{{{text}}}}")
            preset = {
                "id": preset_id,
                "categoryID": category["id"],
                "name": name,
                "template": template,
                "isEnabled": bool(fm.get("isEnabled", True)),
                "outputMode": _coerce_str(fm.get("outputMode"), "replaceSelection"),
                "tagMode": _coerce_str(fm.get("tagMode"), "off"),
                "emojiUsage": _coerce_str(fm.get("emojiUsage"), "off"),
                "languageMode": _coerce_str(fm.get("languageMode"), "keepOriginal"),
                "tone": _coerce_str(fm.get("tone"), "neutral"),
                "toneIntensity": _intensity(fm.get("toneIntensity", "balanced")),
                "writingStyle": _coerce_str(fm.get("writingStyle"), "default"),
                "sortOrder": int(fm.get("sortOrder", 0)),
                "source": _coerce_str(fm.get("source"), "community"),
            }
            shortcut = fm.get("shortcutPosition")
            if shortcut is not None:
                preset["shortcutPosition"] = int(shortcut)
            engines = fm.get("recommendedEngines")
            if engines:
                preset["recommendedEngines"] = _normalize_engines(engines, preset_file)
            out.append(preset)
    return out


def _intensity(value) -> int:
    """Accept either int (0/1/2) or symbolic name."""
    if isinstance(value, int):
        return value
    mapping = {"subtle": 0, "balanced": 1, "strong": 2}
    if value in mapping:
        return mapping[value]
    fail(f"toneIntensity must be subtle/balanced/strong or 0/1/2, got {value!r}")
    return 1  # unreachable


def _coerce_str(value, default: str) -> str:
    """YAML 1.1 (PyYAML's default) parses bare `off`/`on`/`yes`/`no` as
    booleans. Coerce them back to the string the app expects, so
    contributors can write `tagMode: off` without quoting."""
    if value is None:
        return default
    if value is True:
        return "on"
    if value is False:
        return "off"
    return str(value)


def _normalize_engines(engines: list, preset_file: Path) -> list[dict]:
    if not isinstance(engines, list):
        fail(f"{preset_file}: recommendedEngines must be a list")
    out = []
    for entry in engines:
        if not isinstance(entry, dict):
            fail(f"{preset_file}: each recommendedEngine must be a mapping")
        engine = entry.get("engine")
        if engine not in ("ollama", "appleFoundation"):
            fail(f"{preset_file}: engine must be 'ollama' or 'appleFoundation', got {engine!r}")
        spec = {"engine": engine}
        if entry.get("model"):
            spec["model"] = entry["model"]
        if entry.get("notes"):
            spec["notes"] = entry["notes"]
        out.append(spec)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate only, do not write catalog.json")
    args = parser.parse_args()

    categories = load_categories()
    categories_by_slug = {c["_slug"]: c for c in categories}
    presets = load_presets(categories_by_slug)

    catalog = {
        "version": SCHEMA_VERSION,
        "categories": [
            {k: v for k, v in c.items() if k != "_slug" and v is not None}
            for c in categories
        ],
        "presets": presets,
    }

    if args.check:
        print(f"OK — {len(categories)} categories, {len(presets)} presets")
        return

    OUTPUT_FILE.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {OUTPUT_FILE.relative_to(ROOT.parent)} — {len(categories)} categories, {len(presets)} presets")


if __name__ == "__main__":
    main()
