# Contributing

## Adding a preset

1. Pick or create a category. To add to a built-in category, use the
   stable UUID from `Vibalos/Models/PresetCatalog.swift`:

   | Category | UUID |
   |---|---|
   | Prompts | `00000000-0000-0000-0000-000000000101` |
   | Social | `00000000-0000-0000-0000-000000000102` |
   | Email | `00000000-0000-0000-0000-000000000103` |
   | Code | `00000000-0000-0000-0000-000000000104` |
   | Notes | `00000000-0000-0000-0000-000000000105` |
   | Translation | `00000000-0000-0000-0000-000000000106` |
   | Writing | `00000000-0000-0000-0000-000000000107` |

   To add a brand-new community category, generate a fresh UUID
   (`uuidgen` on macOS) and add it to `catalog.json` under
   `categories`. Use a UUID that does NOT collide with any built-in.

2. Add an entry to `catalog.json` under `presets`:

   ```json
   {
     "id": "<fresh-uuid>",
     "categoryID": "<built-in or community category UUID>",
     "name": "Preset Name",
     "template": "Instructions ... use {{text}} where the user's selection should land.",
     "isEnabled": true,
     "outputMode": "replaceSelection",
     "tagMode": "off",
     "emojiUsage": "off",
     "languageMode": "keepOriginal",
     "tone": "neutral",
     "toneIntensity": 1,
     "writingStyle": "default",
     "sortOrder": 0,
     "source": "community"
   }
   ```

3. Add a Markdown source doc at
   `presets/<category>/<preset-slug>.md` with rationale, expected
   inputs, sample outputs.

4. Add 5-10 test inputs under
   `corpus/<category>/<preset-slug>.txt` (one per blank-line-separated
   block). Cover at minimum: a German example, an English example, an
   edge case like very short input, and one that previously failed
   in similar presets if applicable.

5. Open a Pull Request. CI runs the eval harness against your preset
   using the test corpus and a local Ollama model. The PR is blocked
   if pass-rate < 80%.

## Quality bar

- Templates must include `{{text}}` exactly once
- Templates should be language-neutral (use modifier "languageMode" to
  control output language, not hardcode it in the template)
- Templates should NOT include style-block-like bullets — the runtime
  appends those for you
- Templates should be ≤ 6 short sentences; verbose templates degrade
  small-model output quality

## License

By submitting a PR you agree to license your contribution under the
MIT License.
