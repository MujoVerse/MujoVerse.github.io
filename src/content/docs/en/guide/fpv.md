---
title: FPV Quadrotor
description: Manual flight and flight cameras in MujoBots and MinePilot.
---

This is a **development feature for Minecraft Java 1.21.1 / Fabric**. Manual flight requires Fabric API, MujoCraft, MujoBots core with the quadrotor, and MinePilot with flight support. No humanoid or quadruped pack is needed. The web museum demo does not run this feature.

<video controls muted playsinline preload="none" poster="/media/fpv-flight.webp" src="/media/fpv-flight.mp4"></video>

## Fly

Get the **FPV Quadrotor Kit** from the creative inventory (`/give @s mujobots:drone_kit`) and right-click level ground to deploy it. Look at the quadrotor and press `R` or right-click to take control.

| Input | Action |
| --- | --- |
| `Space` / `Shift` | Climb / descend in Assisted; increase / decrease throttle in Acro |
| `W A S D` | Translate in Assisted; control pitch and roll rates in Acro |
| `←` / `→` | Yaw |
| `V` | Ground view → FPV → stabilized view |
| `↑` / `↓` | Adjust camera pitch |
| `B` | Switch between Assisted and Acro after takeoff, independently of the camera |
| `K` / `G` | Auto-land / leave and initiate landing |

The pilot stays on the ground. Remote control is limited to 48 metres and to tracked chunks. Acro does not self-level when you release the keys. Losing focus or leaving range attempts a landing in place, not a return to home.

## Capture and Scope

The clip is an in-game automated single-player run: the quadrotor passes through the cyan gate, banks, then switches to the stabilized camera. It climbs **3.69 metres** and reaches **39.8°** of FPV bank. The model is a generic quadrotor, not calibrated against a real airframe. This capture is not a multiplayer or human-pilot acceptance test.
