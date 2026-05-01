# Wiki drafts

These markdown files are the initial pages for [the Vibalos Wiki](https://github.com/moinsen-dev/vibalos/wiki). They live here in the main repo as drafts because GitHub requires the wiki to be initialized via the browser before its `.wiki.git` repo becomes pushable.

## How to publish

1. Visit https://github.com/moinsen-dev/vibalos/wiki
2. Click **"Create the first page"**
3. Title: `Home`, content: anything (we'll overwrite). Save.
4. Run from the main repo:

   ```bash
   cd /tmp && git clone https://github.com/moinsen-dev/vibalos.wiki.git
   cp /path/to/community-repo/wiki-drafts/*.md /tmp/vibalos.wiki/
   cd /tmp/vibalos.wiki && git add . && git commit -m "Initial wiki content" && git push
   ```

The drafts directory can stay here as a versioned backup — pushing to the wiki doesn't delete it.

## Pages

- `Home.md` — index + roadmap to other pages
- `Hotkey-Reference.md` — every hotkey, how to reconfigure
- `Privacy-and-Security.md` — full data-flow disclosure (what stays on the Mac, what doesn't, why)
