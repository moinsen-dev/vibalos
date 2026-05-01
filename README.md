# Vibalos

> The AI sidekick for vibe coders. Lives in your macOS menu bar.

**Website:** [vibalos.moinsen.dev](https://vibalos.moinsen.dev)
**Buy:** €9.99 one-time, lifetime, one Mac — [Lemonsqueezy](https://moinsen.lemonsqueezy.com/buy/REPLACE_BEFORE_LAUNCH)

---

## What this repo is for

The community front-door for Vibalos. Use it for:

- 🐛 **[Bug reports](../../issues/new?template=bug_report.md)** — something broken? Tell me.
- 💡 **[Feature requests](../../issues/new?template=feature_request.md)** — what should Vibalos learn next?
- 💬 **[Discussions](../../discussions)** — questions, ideas, conversations.

I read every issue. Solo developer, no support team — but I'm responsive.

## What this repo isn't (yet)

The source code lives in a separate, **private** repository. **Vibalos is not currently open source.**

I'd love it to be — but realistically, with AI coding assistants flooding maintainers with low-quality pull requests right now, I'm not ready to take that on while I'm still shaping the product. I'd rather spend my time shipping features than triaging PRs.

If that changes, you'll know — this README will be the first place I update. In the meantime, **feature requests and bug reports here are the way to influence the roadmap.**

## Why pay €9.99 for what looks like a small app?

Vibalos is one of my **daily-driver tools**. I use it every single day, all day, while coding with Claude Code, Cursor, and ChatGPT. Every annoyance I hit, I fix. Every workflow gap I notice, I close. **You're not buying a snapshot — you're buying the trajectory.**

Loose, honest roadmap (will evolve based on what hurts most):

- More polish presets (memory entries, CLAUDE.md rule writing, prompt pre-flight)
- Smarter Claude Code integration (live session awareness, auto-context injection)
- Voice-to-prompt
- Multi-Mac license tier
- Whatever the issue tracker yells loudest about

Lifetime license, one Mac, no subscriptions, no telemetry, no cloud. €9.99 once, forever.

## Privacy & security

- **100% local.** Your text, prompts, and screenshots never leave your Mac. Vibalos talks to Ollama (locally) or Apple Foundation Models (on-device).
- **No telemetry.** Nothing tracked, nothing reported.
- **Offline license verification.** Your license is an Ed25519-signed JSON blob. Vibalos verifies it without phoning home.
- **Signed auto-updates** via Sparkle with EdDSA signatures — same signing scheme as the license.

## Stack (for the curious)

- Swift + SwiftUI on macOS 26+
- Local AI: Ollama or Apple Foundation Models
- Auto-update: Sparkle (EdDSA-signed)
- Licensing: Cloudflare Worker + Ed25519 signatures + Lemonsqueezy webhooks
- Email delivery: Resend

---

Built solo by [Ulrich Diedrichsen](https://moinsen.dev) in Hamburg.
