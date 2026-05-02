# Vibalos preset eval — paste this to Claude Code

You are evaluating polish-preset outputs. Score each `case` against the preset's `template`. Use the rubric in the schema.

## Schema

```
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
```

## Cases

### case `improve-prompt:1` — Improve Prompt

**Engine:** ollama / gemma4:e2b-it-q4_K_M

**Template:**
```
You are converting a user's rough draft into a precise prompt for an AI assistant.

A good "improved prompt" has all of these:
1. Names a fitting assistant role at the start (e.g. "You are a senior Swift engineer …").
2. States the goal in one direct sentence.
3. Lists 2-4 specific constraints, facts, or edge cases the assistant should respect. Do NOT invent constraints that aren't implied by the draft. Specifically: never pick a programming language, framework, library, or technology stack unless the user named one. If the draft doesn't suggest constraints, list at least 2 obvious failure modes the assistant should handle.
4. Names the desired output format (length, structure, tone) — but stay neutral on implementation choice.
5. Stays in the user's language — German stays German, English stays English.

If the user's draft is short, vague, or conversational, EXPAND it. Add the missing role / goal / output spec yourself based on what the user clearly wants. Do NOT just reword the draft into the same length.

Output rules:
- Return ONLY the improved prompt — one block of plain text, ready to send to an assistant.
- No preamble, no commentary, no code fences, no quotation marks around the result.
- Do not echo the user's original draft.

User's rough draft:
{{text}}
```
**User input:**
```
mach mir mal nen kurzen sketch wie wir die landing page neu strukturieren können
```
**Model output:**
```
Du bist ein erfahrener UX- und Webdesign-Architekt. Deine Aufgabe ist es, einen strukturierten Entwurf vorzulegen, wie eine Landingpage neu strukturiert werden kann. Bitte halte dich an die folgenden Regeln: Der Entwurf muss sich ausschließlich auf die Informationsarchitektur und die Benutzerfreundlichkeit konzentrieren. Vermeide jegliche Spezifikationen bezüglich Technologie oder Designelemente. Berücksichtige dabei die Notwendigkeit, die Kernbotschaft schnell zu vermitteln und die Conversion zu optimieren. Das gewünschte Ergebnis ist ein klar strukturierter Textentwurf.
```

### case `improve-prompt:2` — Improve Prompt

**Engine:** ollama / gemma4:e2b-it-q4_K_M

**Template:**
```
You are converting a user's rough draft into a precise prompt for an AI assistant.

A good "improved prompt" has all of these:
1. Names a fitting assistant role at the start (e.g. "You are a senior Swift engineer …").
2. States the goal in one direct sentence.
3. Lists 2-4 specific constraints, facts, or edge cases the assistant should respect. Do NOT invent constraints that aren't implied by the draft. Specifically: never pick a programming language, framework, library, or technology stack unless the user named one. If the draft doesn't suggest constraints, list at least 2 obvious failure modes the assistant should handle.
4. Names the desired output format (length, structure, tone) — but stay neutral on implementation choice.
5. Stays in the user's language — German stays German, English stays English.

If the user's draft is short, vague, or conversational, EXPAND it. Add the missing role / goal / output spec yourself based on what the user clearly wants. Do NOT just reword the draft into the same length.

Output rules:
- Return ONLY the improved prompt — one block of plain text, ready to send to an assistant.
- No preamble, no commentary, no code fences, no quotation marks around the result.
- Do not echo the user's original draft.

User's rough draft:
{{text}}
```
**User input:**
```
write a function that handles user login
```
**Model output:**
```
You are a senior software developer specializing in secure application logic.
The goal is to write a complete and robust function that handles user login.
Constraints: The function must be designed to handle input validation, secure password storage (using hashing), and appropriate error handling for failed logins. It must accept username and password inputs and return a boolean indicating successful authentication. Do not include any external dependencies or specific frameworks unless requested.
The output should be the complete function implementation along with clear comments explaining the logic and security considerations.
```

### case `improve-prompt:3` — Improve Prompt

**Engine:** ollama / gemma4:e2b-it-q4_K_M

**Template:**
```
You are converting a user's rough draft into a precise prompt for an AI assistant.

A good "improved prompt" has all of these:
1. Names a fitting assistant role at the start (e.g. "You are a senior Swift engineer …").
2. States the goal in one direct sentence.
3. Lists 2-4 specific constraints, facts, or edge cases the assistant should respect. Do NOT invent constraints that aren't implied by the draft. Specifically: never pick a programming language, framework, library, or technology stack unless the user named one. If the draft doesn't suggest constraints, list at least 2 obvious failure modes the assistant should handle.
4. Names the desired output format (length, structure, tone) — but stay neutral on implementation choice.
5. Stays in the user's language — German stays German, English stays English.

If the user's draft is short, vague, or conversational, EXPAND it. Add the missing role / goal / output spec yourself based on what the user clearly wants. Do NOT just reword the draft into the same length.

Output rules:
- Return ONLY the improved prompt — one block of plain text, ready to send to an assistant.
- No preamble, no commentary, no code fences, no quotation marks around the result.
- Do not echo the user's original draft.

User's rough draft:
{{text}}
```
**User input:**
```
ich brauche einen prompt der mir hilft, gute commit messages zu schreiben für deutsche projekte mit gemischtem code
```
**Model output:**
```
Du bist ein Senior Softwareentwickler und Git-Experte mit Spezialisierung auf die Erstellung von Commit Messages. Deine Aufgabe ist es, den Benutzer dabei zu unterstützen, präzise, informative und konventionelle Commit Messages für Softwareprojekte zu verfassen.

Das Ziel ist es, basierend auf dem bereitgestellten Code-Kontext oder der Beschreibung eine hochwertige Commit Message zu generieren, die speziell die Konventionen und den sprachlichen Kontext deutscher Projekte berücksichtigt.

Die folgenden Einschränkungen müssen strikt beachtet werden:
1. Die generierten Commit Messages müssen dem konventionellen Format (z.B. Conventional Commits) folgen.
2. Die Sprache der Commit Messages muss Deutsch sein.
3. Du musst die Komplexität gemischten Codes und die spezifische Natur deutscher Projektkommunikation berücksichtigen.
4. Bei unklaren oder sehr kurzen Eingaben musst du klare und spezifische Vorschläge machen, um Ambiguitäten zu vermeiden.

Das gewünschte Ausgabeformat ist eine direkte, formatierte Commit Message in deutscher Sprache.
```

### case `improve-prompt:4` — Improve Prompt

**Engine:** ollama / gemma4:e2b-it-q4_K_M

**Template:**
```
You are converting a user's rough draft into a precise prompt for an AI assistant.

A good "improved prompt" has all of these:
1. Names a fitting assistant role at the start (e.g. "You are a senior Swift engineer …").
2. States the goal in one direct sentence.
3. Lists 2-4 specific constraints, facts, or edge cases the assistant should respect. Do NOT invent constraints that aren't implied by the draft. Specifically: never pick a programming language, framework, library, or technology stack unless the user named one. If the draft doesn't suggest constraints, list at least 2 obvious failure modes the assistant should handle.
4. Names the desired output format (length, structure, tone) — but stay neutral on implementation choice.
5. Stays in the user's language — German stays German, English stays English.

If the user's draft is short, vague, or conversational, EXPAND it. Add the missing role / goal / output spec yourself based on what the user clearly wants. Do NOT just reword the draft into the same length.

Output rules:
- Return ONLY the improved prompt — one block of plain text, ready to send to an assistant.
- No preamble, no commentary, no code fences, no quotation marks around the result.
- Do not echo the user's original draft.

User's rough draft:
{{text}}
```
**User input:**
```
generate a system that scans GitHub PRs for security issues and posts comments
```
**Model output:**
```
You are a senior software architect specializing in automated security tooling and API integration.
The goal is to design a functional system for automatically scanning GitHub Pull Requests for potential security issues and posting relevant comments.
Constraints: The system must interact with the GitHub API to fetch PR data and post comments, and it must operate without requiring manual intervention after setup. The system must prioritize identifying common security vulnerabilities and must handle cases where API access or comment posting fails.
Desired output format is a detailed system design outline covering the required components, data flow, API considerations, and error handling strategies.
```

### case `improve-prompt:5` — Improve Prompt

**Engine:** ollama / gemma4:e2b-it-q4_K_M

**Template:**
```
You are converting a user's rough draft into a precise prompt for an AI assistant.

A good "improved prompt" has all of these:
1. Names a fitting assistant role at the start (e.g. "You are a senior Swift engineer …").
2. States the goal in one direct sentence.
3. Lists 2-4 specific constraints, facts, or edge cases the assistant should respect. Do NOT invent constraints that aren't implied by the draft. Specifically: never pick a programming language, framework, library, or technology stack unless the user named one. If the draft doesn't suggest constraints, list at least 2 obvious failure modes the assistant should handle.
4. Names the desired output format (length, structure, tone) — but stay neutral on implementation choice.
5. Stays in the user's language — German stays German, English stays English.

If the user's draft is short, vague, or conversational, EXPAND it. Add the missing role / goal / output spec yourself based on what the user clearly wants. Do NOT just reword the draft into the same length.

Output rules:
- Return ONLY the improved prompt — one block of plain text, ready to send to an assistant.
- No preamble, no commentary, no code fences, no quotation marks around the result.
- Do not echo the user's original draft.

User's rough draft:
{{text}}
```
**User input:**
```
so jetzt müssen wir mal kurz schauen ob die docker container alle laufen, kannst du mir das per script abnehmen
```
**Model output:**
```
Du bist ein Systemadministrator, spezialisiert auf Linux-Skripte. Deine Aufgabe ist es, ein Shell-Skript zu erstellen, das den Status aller aktiven Docker-Container überprüft. Das Skript soll die Ergebnisse in einem leicht lesbaren Format ausgeben. Achte darauf, dass das Skript robuste Fehlerbehandlung beinhaltet, falls Docker-Befehle fehlschlagen oder Container nicht erreichbar sind. Das gewünschte Ergebnis ist das vollständige, ausführbare Skript.
```

### case `make-prompt-negotiable:1` — Make Prompt Negotiable

**Engine:** ollama / gemma4:e2b-it-q4_K_M

**Template:**
```
Rewrite the prompt below into a SINGLE new prompt that asks the AI to first push back, ask clarifying questions, or propose alternatives whenever the request is ambiguous, risky, or under-specified — and to proceed only after those questions are addressed.

The rewritten prompt must:
- Be a single new prompt, NOT the original prompt with a meta-instruction prepended.
- Preserve the user's goal verbatim in spirit (not necessarily wording).
- Stay in the user's language.
- Spell out at least one concrete trigger for clarification (e.g. deadline pressure, missing scope, ambiguous tech choice).

If the user's draft is very short or vague (e.g. "setup ci"), still produce a single rewritten prompt that names the goal and adds the clarification-first behaviour — do NOT return only a generic meta-instruction.

Return only the rewritten prompt.

{{text}}
```
**User input:**
```
Schreibe eine komplette Authentication-Lösung mit OAuth2, JWT, Refresh-Tokens und Rate-Limiting für unser Backend. Soll heute fertig sein.
```
**Model output:**
```
Bitte stellen Sie vor der Erstellung einer vollständigen Implementierung einer Authentifizierungslösung mit OAuth2, JWT, Refresh-Tokens und Rate-Limiting für unser Backend alle notwendigen Klarstellungen bereit. Insbesondere benötigen wir die genaue Angabe des zu verwendenden Technologie-Stacks (z.B. Programmiersprache, Framework, Datenbank), die Anforderungen an die Skalierbarkeit und die Art der Rate-Limiting-Implementierung sowie eine realistische Einschätzung des Zeitrahmens, da die Anforderung, dies heute fertigzustellen, ohne diese Details nicht umsetzbar ist.
```

### case `make-prompt-negotiable:2` — Make Prompt Negotiable

**Engine:** ollama / gemma4:e2b-it-q4_K_M

**Template:**
```
Rewrite the prompt below into a SINGLE new prompt that asks the AI to first push back, ask clarifying questions, or propose alternatives whenever the request is ambiguous, risky, or under-specified — and to proceed only after those questions are addressed.

The rewritten prompt must:
- Be a single new prompt, NOT the original prompt with a meta-instruction prepended.
- Preserve the user's goal verbatim in spirit (not necessarily wording).
- Stay in the user's language.
- Spell out at least one concrete trigger for clarification (e.g. deadline pressure, missing scope, ambiguous tech choice).

If the user's draft is very short or vague (e.g. "setup ci"), still produce a single rewritten prompt that names the goal and adds the clarification-first behaviour — do NOT return only a generic meta-instruction.

Return only the rewritten prompt.

{{text}}
```
**User input:**
```
build me an MVP for a marketplace app like Etsy but for digital art
```
**Model output:**
```
I need to build an MVP for a marketplace application focused on digital art, similar in structure to Etsy. Before starting the development, you must first ask clarifying questions regarding the scope, target platform, required features (e.g., payment integration, listing management, community features), and proposed technology stack. You must wait for my answers to these questions before generating any design or development plan.
```

### case `make-prompt-negotiable:3` — Make Prompt Negotiable

**Engine:** ollama / gemma4:e2b-it-q4_K_M

**Template:**
```
Rewrite the prompt below into a SINGLE new prompt that asks the AI to first push back, ask clarifying questions, or propose alternatives whenever the request is ambiguous, risky, or under-specified — and to proceed only after those questions are addressed.

The rewritten prompt must:
- Be a single new prompt, NOT the original prompt with a meta-instruction prepended.
- Preserve the user's goal verbatim in spirit (not necessarily wording).
- Stay in the user's language.
- Spell out at least one concrete trigger for clarification (e.g. deadline pressure, missing scope, ambiguous tech choice).

If the user's draft is very short or vague (e.g. "setup ci"), still produce a single rewritten prompt that names the goal and adds the clarification-first behaviour — do NOT return only a generic meta-instruction.

Return only the rewritten prompt.

{{text}}
```
**User input:**
```
setup ci
```
**Model output:**
```
Before executing any technical task, if the request is ambiguous, risky, or under-specified, you must first push back, ask clarifying questions, or propose viable alternatives. You must wait for the user to address these questions before proceeding with the execution of the requested task.
```

### case `polish-with-claude-code-context:1` — Polish (with Claude Code context)

**Engine:** ollama / gemma4:e2b-it-q4_K_M

**Template:**
```
You are improving a follow-up prompt that the user is about to send to a coding assistant.

If recent assistant replies are provided below, use them as conversational context — they describe where the conversation currently stands. Sharpen the user's prompt so it picks up that context naturally: reference concrete things from those replies when helpful, drop vague filler.

If the recent-replies block is empty or absent, do NOT invent context. Just sharpen the user's prompt on its own — make it more specific, drop filler, fix grammar.

ALWAYS preserve the user's language: German prompt → German output, English prompt → English output. Never translate. If the user's prompt mixes German and English (e.g. "und make it dark mode"), keep the dominant language.

Return only the improved prompt — no preamble, no commentary.

Recent assistant replies (oldest first, most recent last):
{{cc_recent_assistant_all}}

User prompt to improve:
{{text}}
```
**User input:**
```
okay jetzt füg auch noch tests dazu
```
**Model output:**
```
füge nun Tests hinzu.
```

### case `polish-with-claude-code-context:2` — Polish (with Claude Code context)

**Engine:** ollama / gemma4:e2b-it-q4_K_M

**Template:**
```
You are improving a follow-up prompt that the user is about to send to a coding assistant.

If recent assistant replies are provided below, use them as conversational context — they describe where the conversation currently stands. Sharpen the user's prompt so it picks up that context naturally: reference concrete things from those replies when helpful, drop vague filler.

If the recent-replies block is empty or absent, do NOT invent context. Just sharpen the user's prompt on its own — make it more specific, drop filler, fix grammar.

ALWAYS preserve the user's language: German prompt → German output, English prompt → English output. Never translate. If the user's prompt mixes German and English (e.g. "und make it dark mode"), keep the dominant language.

Return only the improved prompt — no preamble, no commentary.

Recent assistant replies (oldest first, most recent last):
{{cc_recent_assistant_all}}

User prompt to improve:
{{text}}
```
**User input:**
```
now also handle the empty input case
```
**Model output:**
```
handle also the empty input case
```

### case `polish-with-claude-code-context:3` — Polish (with Claude Code context)

**Engine:** ollama / gemma4:e2b-it-q4_K_M

**Template:**
```
You are improving a follow-up prompt that the user is about to send to a coding assistant.

If recent assistant replies are provided below, use them as conversational context — they describe where the conversation currently stands. Sharpen the user's prompt so it picks up that context naturally: reference concrete things from those replies when helpful, drop vague filler.

If the recent-replies block is empty or absent, do NOT invent context. Just sharpen the user's prompt on its own — make it more specific, drop filler, fix grammar.

ALWAYS preserve the user's language: German prompt → German output, English prompt → English output. Never translate. If the user's prompt mixes German and English (e.g. "und make it dark mode"), keep the dominant language.

Return only the improved prompt — no preamble, no commentary.

Recent assistant replies (oldest first, most recent last):
{{cc_recent_assistant_all}}

User prompt to improve:
{{text}}
```
**User input:**
```
und make it dark mode
```
**Model output:**
```
Apply the 6 suggested template fixes and then re-evaluate the affected Presets, applying the dark mode theme to the results.
```

### case `write-claude-md-rule:1` — Write CLAUDE.md Rule

**Engine:** ollama / gemma4:e2b-it-q4_K_M

**Template:**
```
You are converting the user's note into a properly structured CLAUDE.md feedback rule.
The note describes how the user wants Claude to behave (or stop behaving) on this project: {{cc_project_name}}.

Output requirements:
- Lead with the rule itself in clear, imperative form (one or two short sentences).
- Add a "**Why:**" line explaining the reason — often a past incident, a strong preference, or a constraint.
- Add a "**How to apply:**" line explaining when/where this guidance kicks in.
- Match the tone of typical CLAUDE.md rules: concise, specific, actionable.
- ALL three lines must be in the SAME language as the user's note. If the note is German, every line including the labels must be German — translate them to "**Warum:**" and "**Wie anwenden:**". Same for any other source language.

Preserve the user's language. Return ONLY the structured rule block, ready to paste into a CLAUDE.md file. No preamble, no commentary, no code fences.

User note:
{{text}}
```
**User input:**
```
claude soll nicht mehr mocks in tests verwenden weil wir letzte woche einen migration-bug deswegen erst in prod gefunden haben, integration-tests sollen echten datenbank treffen
```
**Model output:**
```
Claude soll keine Mocks in Tests verwenden.
Warum: Mocks führten zu einem Migration-Bug, der erst in der Produktion entdeckt wurde.
Wie anwenden: Integrationstests müssen mit einer echten Datenbank interagieren.
```

### case `write-claude-md-rule:2` — Write CLAUDE.md Rule

**Engine:** ollama / gemma4:e2b-it-q4_K_M

**Template:**
```
You are converting the user's note into a properly structured CLAUDE.md feedback rule.
The note describes how the user wants Claude to behave (or stop behaving) on this project: {{cc_project_name}}.

Output requirements:
- Lead with the rule itself in clear, imperative form (one or two short sentences).
- Add a "**Why:**" line explaining the reason — often a past incident, a strong preference, or a constraint.
- Add a "**How to apply:**" line explaining when/where this guidance kicks in.
- Match the tone of typical CLAUDE.md rules: concise, specific, actionable.
- ALL three lines must be in the SAME language as the user's note. If the note is German, every line including the labels must be German — translate them to "**Warum:**" and "**Wie anwenden:**". Same for any other source language.

Preserve the user's language. Return ONLY the structured rule block, ready to paste into a CLAUDE.md file. No preamble, no commentary, no code fences.

User note:
{{text}}
```
**User input:**
```
stop summarizing what you just did at the end of every response, I can read the diff myself
```
**Model output:**
```
Rule: Do not include summaries of previous actions or changes at the end of any response.
Why: The user is able to review the diff and context independently.
How to apply: Omit trailing summaries to ensure the output is only the requested content.
```

### case `write-claude-md-rule:3` — Write CLAUDE.md Rule

**Engine:** ollama / gemma4:e2b-it-q4_K_M

**Template:**
```
You are converting the user's note into a properly structured CLAUDE.md feedback rule.
The note describes how the user wants Claude to behave (or stop behaving) on this project: {{cc_project_name}}.

Output requirements:
- Lead with the rule itself in clear, imperative form (one or two short sentences).
- Add a "**Why:**" line explaining the reason — often a past incident, a strong preference, or a constraint.
- Add a "**How to apply:**" line explaining when/where this guidance kicks in.
- Match the tone of typical CLAUDE.md rules: concise, specific, actionable.
- ALL three lines must be in the SAME language as the user's note. If the note is German, every line including the labels must be German — translate them to "**Warum:**" and "**Wie anwenden:**". Same for any other source language.

Preserve the user's language. Return ONLY the structured rule block, ready to paste into a CLAUDE.md file. No preamble, no commentary, no code fences.

User note:
{{text}}
```
**User input:**
```
immer absolute pfade
```
**Model output:**
```
Immer absolute Pfade verwenden.
Warum: Die Verwendung absoluter Pfade ist eine zwingende Anforderung.
Wie anwenden: Diese Regel gilt für alle generierten Pfade.
```

### case `write-memory-entry:1` — Write Memory Entry

**Engine:** ollama / gemma4:e2b-it-q4_K_M

**Template:**
```
You are converting the user's note into a properly structured Claude Code memory entry for project: {{cc_project_name}}.

Decide which type fits best:
- user — details about the user's role, preferences, or knowledge
- feedback — corrections or validated approaches Claude should remember
- project — facts or decisions about the current project
- reference — pointers to external systems or documentation (e.g. "bugs are tracked in Linear project X", "Grafana dashboard at URL")

CAREFUL with capitalised proper nouns: "Linear" usually refers to the project-management tool (linear.app), not to "linear/sequential" — treat as `reference` type pointing at that tool. Same for tool names like "Notion", "Slack", "GitHub", "Figma", etc.

IMPORTANT — the output MUST start with three dashes (---) on the very first line, then the YAML frontmatter, then three dashes again, then a blank line, then the body. Like this exactly:

---
name: <short kebab-or-space name>
description: <one-line description for relevance matching>
type: <one of: user | feedback | project | reference>
---

<body>

Body guidance:
- For user and reference types, keep the body short and factual (1-2 sentences). Do NOT just echo the user's note — distill it.
- For feedback and project types, structure as: rule or fact, then a "**Why:**" line and a "**How to apply:**" line.

Preserve the user's language. Return ONLY the frontmatter+body block, ready to save as a memory file. No preamble, no commentary, no code fences.

User note:
{{text}}
```
**User input:**
```
uli ist senior data engineer und arbeitet seit zehn jahren mit airflow, kafka und dbt; aktuell baut er die analytics-pipeline für ein fintech-startup neu auf
```
**Model output:**
```
---
name: uli
description: Senior data engineer specializing in Airflow, Kafka, dbt, and building analytics pipelines for fintech startups.
type: user
---

Uli is a senior data engineer with ten years of experience working with Airflow, Kafka, and dbt. He is currently rebuilding the analytics pipeline for a fintech startup.
```

### case `write-memory-entry:2` — Write Memory Entry

**Engine:** ollama / gemma4:e2b-it-q4_K_M

**Template:**
```
You are converting the user's note into a properly structured Claude Code memory entry for project: {{cc_project_name}}.

Decide which type fits best:
- user — details about the user's role, preferences, or knowledge
- feedback — corrections or validated approaches Claude should remember
- project — facts or decisions about the current project
- reference — pointers to external systems or documentation (e.g. "bugs are tracked in Linear project X", "Grafana dashboard at URL")

CAREFUL with capitalised proper nouns: "Linear" usually refers to the project-management tool (linear.app), not to "linear/sequential" — treat as `reference` type pointing at that tool. Same for tool names like "Notion", "Slack", "GitHub", "Figma", etc.

IMPORTANT — the output MUST start with three dashes (---) on the very first line, then the YAML frontmatter, then three dashes again, then a blank line, then the body. Like this exactly:

---
name: <short kebab-or-space name>
description: <one-line description for relevance matching>
type: <one of: user | feedback | project | reference>
---

<body>

Body guidance:
- For user and reference types, keep the body short and factual (1-2 sentences). Do NOT just echo the user's note — distill it.
- For feedback and project types, structure as: rule or fact, then a "**Why:**" line and a "**How to apply:**" line.

Preserve the user's language. Return ONLY the frontmatter+body block, ready to save as a memory file. No preamble, no commentary, no code fences.

User note:
{{text}}
```
**User input:**
```
weekly merge freeze starts every Thursday at 5pm because the mobile team cuts release branches Friday morning
```
**Model output:**
```
---
name: Weekly Merge Freeze Schedule
description: Defines the schedule and rationale for the weekly merge freeze.
type: project
---

The weekly merge freeze starts every Thursday at 5 PM.
**Why:** This timing is implemented because the mobile team cuts release branches on Friday morning.
**How to apply:** Ensure all merge activities are completed before the Thursday 5 PM deadline to accommodate the mobile team's workflow.
```

### case `write-memory-entry:3` — Write Memory Entry

**Engine:** ollama / gemma4:e2b-it-q4_K_M

**Template:**
```
You are converting the user's note into a properly structured Claude Code memory entry for project: {{cc_project_name}}.

Decide which type fits best:
- user — details about the user's role, preferences, or knowledge
- feedback — corrections or validated approaches Claude should remember
- project — facts or decisions about the current project
- reference — pointers to external systems or documentation (e.g. "bugs are tracked in Linear project X", "Grafana dashboard at URL")

CAREFUL with capitalised proper nouns: "Linear" usually refers to the project-management tool (linear.app), not to "linear/sequential" — treat as `reference` type pointing at that tool. Same for tool names like "Notion", "Slack", "GitHub", "Figma", etc.

IMPORTANT — the output MUST start with three dashes (---) on the very first line, then the YAML frontmatter, then three dashes again, then a blank line, then the body. Like this exactly:

---
name: <short kebab-or-space name>
description: <one-line description for relevance matching>
type: <one of: user | feedback | project | reference>
---

<body>

Body guidance:
- For user and reference types, keep the body short and factual (1-2 sentences). Do NOT just echo the user's note — distill it.
- For feedback and project types, structure as: rule or fact, then a "**Why:**" line and a "**How to apply:**" line.

Preserve the user's language. Return ONLY the frontmatter+body block, ready to save as a memory file. No preamble, no commentary, no code fences.

User note:
{{text}}
```
**User input:**
```
linear project ID for pipeline bugs
```
**Model output:**
```
---
name: linear project id for pipeline bugs
description: Reference for Linear project IDs related to pipeline bugs.
type: reference
---

The reference is needed for finding the Linear project ID associated with pipeline bugs.
```

### case `plain-language:1` — Plain Language

**Engine:** ollama / gemma4:e2b-it-q4_K_M

**Template:**
```
Rewrite the selected text in plain language at roughly B1 reading level.
Use short sentences and common words. Avoid jargon, idioms, and complex grammar.

Language rule (critical): keep the user's language. If the input is German, the output must be German — even slang, idioms, and casual expressions must be translated into plain German, NOT into English. Same for any other source language.

Preserve all facts. Return only the rewritten text.

{{text}}
```
**User input:**
```
Aufgrund der Implementierung der neuen DSGVO-konformen Datenverarbeitungsrichtlinien müssen alle Kundeninteraktionen, die im Rahmen unserer Customer-Success-Aktivitäten stattfinden, fortan einer doppelten Verifikation unterzogen werden, bevor personenbezogene Daten in unsere Analyseplattform übertragen werden dürfen.
```
**Model output:**
```
Wegen der neuen DSGVO-Regeln für die Datenverarbeitung müssen wir eine neue Regelung einhalten. Alle Kundeninteraktionen, die während unserer Customer Success Aktivitäten stattfinden, müssen jetzt doppelt überprüft werden. Erst danach dürfen personenbezogene Daten in unsere Analyseplattform übertragen werden.
```

### case `plain-language:2` — Plain Language

**Engine:** ollama / gemma4:e2b-it-q4_K_M

**Template:**
```
Rewrite the selected text in plain language at roughly B1 reading level.
Use short sentences and common words. Avoid jargon, idioms, and complex grammar.

Language rule (critical): keep the user's language. If the input is German, the output must be German — even slang, idioms, and casual expressions must be translated into plain German, NOT into English. Same for any other source language.

Preserve all facts. Return only the rewritten text.

{{text}}
```
**User input:**
```
Pursuant to the recently ratified amendments to our service-level agreement, all instances of degraded performance exceeding the contractually delineated thresholds shall henceforth be subject to a remediation protocol involving cross-functional incident response teams convened within a 30-minute aperture from initial detection.
```
**Model output:**
```
Based on the recent changes to our service agreement, any performance that goes beyond the agreed limits must follow a repair plan. This plan involves teams from different departments. These teams must start within 30 minutes of when the problem is first detected.
```

### case `plain-language:3` — Plain Language

**Engine:** ollama / gemma4:e2b-it-q4_K_M

**Template:**
```
Rewrite the selected text in plain language at roughly B1 reading level.
Use short sentences and common words. Avoid jargon, idioms, and complex grammar.

Language rule (critical): keep the user's language. If the input is German, the output must be German — even slang, idioms, and casual expressions must be translated into plain German, NOT into English. Same for any other source language.

Preserve all facts. Return only the rewritten text.

{{text}}
```
**User input:**
```
Lol das ist krass.
```
**Model output:**
```
Das ist sehr beeindruckend.
```

