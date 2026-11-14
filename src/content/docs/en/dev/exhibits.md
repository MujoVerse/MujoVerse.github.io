---
title: Add a robot to the catalogue
description: "Export an exhibit from MJCF: mesh decimation, pose clips and licence checks."
---

Catalogue exhibits are display-only: decimated visual meshes (RVM1) plus precomputed link poses (RMR1), with no physics or policy. `MujoBots/scripts/exhibits/catalog.json` is the single source of truth; `scripts/export-exhibit.py` exports each entry to `hf-assets/exhibits/<id>/` and rebuilds the index and the names in the language files.

## Steps

1. Put the source repository under `../robot-sources/` and **treat it as data; never run its code**.
2. Read its `LICENSE` (rules below) and add an entry to `catalog.json`:
   - `id`, `name`, `nameZh`, `maker`, `year` (first public release; `null` if unsure), `category` (`humanoid|quadruped|biped|arm|hand|mobile|aerial|other`);
   - `blurb` / `blurbZh`: one factual sentence each, no hype, nothing you cannot verify;
   - `mjcf`, `license`, `spdx`, `source`, `commit`;
   - display: `keyframe` (prefer the model's `home`/`stand`), `pose` (joint overrides), `groups` (when the visual/collision split is unusual), `triangles` (default 40,000; 25k–40k for robots, fewer for drones and small parts), `mount` (`[rx, ry, rz]` degrees for models that would lie down or face sideways). Robots must face +x.
   - clips: `{"kind": "pose"}`; `{"kind": "sweep", "joints": "<regex>", "amplitude": 0.15}` for arms, hands and grippers; `{"kind": "qpos", ...}` for redistributable motion data. **Do not invent locomotion for legged robots.**
3. Export to a scratch directory and look at it first:

   ```sh
   .tools/exporter-venv/bin/python -I scripts/export-exhibit.py --catalog scripts/exhibits/catalog.json \
       --sources ../robot-sources --out temp/exhibits-build/out --only <id>
   ```

   The exporter warns when a clip dips below the plinth; fix the pose or lower the sweep amplitude.
4. Export for real (add `--lang src/main/resources/assets/mujobots/lang`), keep the total under about 90 MB (`du -sh hf-assets/exhibits`), and run `./gradlew compileClientJava test`.
5. Publish the assets with `scripts/hf-assets.py upload`, which updates `assets.lock.json`.

## Licence rules

- Only include models whose `LICENSE` allows redistribution and modification (Apache-2.0, MIT, BSD-2/3-Clause and similar). **Never** include non-commercial, no-derivatives or "all rights reserved" assets.
- Set `spdx` from the actual `LICENSE` text, not a README badge. MuJoCo Menagerie licences are per model directory.
- The exporter copies the `LICENSE` into every exhibit folder; keep it there, since BSD and MIT require the notice to ship with the meshes.
- Motion data is an asset too: use it only when the repository licence covers it (booster_assets is BSD-3-Clause for the whole repository, including `motions/`).
