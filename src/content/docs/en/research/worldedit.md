---
title: A test course in five minutes with WorldEdit
description: "Build a walking course with rough ground, a gentle slope and a step using WorldEdit, walk a T2 over it and analyse the recording."
---

Minecraft blocks are 1 m cubes, so a slope built from whole blocks is a staircase of 1 m steps that no robot can climb. But MujoCraft builds terrain from each block's real collision boxes, so partial blocks give you fine-grained terrain:

| Block | Collision height | Use |
|---|---|---|
| carpet | 6.25 cm | small bumps, rough ground |
| snow (1–8 layers) | (layers − 1) × 12.5 cm | gentle slopes, steps; one layer has no collision |
| slab | 50 cm | high steps, kerbs |

The course below takes fewer than 20 [WorldEdit](https://modrinth.com/mod/worldedit) 7.3 (Fabric 1.21.1) commands and was tested in a real client.

![The course: carpet rough patch, snow slope, 25 cm step](/media/test-course.webp)

## 1. Setup

- Install WorldEdit in addition to the mods from the [Quick start](/en/research/quickstart/).
- Create a **superflat** world with cheats enabled. Superflat ground is at y = −61 and robots stand at y = −60; if your ground differs, shift every y below.

## 2. Build the course

Type these into chat one by one (WorldEdit commands start with `//`):

```text
//pos1 -2,-61,-5
//pos2 64,-61,5
//set smooth_stone

//pos1 -2,-60,-5
//pos2 64,-50,5
//set air

//pos1 8,-60,-5
//pos2 15,-60,5
//set 35%white_carpet,65%air

//pos1 26,-60,-5
//pos2 32,-60,5
//set smooth_stone
//pos1 18,-61,-5
//pos2 40,-58,5
//snowsmooth 12

//pos1 50,-60,-5
//pos2 64,-60,5
//set snow[layers=3]
//desel
```

In order:

1. a 67 × 11 m smooth-stone strip with clear air above;
2. **x 8–15**: 35% random carpet, 6.25 cm bumps;
3. **x 18–40**: a 1 m plateau, then `//snowsmooth` turns its surroundings into snow-layer slopes rising at most 12.5 cm per block;
4. **from x 50**: a 25 cm snow step (3 layers).

## 3. Walk a T2 across and record it

```text
/mujobots spawn 1 -60 0
/mujobots record start
/mujobots walk 0.6 0 0
```

About 100 seconds later:

```text
/mujobots record stop
```

Or drive it from the [Python client](/en/research/python/) with your own speed profile or controller.

## 4. Analyse

```python
import sys
import numpy as np
from minepilot.recording import load_recording

r = load_recording(sys.argv[1])
t = r.time[:, 0] - r.time[0, 0]
x, height = r.root_pose[:, 0], r.root_pose[:, 2]        # MuJoCo world: x = MC x, z = MC y
w, qx, qy, qz = r.root_pose[:, 3:].T
upright = 1 - 2 * (qx**2 + qy**2)                        # cosine between torso axis and vertical
for i in range(0, len(t), 250):
    print(f"t={t[i]:5.1f}s  x={x[i]:6.2f}  height={height[i]:7.3f}  upright={upright[i]:4.2f}")
if (upright < 0.5).any():
    i = int(np.argmax(upright < 0.5))
    print(f"fell at t={t[i]:.2f}s, x={x[i]:.2f}")
```

```sh
python analyze.py <world>/mujobots/recordings/t2-....npz
```

What we measured (T2's stock WALK controller at 0.6 m/s):

| Section | Result |
|---|---|
| carpet rough patch | passed, uprightness stayed at 1.00 |
| snow slope (about 0.5 m up and down) | passed, lowest uprightness 0.93 |
| 25 cm step | fell at x ≈ 51.2 (t = 58 s) |

![T2 fallen at the 25 cm step](/media/test-course-fall.webp)

T2's walking policy was trained on flat ground, so failing a 25 cm step is expected. Swap the controller, change the step height (`snow[layers=2]` is 12.5 cm), or turn on `/gamerule mujobotsAutoGetUp true` so it stands back up, and the course becomes a repeatable comparison.

## Tips

- `//undo` reverts the last edit; `//set 20%stone_slab,80%air` scatters 50 cm obstacles.
- More `//snowsmooth` iterations give gentler slopes; rough out heights with blocks first, then smooth.
- After terrain edits the physics scene rebuilds automatically; no need to respawn the robot.
