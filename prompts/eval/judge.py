"""Claude-as-judge wrapper for preset output evaluation.

Sends (preset metadata, user input, model output) to Claude Sonnet,
gets back a structured verdict: pass/fail per criterion plus optional
suggested template fix.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Optional

try:
    import anthropic
except ImportError as e:
    raise SystemExit(
        "Missing dependency: anthropic. Install with:\n"
        "  pip3 install -r prompts/eval/requirements.txt"
    ) from e


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


class ClaudeJudge:
    def __init__(self, api_key: Optional[str] = None, model: str = JUDGE_MODEL) -> None:
        api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise SystemExit(
                "ANTHROPIC_API_KEY is not set. Export it or pass --api-key."
            )
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def judge(self, preset: PresetMeta, user_input: str, model_output: str) -> JudgeVerdict:
        prompt = JUDGE_PROMPT_TEMPLATE.format(
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
