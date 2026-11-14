---
title: Verification evidence
description: "The tests, numbers and raw evidence behind every capability claim."
---

This page lists the capabilities MujoVerse claims and the tests and measurements behind them. Raw logs, screenshots and large files are in the Hugging Face dataset [MujoVerse/mujobots-evidence](https://huggingface.co/datasets/MujoVerse/mujobots-evidence); each repository's `docs/evidence/` folder holds the small files and their descriptions.

Unless noted, numbers come from a real Minecraft server (GameTest) or a real client on macOS arm64, not from a standalone MuJoCo script.

## Controllers match their reference implementations

| Claim | Evidence |
|---|---|
| The T2 WALK network in the JVM matches the original TorchScript | `PolicyParityTest`: element-wise error ≤ 3×10⁻⁵ |
| The T2 WALK controller (observation history, startup, joint targets) matches the team's Arena runtime | same test: 80 full control frames, target error ≤ 3×10⁻⁵ per element |
| 50 Hz policy, 500 Hz torque PD | real server: exactly 450 inferences over 4,500 physics substeps |
| Deterministic state across saves | native and controller state round-trip exactly; after quit and reload the same UUID keeps walking |

## Locomotion and recovery

| Claim | Evidence |
|---|---|
| T2 walks on Minecraft terrain | GameTest 2.44 m forward; real client 2.90 m, then 3.46 m more after reloading the save, upright cosine always > 0.998 |
| T2 gets up by itself after a fall | original supine and prone get-up networks (164 observations, 31 actions); `RecoveryParityTest` matches the original Python runtime numerically; `RecoveryNativeTest` starts supine and prone and stands up using only native contacts and motor torques (no root writes after setup), then walks away |
| Closed-loop driving from Python | headless server, T2 and G1 each walk a 1.5 m square: 4/4 waypoints, about 0.21 m from the start on return |

## Data interfaces

| Claim | Evidence |
|---|---|
| Recordings are faithful to native state | `check-recording.py` replays every frame through forward kinematics in an independent MuJoCo model: T2 10 s (500 frames), G1 30 s (1500 frames), maximum body position error 0 m |
| The body-pose stream is complete and fast | 5,001 frames per robot at 500 Hz: zero drops and zero sequence gaps; median sample-to-Python latency about 0.2 ms, P99 about 0.5 ms; about 3.4 MB/s (T2) |
| The bridge works on a real dedicated server | Fabric 1.21.1 dedicated server, no players online: `/minepilot bridge start` in the console, `bridge.json` mode 0600, a Python client walked a T2 about 1.5 m at uprightness 0.997, clean shutdown |
| The bridge is local only | GameTests cover authentication, OP permission, port fallback, browser Origin rejection, command expiry, player takeover and release on disconnect |

## Performance

`MujoBots/scripts/benchmark-physics.sh` measures the physics and control time inside one server tick on macOS arm64 (Apple silicon): 25 native 2 ms steps per tick including T2 WALK control, excluding Minecraft itself, terrain capture and scene rebuilds. Minecraft's whole tick budget is 50 ms.

| Live T2s | Rigid structures | Mean ms / tick | P95 |
|---:|---:|---:|---:|
| 1 | 0 | 3.3 | 3.7 |
| 5 | 0 | 17.4 | 19.6 |
| 10 | 0 | 34.2 | 37.9 |
| 0 | 10 | 0.9 | 0.9 |
| 0 | 100 | 8.8 | 8.9 |

Cost grows linearly with the number of robots; about ten live T2s use two thirds of the tick budget.

## Licence checks on released files

Every released jar is checked at build time: each file has a licence entry and provenance record, restricted files are blocked by a hash list, and the inference runtime carries natives for all three platforms.

## Not yet verified

- Walking on stairs, slopes and other general terrain;
- the robot limit within a full Minecraft tick (terrain and scene rebuilds included), and performance on Windows and Linux;
- the bridge end to end on Linux and Windows (the mods themselves were tested on all three platforms);
- G1 getting up by itself (it has no get-up controller yet).
