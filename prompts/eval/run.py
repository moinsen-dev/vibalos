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
    from .judge import JudgeVerdict, PresetMeta, make_judge
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from judge import JudgeVerdict, PresetMeta, make_judge  # type: ignore


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
    except urllib.error.HTTPError as e:
        # 4xx/5xx for a single call: the bridge IS reachable, the
        # action just failed. Surface as RuntimeError so the eval
        # loop can record it and continue with the next input.
        body = ""
        try:
            body = e.read().decode("utf-8")
        except Exception:
            pass
        raise RuntimeError(f"bridge HTTP {e.code}: {body[:300]}") from e
    except urllib.error.URLError as e:
        # Connection refused / app not running — abort the sweep,
        # there's nothing useful we can do.
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


def run_eval_for_preset(entry: PresetEntry, judge, bridge_url: str, max_inputs: int | None = None) -> EvalReport:
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
        engine_error: str | None = None
        try:
            engine, model, output = preview_template(entry.meta, user_input, bridge_url=bridge_url)
        except RuntimeError as e:
            # Engine failure (empty Ollama response, model crashed, etc.)
            # is itself a failure mode worth scoring. Record empty
            # output and continue with next input rather than aborting.
            engine, model, output = "ollama", "unknown", ""
            engine_error = str(e)
            print(f"      ⚠️  engine error: {engine_error[:200]}")
        if judge is None:
            verdict = JudgeVerdict(passed=False, scores={}, reasons=["dry-run"] if engine_error is None else [f"engine error: {engine_error}"], suggested_template=None, raw_response="")
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


# -- Briefing / state / verdicts (paste-judge workflow) ----------------------


VERDICTS_SCHEMA_DOC = """\
Return ONLY a JSON object of this shape:
{
  "verdicts": [
    {
      "case_id": "<the case_id from the briefing>",
      "pass": <bool>,
      "scores": {
        "faithfulness": <int 0-5>,
        "no_leak": <int 0-5>,
        "language_match": <int 0-5>,
        "intent_match": <int 0-5>,
        "structure": <int 0-5>
      },
      "reasons": [<short strings, one per criterion that scored <4>],
      "suggested_template": <string or null>
    }
  ]
}

Pass criteria:
- All 5 scores >= 3
- No hard fail: output didn't echo the template/style block, language is right,
  output isn't empty, no emoji when emojiUsage=off, no hashtags when tagMode=off

If pass=false, optionally provide a `suggested_template` rewrite. Keep
`{{text}}` literally inside it. Only suggest a rewrite if confident; else null.
"""


def engine_state_dict(reports: list[EvalReport]) -> dict:
    """Machine-readable state captured after the engine runs but
    before the verdicts are known. Round-trips via JSON so the user
    can store it, judge separately, then resume."""
    return {
        "version": 1,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "reports": [
            {
                "preset_slug": r.preset_slug,
                "preset_name": r.preset_name,
                "results": [
                    {
                        "case_id": f"{r.preset_slug}:{i+1}",
                        "user_input": result.user_input,
                        "engine": result.engine,
                        "model": result.model,
                        "model_output": result.model_output,
                    }
                    for i, result in enumerate(r.results)
                ],
            }
            for r in reports
        ],
    }


def briefing_markdown(reports: list[EvalReport], engine_state: dict) -> str:
    """Paste-ready briefing for Claude Code as judge. Includes the
    schema doc + all cases. Claude reads this and returns
    verdicts.json."""
    out = []
    out.append("# Vibalos preset eval — paste this to Claude Code\n")
    out.append(
        "You are evaluating polish-preset outputs. Score each `case` "
        "against the preset's `template`. Use the rubric in the schema."
    )
    out.append("\n## Schema\n")
    out.append("```")
    out.append(VERDICTS_SCHEMA_DOC.strip())
    out.append("```")

    out.append("\n## Cases\n")
    for r in reports:
        for i, result in enumerate(r.results):
            case_id = f"{r.preset_slug}:{i+1}"
            out.append(f"### case `{case_id}` — {r.preset_name}\n")
            out.append(f"**Engine:** {result.engine} / {result.model}\n")
            # The preset template is the same for every case in a
            # report, so include it once at the case level for
            # convenience.
            out.append("**Template:**")
            out.append("```")
            # Find the original PresetMeta for this preset — quickest
            # via re-loading. But we don't have it here. Embed the
            # template by looking it up in engine_state if present.
            # For now, look it up from the corpus loader.
            # (We re-derive PresetMeta in apply_verdicts side too.)
            out.append("(see prompts/presets/<category>/" + r.preset_slug + ".yaml)")
            out.append("```")
            out.append(f"**User input:**")
            out.append("```")
            out.append(result.user_input)
            out.append("```")
            out.append(f"**Model output:**")
            out.append("```")
            out.append(result.model_output)
            out.append("```")
            out.append("")
    return "\n".join(out) + "\n"


def apply_verdicts(reports: list[EvalReport], verdicts_data: dict) -> None:
    """Mutate `reports` in-place by attaching the verdicts from a
    Claude-Code-produced JSON."""
    by_case = {v["case_id"]: v for v in verdicts_data.get("verdicts", [])}
    for r in reports:
        for i, result in enumerate(r.results):
            case_id = f"{r.preset_slug}:{i+1}"
            v = by_case.get(case_id)
            if v is None:
                # Leave dry-run sentinel; user might have judged a subset
                continue
            result.verdict = JudgeVerdict(
                passed=bool(v.get("pass", False)),
                scores=v.get("scores", {}),
                reasons=v.get("reasons", []),
                suggested_template=v.get("suggested_template"),
                raw_response="",
            )


def reports_from_state(state: dict, presets_by_slug: dict[str, PresetEntry]) -> list[EvalReport]:
    """Reconstruct EvalReport list from a saved engine_state dict."""
    out: list[EvalReport] = []
    for r in state.get("reports", []):
        report = EvalReport(preset_slug=r["preset_slug"], preset_name=r["preset_name"])
        for c in r.get("results", []):
            report.results.append(EvalResult(
                preset_name=r["preset_name"],
                preset_slug=r["preset_slug"],
                user_input=c["user_input"],
                engine=c["engine"],
                model=c["model"],
                model_output=c["model_output"],
                verdict=JudgeVerdict(passed=False, scores={}, reasons=["pending"], suggested_template=None, raw_response=""),
            ))
        out.append(report)
    return out


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


def _select_targets(preset: str, category: str | None) -> list[PresetEntry]:
    targets: list[PresetEntry] = []
    if preset == "all":
        for cat_slug, slug in discover_presets():
            if category and cat_slug != category:
                continue
            targets.append(load_preset(cat_slug, slug))
        return targets
    # Comma-separated multiple slugs supported.
    requested = [s.strip() for s in preset.split(",") if s.strip()]
    available = discover_presets()
    for slug_request in requested:
        matches = [
            (cat_slug, slug)
            for cat_slug, slug in available
            if slug == slug_request and (category is None or cat_slug == category)
        ]
        if not matches:
            raise SystemExit(
                f"Preset '{slug_request}' not found. Available:\n"
                + "\n".join(f"  {c}/{s}" for c, s in available)
            )
        for cat_slug, slug in matches:
            targets.append(load_preset(cat_slug, slug))
    return targets


def _resolve_output_path(value: str, prefix: str, ext: str) -> Path:
    p = Path(value)
    if p.is_dir() or value.endswith("/"):
        return p / f"{prefix}-{time.strftime('%Y-%m-%d-%H%M%S')}.{ext}"
    return p


def main() -> None:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Evaluate Vibalos polish presets against a corpus of test inputs.\n\n"
            "Three workflows:\n"
            "  1. End-to-end with Anthropic API:\n"
            "     export ANTHROPIC_API_KEY=…\n"
            "     run.py --preset improve-prompt --judge anthropic-api --output report.md\n"
            "  2. Engine-only dry run (eyeball outputs, no scoring):\n"
            "     run.py --preset improve-prompt --dry-run\n"
            "  3. Manual paste-judge with Claude Code (recommended, no API key):\n"
            "     a) run.py --preset improve-prompt --emit-briefing eval-out/\n"
            "        → writes briefing.md + state.json\n"
            "     b) Paste briefing.md to a Claude Code chat → save its JSON answer\n"
            "        as verdicts.json\n"
            "     c) run.py --apply-verdicts eval-out/state.json verdicts.json\n"
            "                --output report.md\n"
        ),
    )
    parser.add_argument("--preset", default="all", help="Preset slug or 'all'")
    parser.add_argument("--category", default=None, help="Limit to a category slug (only used with --preset all)")
    parser.add_argument("--max-inputs", type=int, default=None, help="Cap inputs per preset")
    parser.add_argument("--bridge-url", default=DEFAULT_BRIDGE_URL, help="Vibalos moinsen bridge URL")
    parser.add_argument("--output", default=None, help="Write Markdown report to this path (default: stdout)")
    parser.add_argument("--judge", default="anthropic-api", choices=["anthropic-api"], help="Auto-judge backend (only API path supported; for free/Claude-Code-judge use --emit-briefing)")
    parser.add_argument("--dry-run", action="store_true", help="Run engine only, skip judging entirely")
    parser.add_argument("--emit-briefing", default=None, metavar="DIR", help="Run engine, write briefing.md + state.json to DIR for paste-judging by Claude Code")
    parser.add_argument("--apply-verdicts", nargs=2, metavar=("STATE", "VERDICTS"), default=None, help="Skip engine, read engine state JSON + verdicts JSON, produce final report")
    args = parser.parse_args()

    # Mode 3 part b: --apply-verdicts STATE VERDICTS → assemble report
    if args.apply_verdicts is not None:
        state_path, verdicts_path = args.apply_verdicts
        state = json.loads(Path(state_path).read_text())
        verdicts = json.loads(Path(verdicts_path).read_text())
        # Re-derive PresetEntry index for slug→meta lookup. Needed
        # for some edge cases; report rendering doesn't actually use
        # it, but keep the hook in place for future template-aware
        # report features.
        presets_by_slug = {entry.slug: entry for entry in (load_preset(c, s) for c, s in discover_presets())}
        reports = reports_from_state(state, presets_by_slug)
        apply_verdicts(reports, verdicts)
        md = report_to_markdown(reports)
        if args.output:
            out_path = _resolve_output_path(args.output, "eval", "md")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(md)
            print(f"Wrote report to {out_path}")
        else:
            print(md)
        return

    targets = _select_targets(args.preset, args.category)
    print(f"Evaluating {len(targets)} preset{'s' if len(targets) != 1 else ''}…\n")

    auto_judge = None
    if not args.dry_run and args.emit_briefing is None:
        auto_judge = make_judge(backend=args.judge)

    reports: list[EvalReport] = []
    for entry in targets:
        print(f"➤ {entry.meta.name} ({entry.category_slug}/{entry.slug})")
        report = run_eval_for_preset(entry, auto_judge, args.bridge_url, max_inputs=args.max_inputs)
        reports.append(report)
        print()

    if args.emit_briefing is not None:
        out_dir = Path(args.emit_briefing)
        out_dir.mkdir(parents=True, exist_ok=True)
        state = engine_state_dict(reports)
        # Embed each preset's template into the state so the briefing
        # can render it inline (judge needs to see it to score).
        slug_to_template = {entry.slug: entry.meta.template for entry in targets}
        for r in state["reports"]:
            r["template"] = slug_to_template.get(r["preset_slug"], "")
        state_path = out_dir / "state.json"
        state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False))
        briefing = _briefing_with_templates(reports, slug_to_template)
        briefing_path = out_dir / "briefing.md"
        briefing_path.write_text(briefing)
        print(f"Wrote engine state to {state_path}")
        print(f"Wrote paste-ready briefing to {briefing_path}")
        print()
        print("Next steps:")
        print(f"  1. Paste {briefing_path} into a Claude Code chat.")
        print(f"  2. Save Claude's JSON response as verdicts.json")
        print(f"  3. Run: python3 prompts/eval/run.py --apply-verdicts {state_path} verdicts.json --output report.md")
        return

    md = report_to_markdown(reports)
    if args.output:
        out_path = _resolve_output_path(args.output, "eval", "md")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md)
        print(f"Wrote report to {out_path}")
    else:
        print(md)


def _briefing_with_templates(reports: list[EvalReport], slug_to_template: dict[str, str]) -> str:
    """Like briefing_markdown but inlines the preset template per
    case so the judge has everything they need without browsing the
    repo."""
    out = []
    out.append("# Vibalos preset eval — paste this to Claude Code\n")
    out.append(
        "You are evaluating polish-preset outputs. Score each `case` "
        "against the preset's `template`. Use the rubric in the schema."
    )
    out.append("\n## Schema\n")
    out.append("```")
    out.append(VERDICTS_SCHEMA_DOC.strip())
    out.append("```")
    out.append("\n## Cases\n")
    for r in reports:
        template = slug_to_template.get(r.preset_slug, "(template missing)")
        for i, result in enumerate(r.results):
            case_id = f"{r.preset_slug}:{i+1}"
            out.append(f"### case `{case_id}` — {r.preset_name}\n")
            out.append(f"**Engine:** {result.engine} / {result.model}\n")
            out.append("**Template:**")
            out.append("```")
            out.append(template)
            out.append("```")
            out.append(f"**User input:**")
            out.append("```")
            out.append(result.user_input)
            out.append("```")
            out.append(f"**Model output:**")
            out.append("```")
            out.append(result.model_output)
            out.append("```")
            out.append("")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    main()
