# mujoverse.github.io

Homepage and documentation for the MujoVerse mods. Astro + Starlight, static output for GitHub Pages.

```sh
npm install
npm run dev      # http://localhost:4321
npm run build    # -> dist/
```

- Landing page: `src/components/Landing.astro` (Chinese at `/`, English at `/en/`)
- Docs: `src/content/docs/` (Chinese) and `src/content/docs/en/` (English)
- Media: `public/media/` — real in-game captures from the MujoVerse acceptance runs

## Museum web preview

`/demo/` and `/en/demo/` embed the upstream Minecraft Web Client v2.4.0 on demand. The site ships only the museum world export, not a copy of the game client or its assets. There is no multiplayer server or proxy. The game loads the world from the configured public site URL; for local world changes, drag the local ZIP into the upstream client to test before deploying.

To refresh it, use an already built **vanilla-block** museum save (not the deluxe world or a datapack bootstrap):

```sh
python -m pip install nbtlib==2.0.4
python scripts/export-museum-preview.py "/path/to/built/MujoVerse Museum" public/worlds/museum-preview.zip
```

The initial source was `MujoBots/.runtime/museum-hero/saves/MujoVerse Museum` in the development workspace. The export contains 130 terrain chunks, with placeholder blocks for robot pedestals and a synthetic spawn profile. No original player data, entities, signs, command data, custom assets or mod JARs are included. Do not replace it with a ZIP of the full source save.
