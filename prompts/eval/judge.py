"""Claude-as-judge wrapper for preset output evaluation.

Two backends:

- `ClaudeCodeJudge` (default): shells out to the local `claude` CLI in
  --bare --print mode. Uses the user's existing Claude Code session,
  no API key needed. Slower per-call (~2-4s startup) but free for the
  user.

- `AnthropicAPIJudge`: direct Anthropic API via the `anthropic` SDK.
  Requires ANTHROPIC_API_KEY env var. Fast, but billed.

Both submit the same judge prompt and return the same `JudgeVerdict`
shape so the runner doesn't care which backend is in use.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from typing import Optional

try:
    import anthropic  # type: ignore
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False


JUDGE_MODEL = "claude-sonnet-4-6"

JUDGE_SYSTEM = """You are a strict, fair evaluator of text-polishing prompts.
You score whether a small local model's output actually executed the
prompt's instructions on a user's input. You return ONLY JSON, no prose."""

JUDGE_PROMPT_TEMPLATE = """Evaluate the model output below against the preset's stated intent.

PRESET NAME: {preset_name}
PRESET INTENT (template):
---
{template}
---
RUNTIME MODIFIERS: tagMode={tag_mode}, emojiUsage={emoji_usage}, languageMode={language_mode}, tone={tone}, toneIntensity={tone_intensity}, writingStyle={writing_style}

USER INPUT:
---
{user_input}
---

MODEL OUTPUT:
---
{model_output}
---

Score the output across these criteria. Each is 0-5 (0=fail, 5=excellent):

1. faithfulness: Did the output transform the input as the template instructs?
2. no_leak: Did the output avoid quoting the instructions, the style block,
   or the original prompt verbatim?
3. language_match: Was the requested language preserved (or transformed if
   languageMode says so)?
4. intent_match: Was the user's intent in the input preserved?
5. structure: Did the output respect any structural requirements stated in
   the template (e.g. "use ## Summary and ## Test plan", "one line, no quotes",
   "checklist with - [ ] items")?

HARD FAIL (set pass=false regardless of scores) if any of:
- Output literally repeats the template's bullets / instructions / style controls
- Output is just "Style controls:\\n- Tags:\\n- Emoji use:\\n..." (echo bug)
- Output is empty or whitespace-only
- Output is in a clearly wrong language
- Output adds emoji when emojiUsage=off, or hashtags when tagMode=off

PASS rule: pass=true only if all five criteria are >=3 AND no hard fail.

If pass=false, optionally provide `suggested_template` — a rewritten
version of the preset's template that you believe would fix the
failure modes. Only suggest a rewrite if you're confident; otherwise
return null. Keep `{{text}}` literally in the suggested template.

Return JSON ONLY in this exact shape:
{{
  "pass": <bool>,
  "scores": {{
    "faithfulness": <int 0-5>,
    "no_leak": <int 0-5>,
    "language_match": <int 0-5>,
    "intent_match": <int 0-5>,
    "structure": <int 0-5>
  }},
  "reasons": [<short strings, one per criterion that scored <4>],
  "suggested_template": <string or null>
}}"""


@dataclass
class JudgeVerdict:
    passed: bool
    scores: dict[str, int]
    reasons: list[str]
    suggested_template: Optional[str] = None
    raw_response: str = ""


@dataclass
class PresetMeta:
    name: str
    template: str
    tag_mode: str = "off"
    emoji_usage: str = "off"
    language_mode: str = "keepOriginal"
    tone: str = "neutral"
    tone_intensity: int = 1
    writing_style: str = "default"


def _build_judge_prompt(preset: PresetMeta, user_input: str, model_output: str) -> str:
    return JUDGE_PROMPT_TEMPLATE.format(
        preset_name=preset.name,
        template=preset.template,
        tag_mode=preset.tag_mode,
        emoji_usage=preset.emoji_usage,
        language_mode=preset.language_mode,
        tone=preset.tone,
        tone_intensity=preset.tone_intensity,
        writing_style=preset.writing_style,
        user_input=user_input,
        model_output=model_output,
    )


class AnthropicAPIJudge:
    """Anthropic-API-backed judge. Requires ANTHROPIC_API_KEY."""

    def __init__(self, api_key: Optional[str] = None, model: str = JUDGE_MODEL) -> None:
        if not _ANTHROPIC_AVAILABLE:
            raise SystemExit(
                "anthropic SDK not installed. Install with:\n"
                "  pip3 install -r prompts/eval/requirements.txt"
            )
        api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise SystemExit(
                "ANTHROPIC_API_KEY is not set. Export it or pass --api-key."
            )
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def judge(self, preset: PresetMeta, user_input: str, model_output: str) -> JudgeVerdict:
        prompt = _build_judge_prompt(preset, user_input, model_output)
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=JUDGE_SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in resp.content if block.type == "text").strip()
        parsed = _extract_json(text)
        return JudgeVerdict(
            passed=bool(parsed.get("pass", False)),
            scores=parsed.get("scores", {}),
            reasons=parsed.get("reasons", []),
            suggested_template=parsed.get("suggested_template"),
            raw_response=text,
        )


class ClaudeCodeJudge:
    """DEPRECATED. Subprocess-shelling out to `claude --print` is too
    expensive (each invocation re-creates the Claude Code system
    context, ~$0.30+ per call) and `--bare` mode requires explicit
    ANTHROPIC_API_KEY — defeating the "free for the user" goal.

    Use the briefing/verdicts workflow instead: run `--emit-briefing`,
    paste the resulting Markdown into a Claude Code chat, save the
    JSON response to verdicts.json, then run `--apply-verdicts` to
    finalize the report. See run.py docstring for the recipe.
    """

    def __init__(self, claude_binary: str = "claude", timeout: float = 120.0) -> None:
        self.claude_binary = claude_binary
        self.timeout = timeout

    def judge(self, preset: PresetMeta, user_input: str, model_output: str) -> JudgeVerdict:
        prompt = _build_judge_prompt(preset, user_input, model_output)
        cmd = [
            self.claude_binary,
            "--bare",
            "--print",
            "--output-format", "json",
            "--append-system-prompt", JUDGE_SYSTEM,
            prompt,
        ]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )
        except FileNotFoundError as e:
            raise SystemExit(
                f"claude CLI not found ({self.claude_binary}). "
                "Install Claude Code or pass --judge=anthropic-api with an API key."
            ) from e
        except subprocess.TimeoutExpired as e:
            raise RuntimeError(f"claude CLI timed out after {self.timeout}s") from e

        if result.returncode != 0:
            raise RuntimeError(
                f"claude CLI exited {result.returncode}\nstderr: {result.stderr[:500]}"
            )

        # `--output-format json` returns a result envelope. The actual
        # judge response is in the `result` field as a string (which
        # we then parse as JSON ourselves).
        try:
            envelope = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"claude CLI did not return valid JSON envelope: {e}\nRaw: {result.stdout[:500]}"
            )

        if envelope.get("is_error"):
            raise RuntimeError(f"claude CLI returned error envelope: {envelope.get('result', envelope)}")

        verdict_text = envelope.get("result", "")
        parsed = _extract_json(verdict_text)
        return JudgeVerdict(
            passed=bool(parsed.get("pass", False)),
            scores=parsed.get("scores", {}),
            reasons=parsed.get("reasons", []),
            suggested_template=parsed.get("suggested_template"),
            raw_response=verdict_text,
        )


def make_judge(backend: str = "claude-code", api_key: Optional[str] = None) -> "AnthropicAPIJudge | ClaudeCodeJudge":
    """Factory for the runner. Default is the local Claude Code CLI."""
    if backend == "claude-code":
        return ClaudeCodeJudge()
    if backend in ("anthropic", "anthropic-api", "api"):
        return AnthropicAPIJudge(api_key=api_key)
    raise SystemExit(f"Unknown judge backend: {backend}. Choose 'claude-code' or 'anthropic-api'.")


# Legacy alias — old callers used `ClaudeJudge` for the Anthropic SDK
# path. Keep it pointing to AnthropicAPIJudge so any external scripts
# don't break.
ClaudeJudge = AnthropicAPIJudge


def _extract_json(text: str) -> dict:
    """Extract the JSON object from Claude's response. Tolerant of
    surrounding prose, code fences, etc."""
    # Try plain parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strip code fences
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except json.JSONDecodeError:
            pass

    # Find first {...} block
    brace = re.search(r"\{.*\}", text, re.DOTALL)
    if brace:
        try:
            return json.loads(brace.group(0))
        except json.JSONDecodeError as e:
            raise ValueError(f"Could not parse JSON from judge: {e}\nRaw: {text[:500]}")

    raise ValueError(f"No JSON found in judge response: {text[:500]}")
