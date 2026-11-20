---
title: Licences and credits
description: "Licences of the four mods and the sources of robot models, motions and libraries."
---

The code of all four mods (MujoCraft, MujoBots, MinePilot, MineArena) is licensed under **Apache-2.0**. The models, motions and libraries below keep their own licences; licence texts that must travel with a file are bundled in the corresponding jar.

## Robots

### Booster T2

- **Robot model, walking and get-up control:** from Booster Robotics' T2 software stack; walking and get-up ship with the T2 firmware. Booster also publishes T2 robot descriptions under BSD-3-Clause in [booster_assets](https://github.com/BoosterRobotics/booster_assets).
- **v3 visual meshes, materials and textures:** made by the MujoVerse team.

### Unitree G1

- **Robot model and meshes:** the G1 29-DoF description packaged in NVIDIA [GR00T-WholeBodyControl](https://github.com/NVlabs/GR00T-WholeBodyControl) (Apache-2.0).
- **SONIC whole-body controller weights:** [nvidia/GEAR-SONIC](https://huggingface.co/nvidia/GEAR-SONIC), NVIDIA Open Model Agreement, not retrained. The full licence ships in the jar.
- **Walk, backward, side-step and turn reference motions:** generated with [ARDY-G1](https://github.com/nv-tlabs/ardy) (code Apache-2.0; weights under the NVIDIA Open Model Agreement, which claims no ownership of outputs). Prompts, seeds and selected frames are recorded in `motions-provenance.json` inside the jar.

### The 33 catalogue robots

From [MuJoCo Menagerie](https://github.com/google-deepmind/mujoco_menagerie) and [booster_assets](https://github.com/BoosterRobotics/booster_assets), including Booster's published dance motions. Every robot folder carries its upstream `LICENSE` (Apache-2.0, MIT, BSD-3-Clause or BSD-2-Clause), and `robot.json` records the source URL, commit and file checksums. Meshes were simplified and re-encoded; nothing else was changed.

Robot names and brands belong to their owners; their appearance here does not imply endorsement.

## Physics and matches

- **MuJoCo** ([google-deepmind/mujoco](https://github.com/google-deepmind/mujoco)): Apache-2.0. The native library ships with MujoCraft together with its upstream third-party notices.
- **RoboCup GameController 7.0** ([RoboCup-HumanoidSoccerLeague/GameController](https://github.com/RoboCup-HumanoidSoccerLeague/GameController)): MIT, ships with MineArena.
- **Football physics parameters** follow the team's RoboCup Arena runtime. The black-and-white ball texture is the team's own.
- **Valkyrien Skies 2**: LGPL-3.0. The VS2 add-on only calls its public API; no VS2 code is copied or bundled.

## Runtime libraries

- **ONNX Runtime** Java 1.31.1: MIT, ships with MujoBots (Windows x64, Linux x64, macOS arm64).
- **Minecraft** is a Mojang/Microsoft product; **Fabric Loader / Fabric API** (Apache-2.0) are dependencies. Neither is included in our files.

## Deluxe museum edition

The decoration mods, Sodium, Iris and the Complementary shaders in the deluxe modpack are downloaded from Modrinth by the modpack, keep their own licences, and are not part of the files we distribute.

## Browser mod playtest

- [MuJoCo 3.8 WebAssembly (Apache-2.0)](/licenses/playtest/mujoco.txt)
- [Three.js (MIT)](/licenses/playtest/three.txt)
- [Lucide (ISC, with the Feather MIT notice)](/licenses/playtest/lucide.txt)
