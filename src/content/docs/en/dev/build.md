---
title: Build from source
description: "Clone the four repositories, fetch assets, build the release jars and run the tests."
---

## Layout

The four mods are four independent Git repositories, but each Gradle build includes its siblings from neighbouring folders (`../MujoCraft` and so on), so they must sit side by side:

```text
MujoVerse/
├── MujoCraft/    # physics core (MuJoCo JNI)
├── MujoBots/     # robots, catalogue, rendering, control API
├── MinePilot/    # driving, local bridge, Python package in python/
└── MineArena/    # football pitches, GameController, matches
```

```sh
mkdir MujoVerse && cd MujoVerse
for r in MujoCraft MujoBots MinePilot MineArena; do git clone https://github.com/MujoVerse/$r.git; done
```

## Toolchain

- **JDK 21.** On macOS (Apple silicon) `MujoCraft/scripts/setup.sh` downloads Corretto 21 into `MujoCraft/.tools/jdk`; elsewhere install JDK 21 and set `JAVA_HOME`.
- MuJoCo and GameController native libraries for all three platforms are prebuilt in `MujoCraft/native/prebuilt/` and `MineArena/native/prebuilt/`, so a normal build needs no C++ toolchain. See each `native/README.md` to rebuild them.

## Build

```sh
cd MujoCraft && bash scripts/setup.sh
export JAVA_HOME=$PWD/.tools/jdk/Contents/Home     # or your JDK 21
./gradlew build
cd ../MujoBots && ./gradlew build
```

MujoBots' robot models, weights and catalogue meshes (about 300 MB) are not in Git. The `fetchAssets` task downloads the revision pinned in `assets.lock.json` from Hugging Face [MujoVerse/mujobots-assets](https://huggingface.co/MujoVerse/mujobots-assets) into `hf-assets/` and checks every SHA-256.

The MujoBots build produces the core jar and three robot packs (T2, G1, exhibits) and checks every jar:

- each file has a licence entry and provenance record;
- restricted files are blocked by a hash list;
- the ONNX Runtime nested in the G1 pack carries natives for all three platforms.

Outputs land in each repository's `build/libs/`.

## Tests

```sh
./gradlew test             # unit tests
./gradlew runGametest      # GameTests in a real headless Minecraft server
./gradlew runClient        # development client
```

MinePilot's build starts its own and MineArena's GameTest servers. With two game processes running at once, a football test that depends on physics timing can time out; use `--max-workers=1`.

Python package:

```sh
cd MinePilot/python
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -e '.[test,mcp]'
.venv/bin/pytest
```
