#!/usr/bin/env python3
"""Run preset evaluation against a corpus of test inputs.

Pipeline per (preset, input):
    1. Send `preview_preset` action to the running Vibalos app via the
       moinsen bridge → get model output (uses the active engine + model
       configured in the app).
    2. Send (preset, input, output) to Claude as judge → structured
       verdict (pass/fail + scores + suggested fix).
    3. Aggregate into a Markdown report.

Usage:
    python3 prompts/eval/run.py --preset improve-prompt
    python3 prompts/eval/run.py --preset all
    python3 prompts/eval/run.py --preset improve-prompt --output prompts/eval-results/

Requires:
- The Vibalos app to be running (moinsen bridge on http://localhost:9335)
- ANTHROPIC_API_KEY exported in the environment
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:
    raise SystemExit("Missing dependency: pyyaml. Install with: pip3 install -r prompts/eval/requirements.txt")

# Allow running this file directly (`python3 prompts/eval/run.py`) by
# falling back to absolute imports relative to the repo root.
try:
    from .judge import ClaudeJudge, JudgeVerdict, PresetMeta
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from judge import ClaudeJudge, JudgeVerdict, PresetMeta  # type: ignore


REPO_ROOT = Path(__file__).resolve().parents[2]
PROMPTS_DIR = REPO_ROOT / "prompts"
DEFAULT_BRIDGE_URL = "http://localhost:9335/action"


# -- Bridge call --------------------------------------------------------------


def call_bridge(action: str, parameters: dict, bridge_url: str = DEFAULT_BRIDGE_URL, timeout: float = 60.0) -> dict:
    payload = json.dumps({"action": action, "parameters": parameters}).encode("utf-8")
    req = urllib.request.Request(
        bridge_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise SystemExit(f"Cannot reach Vibalos bridge at {bridge_url}: {e}\nIs the app running?")


def preview_preset(preset_name: str, user_input: str, bridge_url: str = DEFAULT_BRIDGE_URL) -> tuple[str, str, str]:
    """Returns (engine, model, model_output) by name-lookup in the running app's catalog."""
    resp = call_bridge("preview_preset", {"name": preset_name, "input": user_input}, bridge_url=bridge_url)
    if not resp.get("success"):
        raise RuntimeError(f"preview_preset failed: {resp.get('data', {}).get('message', resp)}")
    out = resp["data"].get("output", {})
    return out.get("engine", "unknown"), out.get("model", "unknown"), out.get("result", "")


def preview_template(meta: PresetMeta, user_input: str, bridge_url: str = DEFAULT_BRIDGE_URL) -> tuple[str, str, str]:
    """Returns (engine, model, model_output) by sending the YAML template
    directly. Bypasses the catalog so we can test new versions without
    syncing them in first."""
    params = {
        "template": meta.template,
        "input": user_input,
        "name": meta.name,
        "tagMode": meta.tag_mode,
        "emojiUsage": meta.emoji_usage,
        "languageMode": meta.language_mode,
        "tone": meta.tone,
        "toneIntensity": str(meta.tone_intensity),
        "writingStyle": meta.writing_style,
    }
    resp = call_bridge("preview_template", params, bridge_url=bridge_url)
    if not resp.get("success"):
        raise RuntimeError(f"preview_template failed: {resp.get('data', {}).get('message', resp)}")
    out = resp["data"].get("output", {})
    return out.get("engine", "unknown"), out.get("model", "unknown"), out.get("result", "")


# -- Catalog/corpus loading ----------------------------------------------------


@dataclass
class PresetEntry:
    slug: str
    category_slug: str
    meta: PresetMeta


def load_preset(category_slug: str, preset_slug: str) -> PresetEntry:
    yaml_path = PROMPTS_DIR / "presets" / category_slug / f"{preset_slug}.yaml"
    if not yaml_path.exists():
        raise SystemExit(f"Preset YAML not found: {yaml_path}")

    text = yaml_path.read_text()
    if not text.startswith("---"):
        raise SystemExit(f"{yaml_path}: expected YAML frontmatter")
    parts = text.split("---", 2)
    fm = yaml.safe_load(parts[1]) or {}
    body = parts[2].strip()

    return PresetEntry(
        slug=preset_slug,
        category_slug=category_slug,
        meta=PresetMeta(
            name=fm["name"],
            template=body,
            tag_mode=str(fm.get("tagMode", "off")) if not isinstance(fm.get("tagMode"), bool) else ("off" if not fm["tagMode"] else "on"),
            emoji_usage=str(fm.get("emojiUsage", "off")) if not isinstance(fm.get("emojiUsage"), bool) else ("off" if not fm["emojiUsage"] else "on"),
            language_mode=fm.get("languageMode", "keepOriginal"),
            tone=fm.get("tone", "neutral"),
            tone_intensity=int(fm["toneIntensity"]) if isinstance(fm.get("toneIntensity"), int) else {"subtle": 0, "balanced": 1, "strong": 2}.get(fm.get("toneIntensity", "balanced"), 1),
            writing_style=fm.get("writingStyle", "default"),
        ),
    )


def load_corpus(category_slug: str, preset_slug: str) -> list[str]:
    corpus_path = PROMPTS_DIR / "corpus" / category_slug / f"{preset_slug}.txt"
    if not corpus_path.exists():
        return []
    raw = corpus_path.read_text()
    blocks = []
    current = []
    for line in raw.splitlines():
        if line.lstrip().startswith("#"):
            continue
        if not line.strip():
            if current:
                blocks.append("\n".join(current).strip())
                current = []
            continue
        current.append(line)
    if current:
        blocks.append("\n".join(current).strip())
    return [b for b in blocks if b]


def discover_presets() -> list[tuple[str, str]]:
    """Walk presets/ and return (category_slug, preset_slug) pairs."""
    out = []
    presets_root = PROMPTS_DIR / "presets"
    for cat_dir in sorted(presets_root.iterdir()):
        if not cat_dir.is_dir():
            continue
        for yaml_file in sorted(cat_dir.glob("*.yaml")):
            out.append((cat_dir.name, yaml_file.stem))
    return out


# -- Eval loop -----------------------------------------------------------------


@dataclass
class EvalResult:
    preset_name: str
    preset_slug: str
    user_input: str
    engine: str
    model: str
    model_output: str
    verdict: JudgeVerdict


@dataclass
class EvalReport:
    preset_slug: str
    preset_name: str
    results: list[EvalResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.verdict.passed)

    @property
    def pass_rate(self) -> float:
        return self.passed / self.total if self.total else 0.0


def run_eval_for_preset(entry: PresetEntry, judge: ClaudeJudge | None, bridge_url: str, max_inputs: int | None = None) -> EvalReport:
    inputs = load_corpus(entry.category_slug, entry.slug)
    if max_inputs is not None:
        inputs = inputs[:max_inputs]

    if not inputs:
        print(f"⚠️  No corpus for {entry.category_slug}/{entry.slug} — skipping.")
        return EvalReport(preset_slug=entry.slug, preset_name=entry.meta.name)

    report = EvalReport(preset_slug=entry.slug, preset_name=entry.meta.name)

    for i, user_input in enumerate(inputs, start=1):
        print(f"  [{i}/{len(inputs)}] {entry.meta.name}: {user_input[:60]}{'…' if len(user_input) > 60 else ''}")
        # Use preview_template so the eval always tests the YAML's
        # current template, regardless of whether the running app's
        # catalog has been synced to the latest version.
        engine, model, output = preview_template(entry.meta, user_input, bridge_url=bridge_url)
        if judge is None:
            verdict = JudgeVerdict(passed=False, scores={}, reasons=["dry-run"], suggested_template=None, raw_response="")
        else:
            verdict = judge.judge(entry.meta, user_input, output)
        report.results.append(EvalResult(
            preset_name=entry.meta.name,
            preset_slug=entry.slug,
            user_input=user_input,
            engine=engine,
            model=model,
            model_output=output,
            verdict=verdict,
        ))
        if judge is None:
            preview = output.replace("\n", " ⏎ ")[:120]
            print(f"      📤 {preview}{'…' if len(output) > 120 else ''}")
        else:
            status = "✅ PASS" if verdict.passed else "❌ FAIL"
            print(f"      {status}  scores={verdict.scores}")
            if verdict.reasons:
                for r in verdict.reasons[:3]:
                    print(f"        → {r}")

    return report


# -- Report formatting ---------------------------------------------------------


def report_to_markdown(reports: list[EvalReport]) -> str:
    lines = []
    lines.append(f"# Vibalos preset eval report\n")
    lines.append(f"_Generated {time.strftime('%Y-%m-%d %H:%M %Z')}_\n")

    total = sum(r.total for r in reports)
    passed = sum(r.passed for r in reports)
    overall = passed / total if total else 0.0
    lines.append(f"**Overall pass rate: {overall*100:.0f}%** ({passed}/{total})\n")

    lines.append("\n## Per-preset summary\n")
    lines.append("| Preset | Pass rate | Engine / Model |")
    lines.append("|---|---|---|")
    for r in reports:
        if r.total == 0:
            lines.append(f"| {r.preset_name} | _no corpus_ | — |")
        else:
            engine_model = f"{r.results[0].engine} / {r.results[0].model}"
            lines.append(f"| {r.preset_name} | {r.passed}/{r.total} ({r.pass_rate*100:.0f}%) | {engine_model} |")

    lines.append("\n## Failures\n")
    any_fail = False
    for r in reports:
        for result in r.results:
            if result.verdict.passed:
                continue
            any_fail = True
            lines.append(f"### {r.preset_name}")
            lines.append(f"**Input:** `{result.user_input}`")
            lines.append(f"**Output:** ```\n{result.model_output}\n```")
            lines.append(f"**Scores:** `{result.verdict.scores}`")
            if result.verdict.reasons:
                lines.append("**Reasons:**")
                for reason in result.verdict.reasons:
                    lines.append(f"- {reason}")
            if result.verdict.suggested_template:
                lines.append("\n**Suggested template:**")
                lines.append("```")
                lines.append(result.verdict.suggested_template)
                lines.append("```")
            lines.append("")
    if not any_fail:
        lines.append("_None — all evaluated outputs passed._")

    return "\n".join(lines) + "\n"


# -- CLI -----------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", default="all", help="Preset slug (e.g. improve-prompt) or 'all'")
    parser.add_argument("--category", default=None, help="Limit to a category slug (e.g. prompts). Ignored when --preset is set explicitly.")
    parser.add_argument("--max-inputs", type=int, default=None, help="Cap inputs per preset")
    parser.add_argument("--bridge-url", default=DEFAULT_BRIDGE_URL, help="Vibalos moinsen bridge URL")
    parser.add_argument("--output", default=None, help="Write Markdown report to this path (default: stdout)")
    parser.add_argument("--dry-run", action="store_true", help="Run engine only, skip Claude judge (no API key needed)")
    args = parser.parse_args()

    judge = None if args.dry_run else ClaudeJudge()

    targets: list[PresetEntry] = []
    if args.preset == "all":
        for cat_slug, slug in discover_presets():
            if args.category and cat_slug != args.category:
                continue
            targets.append(load_preset(cat_slug, slug))
    else:
        # Find by slug
        matches = [
            (cat_slug, slug)
            for cat_slug, slug in discover_presets()
            if slug == args.preset and (args.category is None or cat_slug == args.category)
        ]
        if not matches:
            raise SystemExit(f"Preset '{args.preset}' not found. Available:\n" + "\n".join(f"  {c}/{s}" for c, s in discover_presets()))
        for cat_slug, slug in matches:
            targets.append(load_preset(cat_slug, slug))

    print(f"Evaluating {len(targets)} preset{'s' if len(targets) != 1 else ''}…\n")

    reports: list[EvalReport] = []
    for entry in targets:
        print(f"➤ {entry.meta.name} ({entry.category_slug}/{entry.slug})")
        report = run_eval_for_preset(entry, judge, args.bridge_url, max_inputs=args.max_inputs)
        reports.append(report)
        print()

    md = report_to_markdown(reports)
    if args.output:
        out_path = Path(args.output)
        if out_path.is_dir() or args.output.endswith("/"):
            out_path = Path(args.output) / f"eval-{time.strftime('%Y-%m-%d-%H%M%S')}.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md)
        print(f"Wrote report to {out_path}")
    else:
        print(md)


if __name__ == "__main__":
    main()
