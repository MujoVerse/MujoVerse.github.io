---
title: Install
description: "Install the four MujoVerse mods, or download the museum pack."
---

## Requirements

| | |
|---|---|
| Minecraft | Java Edition **1.21.1** |
| Loader | **Fabric Loader 0.16.10** or newer |
| Dependency | **Fabric API** for 1.21.1 |
| OS | Windows x64, Linux x64, macOS (Apple silicon) |
| Memory | **4 GB** or more allocated to the game |

Nothing else to install: the physics engine and the robots' "brains" ship inside the mods.

:::caution[Windows]
The neural-network runtime used by G1, K1, T1 and Go1 needs the Microsoft Visual C++ 2015–2022 Redistributable (x64), which most PCs already have. If it is missing, the game tells you when you spawn one of those robots instead of crashing; everything else keeps working.
:::

## Option 1: mods only

1. Create a Fabric 1.21.1 instance in your launcher (official launcher, Modrinth App, Prism, …).
2. Put these jars in the instance's `mods` folder:

| Mod | Role | Required? |
|---|---|---|
| MujoCraft | physics engine | required |
| MujoBots | robot core | required (needs MujoCraft) |
| Robot packs: T2, G1, K1, T1, Go1, exhibits | one robot or the exhibit set per pack; install what you want | at least one |
| MujoBots ONNX Runtime | neural-network runtime | needed by G1, K1, T1, Go1 |
| MinePilot | drive robots; program and AI interface | recommended |
| MineArena | robot football | optional (needs MujoBots) |
| Fabric API | dependency | required |

3. Start the game, create a **Creative** world, and open the **MujoBots** and "Tools & Utilities" creative tabs.

## Option 2: the museum

To see what the mods can do first, install the museum. It comes in two editions; see [Museum world](/en/guide/museum/):

- **Vanilla-block edition**: a world folder. Drop it into `saves/`; it needs only the four mods.
- **Deluxe edition**: a Modrinth modpack (`.mrpack`). Import it into Modrinth App or Prism and it downloads the decoration mods and shaders for you.

## FAQ

- **The robot just stands there.** That is the default. Right-click it with the T2 WALK Remote, or climb in and drive it with [MinePilot](/en/guide/driving/).
- **Low frame rate.** Every live robot keeps computing its physics and movement, which costs CPU. Catalogue exhibits run no physics and cost almost nothing.
