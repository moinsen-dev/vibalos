# Vibalos Prompt Catalog

Community-curated polish presets for [Vibalos](https://vibalos.moinsen.dev).
The macOS app reads `catalog.json` from this folder via its built-in
sync feature; pull requests against this folder become new community
presets.

## Use it

In Vibalos:

1. Settings → **Catalog Source**
2. Toggle **Enable community presets**
3. Click **Sync Now**

The default catalog URL points at `prompts/catalog.json` on the `main`
branch of this repo. You can also paste any other HTTPS-reachable
`catalog.json` (e.g. your own GitHub repo) to use a custom source —
the schema is the same.

## Contribute a preset

See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the full PR workflow.
TL;DR:

1. Add an entry to `catalog.json` under `presets` with a fresh UUID,
   the right `categoryID`, and a template containing `{{text}}`.
2. Add a Markdown source doc under
   `presets/<category>/<preset-slug>.md` with rationale and example
   outputs.
3. Add 5-10 test inputs in `corpus/<category>/<preset-slug>.txt`.
4. Open a Pull Request. CI runs the eval harness; the PR is blocked
   if pass-rate < 80%.

## Conflict precedence inside Vibalos

Vibalos applies a deterministic merge during sync:

- **Built-in presets** (shipped with the app) — never replaced
- **User-customized presets** — never replaced
- **Community presets with the same UUID** — get updated in place
- **Community presets with new UUIDs** — get added

User preferences attached to community presets (shortcut position,
enabled/disabled toggle) survive across updates.

## Schema

`catalog.json` follows the v3 schema defined in
`Vibalos/Models/PresetCatalog.swift` (in the source repo). See
`CONTRIBUTING.md` for the field-by-field reference.

## License

MIT — anyone can use, modify, or fork this catalog. Submissions are
licensed MIT by the act of opening a PR.
