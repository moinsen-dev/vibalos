# Vibalos Roadmap

> Living document. Updated when issues move between milestones. The
> [issue tracker](https://github.com/moinsen-dev/vibalos/issues) is
> authoritative for current status — this file is the 50-foot view.

## Status today

**Pre-launch.** Lemonsqueezy account verification is in progress; the
buy URL will appear when KYC clears (typically 24-48h, in our case
landing on Mon/Tue 2026-05-04 / 2026-05-05 due to the German weekend).

Until then: Vibalos installs but isn't yet sold. The landing page
(https://vibalos.moinsen.dev) shows pre-launch status, the GitHub repo
is the way to follow along or shape the roadmap.

## v1.0 — Public Launch

Tracked privately by the maintainer (DMG build, Worker deploy, Resend
domain verification, final legal review). When public testers join the
loop, those tasks will be visible here too.

## v1.x — Quality Wave

Post-launch polish, fluid 1.1 / 1.2 / 1.3 cadence. Most of these are
`dogfood-pain` — the maintainer hits them daily and wants them gone.

- [ ] [#1] Settings: redesign with sidebar layout (Apple-style)
- [ ] [#2] Menu bar: better grouping and section headings
- [ ] [#3] Dashboard window (⌥⌘D): daily stats
- [ ] [#4] Polish: streaming output in HUD (token-by-token)
- [ ] [#5] Polish preset: Write CLAUDE.md Rule
- [ ] [#6] Polish preset: Write Memory Entry
- [ ] [#7] Claude Code: Park / Resume UX polish
- [ ] [#8] Pasteboard: pin items, app-exclude rules, per-type retention
- [ ] [#9] Claude Code: {{cc_recent_qa_*}} and {{cc_*_claude_md}} tokens
- [ ] [#10] Polish preset: Anti-Slop linter against your CLAUDE.md
- [ ] [#11] Claude Code: Send to Claude Code hotkey (polish + dispatch)
- [ ] [#12] Claude Code: Prompt pre-flight (anti-contradiction check)

## v2.0 — Voice Expansion

Aspirational. Bring built-in dictation into the menu bar, deeply tied
to the Polish pipeline. Inspired by [sebsto/wispr](https://github.com/sebsto/wispr)
(open-source, minimal scope by author's design) and the commercial
[wisprflow.ai](https://wisprflow.ai/) (the maintainer's daily driver
— 1.2M words dictated in 12 months).

- [ ] [#13] Foundation: Voice-to-prompt pipeline (engine choice)
- [ ] [#14] Whisper-based dictation engine
- [ ] [#15] Voice presets

## Future / unscheduled

Open questions and aspirational items without a date.

- [ ] [#16] Should Vibalos go open source?
- [ ] [#17] Multi-Mac license tier (3 Macs, €19.99)

## How priorities get decided

Three labels drive the order:

- `dogfood-pain` — the maintainer hit it himself today. Highest priority.
- `community-asked` — surfaced via issue or discussion. Triaged daily.
- `priority:critical` / `priority:high` — set per issue based on impact.

The full method is on the [Method page](https://vibalos.moinsen.dev/methode).

---

[Issues](https://github.com/moinsen-dev/vibalos/issues) ·
[Discussions](https://github.com/moinsen-dev/vibalos/discussions) ·
[Method](https://vibalos.moinsen.dev/methode) ·
[Buy](https://vibalos.moinsen.dev/#download) (when launched)
