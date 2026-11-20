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

`/demo/` and `/en/demo/` embed the upstream Minecraft Web Client v2.4.0 on demand. The site ships only the museum world export, not a copy of the game client or its assets. There is no multiplayer server or proxy. The client loads the read-only `museum-preview/index.json` from the configured public site URL. The exporter also writes a ZIP for download and for testing local changes by dragging the file into the upstream client.

To refresh it, use an already built **vanilla-block** museum save (not the deluxe world or a datapack bootstrap):

```sh
python -m pip install nbtlib==2.0.4
python scripts/export-museum-preview.py "/path/to/built/MujoVerse Museum" public/worlds/museum-preview.zip
```

The initial source was `MujoBots/.runtime/museum-hero/saves/MujoVerse Museum` in the development workspace. The export contains 130 terrain chunks, with placeholder blocks for robot pedestals and a synthetic spawn profile. No original player data, entities, signs, command data, custom assets or mod JARs are included. Do not replace it with a ZIP of the full source save.

## Full Tour playtest

`/playtest/` and `/en/playtest/` use the separate **MujoVerse Full Tour** development save, not the museum. Refresh them from the built 11-station save (check for `mujotour-built.json`):

```sh
python scripts/export-museum-preview.py --full-tour "/path/to/saves/MujoVerse Full Tour" public/worlds/full-tour-preview.zip
```

The browser export preserves the lobby, station floors and connecting paths. It ships only the cropped Overworld terrain with a fresh visitor profile; it excludes entities, sign contents, command blocks, recordings, player files and local mods. The original save and its Fabric runtime stay local.

## Desktop museum

Run `python scripts/package-desktop-museum.py <built-museum-save> <verified-release/mods> <output-directory>` with `nbtlib==2.0.4`. Use the same source save as the web preview, and the archived 0.5.0 build (November 15, 2026) with its `build-receipt.json`. The script produces a world ZIP for Pages and a `.mrpack` for GitHub Releases. It omits player history and replaces pre-0.5.0 calls in the lab with current commands. The included live robots are G1 and Go1; T2 firmware bundles are excluded. Import into a clean 1.21.1 / Fabric 0.16.10 / Java 21 instance before publishing any regenerated archives.
