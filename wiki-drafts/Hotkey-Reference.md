# Hotkey Reference

All Vibalos hotkeys, with default bindings. Every binding is reconfigurable in **Settings → Shortcuts**.

## Polish presets

Run a Polish preset by selecting text in any app and pressing one of:

| Default | Category | Slot |
|---|---|---|
| `⌥1`–`⌥0` | Prompts (the default category) | 1–10 |
| `⌥⇧1`–`⌥⇧0` | Social | 1–10 |
| `⌥⌃1`–`⌥⌃0` | Email | 1–10 |

You can create as many categories as you like, but only three modifier banks exist (Option, Option-Shift, Option-Control). Categories without a modifier bank still appear in the menu bar but have no direct number shortcut until assigned.

## Pasteboard

| Hotkey | What it does |
|---|---|
| `⌥⌘V` | Open clipboard history. Search by typing, click to copy, `⌥+click` to copy and apply a Polish preset. |

Password-manager apps (1Password, Bitwarden, Apple Passwords) are detected and skipped automatically — their clipboard contents never reach the history.

## Snap (region screenshot + OCR)

| Hotkey | What it does |
|---|---|
| `⌥⌘5` | Region screenshot with built-in Apple Vision OCR. Image and recognized text both land on the clipboard. |

The screenshot also appears as an entry in your pasteboard history. The optional annotation editor (arrows, highlights, text overlays) opens when you click "Annotate…" in the history.

## Tools

| Default | What it does |
|---|---|
| `⌘,` | Open Settings |
| `⌥⌘D` | Dashboard *([#3](https://github.com/moinsen-dev/vibalos/issues/3) — coming in v1.x)* |
| `⌥⌘C` | Send to Claude Code *([#11](https://github.com/moinsen-dev/vibalos/issues/11) — coming in v1.x)* |
| `⌥V` | Voice (push-to-talk) *([#13](https://github.com/moinsen-dev/vibalos/issues/13) — aspirational v2.0)* |

## Reconfiguring

Every hotkey above is just a default. To change:

1. Open Settings (`⌘,`)
2. Go to the Shortcuts pane
3. Click on the hotkey field for any preset or action
4. Press your new combination

Conflicts with system shortcuts or other apps are detected and surfaced.

## Why these defaults

`⌥1`–`⌥0` is the maintainer's choice because:

- The Option key is rarely used by macOS itself, so collisions are minimal
- 10 slots covers most workflows without resorting to chord shortcuts
- Modifier banks let you scale to 30 direct shortcuts without losing the muscle-memory pattern

If you have a strong reason to change them globally, the Settings shortcut pane supports bulk reassignment — but most users find Option-N intuitive.
