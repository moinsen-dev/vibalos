# Privacy & Security

Vibalos is built around one principle: **your text, your prompts, your screenshots stay on your Mac**. This page is the receipts.

## What stays on your Mac

| Data | Stored where | Retention |
|---|---|---|
| Polish input/output history | Local SwiftData DB at `~/Library/Containers/dev.moinsen.Vibalos/Data/` | User-controlled |
| Clipboard history | Same DB, separate table | User-controlled, password-manager content excluded |
| Screenshots + OCR text | Same DB, image data inline | User-controlled |
| Polish presets | Same DB | Lifetime of install |
| Active Claude Code session metadata | Read on-demand from `~/.claude/projects/<encoded>/` | Not duplicated by Vibalos |
| License JSON file | `~/Library/Application Support/Vibalos/license.json` | Until license is removed |
| Settings (UserDefaults) | `~/Library/Preferences/dev.moinsen.Vibalos.plist` | Until reset |

**None** of this is sent anywhere by Vibalos.

## What goes off your Mac, and why

Two things, both tied to specific user actions:

### 1. AI inference (when running a Polish preset)

Polish sends your selected text + the preset template to your chosen engine:

- **Ollama** (default) — runs **on your Mac**, no network call. Vibalos talks to `http://localhost:11434`.
- **Apple Foundation Models** — runs **on your Mac**, on-device, no network call. macOS 26+ only.

If you change the engine endpoint to a remote Ollama instance, **then** text leaves your Mac — but to your own server, not to ours.

**There is no "Vibalos cloud."**

### 2. License purchase + activation (one time, per Mac)

When you buy Vibalos:

- Your email + payment info goes to **Lemonsqueezy** (our reseller, the "Merchant of Record"). See their [Privacy Policy](https://www.lemonsqueezy.com/privacy).
- Lemonsqueezy fires a webhook at our **Cloudflare Worker** (`vibalos-license-issuer`) which signs an Ed25519 license over `email + ISO8601 issuedAt` and sends it to you via **Resend** (transactional email).
- Vibalos verifies the signature **offline** when you paste the license JSON into the activation window. There is **no phone-home**.

Once activated, your Mac never talks to our infrastructure again — except for Sparkle update checks (next section).

### 3. Update checks via Sparkle

Vibalos polls `https://vibalos.moinsen.dev/appcast.xml` periodically (default: once per day) to check for new releases. The URL is reachable from any browser.

What Sparkle sends in the request:

- Standard HTTP headers (User-Agent identifies the Vibalos version, your macOS version, your Mac's CPU architecture)
- Nothing else. No license info, no usage data, no telemetry.

Updates themselves are **EdDSA-signed** by the maintainer — your installed Vibalos verifies the signature before installing, so even a compromised update server can't push a malicious update.

## What's deliberately not built

- **No telemetry.** Not even "anonymous usage stats." Not even crash reports (yet — Sentry-style integration would have to be opt-in if it ever ships).
- **No accounts.** No Vibalos login. Your license is a JSON file, not an account.
- **No analytics.** No Google Analytics, no Plausible, no anything on the landing page beyond Cloudflare's edge-level request log.
- **No remote feature flags.** What you see is what's in the binary you installed.

## How to verify

This page describes intent. To verify:

- Open **Activity Monitor → Network** while using Vibalos. The only outbound traffic should be to your Ollama endpoint (if used) and the Sparkle appcast URL.
- Run [Little Snitch](https://www.obdev.at/products/littlesnitch/) or similar. Set Vibalos to "ask for every connection." You should be asked exactly twice: once for Ollama (if used), once for the appcast.
- Inspect the local SwiftData DB with the Apple [SwiftData Inspector](https://developer.apple.com/documentation/swiftdata) or any sqlite browser — it's your data, you can read it.

## Compliance

A complete data-flow map for compliance reviews lives at [vibalos.moinsen.dev/datenfluss](https://vibalos.moinsen.dev/datenfluss) (DE) / [vibalos.moinsen.dev/en/data-flow](https://vibalos.moinsen.dev/en/data-flow) (EN). It includes:

- The full diagram (where every byte goes)
- A GDPR Art. 28 statement (no DPA required — Vibalos doesn't process data on behalf of a controller)
- An EU AI Act Art. 50 statement (Vibalos is an interface to local AI, not a model provider — Art. 50 obligations fall on Ollama/Apple/etc.)
- A "verify it yourself" walkthrough using Activity Monitor and Little Snitch

If you need a written one-pager addressed to your DPO or auditor, email `business@moinsen.dev` — happy to produce one.

## Changes to this page

Material changes to data handling are versioned in this wiki's git history. Watch the wiki repo for notifications, or check `git log Privacy-and-Security.md` if you want to see what's evolved.
