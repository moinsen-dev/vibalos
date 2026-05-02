# Vibalos Prompt Catalog

The 32 polish presets that ship with [Vibalos](https://vibalos.moinsen.dev),
maintained as YAML files. The macOS app pulls `catalog.json` from this
folder via its built-in sync feature. **Anyone can propose a new preset
via Pull Request** — every PR runs through an automated eval gate
before it can be merged.

## Layout

```
prompts/
├── catalog.json          # Generated artifact — do not hand-edit
├── categories.yaml       # Category definitions (slugs, UUIDs, modifier banks)
├── presets/<cat>/*.yaml  # Source-of-truth: one YAML per preset
├── corpus/<cat>/*.txt    # Realistic test inputs the eval runs against
├── eval/                 # Python eval harness + Claude-Code-as-judge loop
└── bundle.py             # Regenerates catalog.json from YAML sources
```

The YAML format is frontmatter + template body, like Claude Code skills:

```yaml
---
id: <fresh-uuid>
name: My New Preset
isEnabled: true
sortOrder: 0
source: community
recommendedEngines:
  - engine: ollama
    model: gemma3:4b
    notes: "Tested DE+EN, output is structured."
---
Polish the text below into …
Preserve the user's intent and language. Return only the result.

{{text}}
```

## Use it

In Vibalos:

1. Settings → **Catalog Source**
2. Toggle **Enable community presets**
3. Click **Sync Now**

The default catalog URL points at `prompts/catalog.json` on the `main`
branch of this repo. You can also paste any other HTTPS-reachable
`catalog.json` (e.g. your own private fork) to use a different source.

## Contribute a preset

See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the full PR workflow.
TL;DR:

1. Pick a fresh UUID (`uuidgen`) and write
   `presets/<category-slug>/<preset-slug>.yaml`.
2. Add 5-10 realistic test inputs (DE, EN, edge cases) at
   `corpus/<category-slug>/<preset-slug>.txt`.
3. Run the bundler locally: `python3 prompts/bundle.py`. It validates
   UUIDs, schema, and `{{text}}` placeholders, then regenerates
   `catalog.json`.
4. Open a Pull Request. CI runs the bundler check + eval harness;
   PR is blocked if pass-rate < 80%.

## Eval harness

Every preset is tested against its corpus through Vibalos's actual
prompt-rendering and engine pipeline (Ollama or Apple Foundation),
then judged by Claude Code:

```bash
# 1. Run engine, write briefing + state
python3 prompts/eval/run.py --preset improve-prompt --emit-briefing eval-out/

# 2. Paste eval-out/briefing.md into a Claude Code chat.
#    Save Claude's JSON response as verdicts.json.

# 3. Apply verdicts → final report
python3 prompts/eval/run.py --apply-verdicts eval-out/state.json verdicts.json \
                            --output eval-out/report.md
```

**Current state:** all 32 presets pass with `gemma4:e2b-it-q4_K_M`
on a 96-input corpus (3 inputs per preset). Pass-rate climbed from
89% → 96% → 100% across two iterations of template tightening based
on judge feedback.

The judge scores 5 dimensions per output (faithfulness, no-leak,
language match, intent match, structural compliance) with hard-fail
rules for echo-of-instructions, language drift, and emoji/tag
injection when those modifiers are off.

## Conflict precedence inside Vibalos

When the app syncs from this catalog, it applies a deterministic merge:

- Presets currently tagged `userCustom` in your local catalog (i.e.
  ones you edited locally) — never replaced.
- Community presets with the same UUID as one you already have — get
  updated in place; your `shortcutPosition` and `enabled/disabled`
  toggle survive the update.
- Community presets with new UUIDs — get added.

## Schema

`catalog.json` follows the v4 schema defined in
`Vibalos/Models/PresetCatalog.swift` (in the source repo). See
[`CONTRIBUTING.md`](./CONTRIBUTING.md) for the field-by-field
reference.

## License

MIT — anyone can use, modify, or fork this catalog. Submissions are
licensed MIT by the act of opening a PR.
