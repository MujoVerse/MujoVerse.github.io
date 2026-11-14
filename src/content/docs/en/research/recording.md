---
title: Record a gait
description: "Export a T2 or G1 trajectory from Minecraft as NPZ, load it with NumPy and verify it independently."
---

MujoBots records a robot's motion in the Minecraft scene at its control rate (50 Hz for both WALK and SONIC, 2 ms physics step) and exports NumPy `.npz` plus a `.meta.json`. Recording only observes: it never takes control and uploads nothing.

## 1. Record

In a world with cheats enabled:

```text
/mujobots spawn t2                    # or another robot id, e.g. g1
/mujobots record start                # nearest live robot within 64 m
/mujobots walk 0.35 0 0               # walk for a few seconds
/mujobots record stop
/mujobots record list                 # active recordings and exports awaiting retry
```

`start` / `stop` also take entity selectors or UUIDs, so several robots can be recorded at once: `/mujobots record start @e[type=mujobots:g1]`.

Files go into the world save:

```text
<world>/mujobots/recordings/t2-<uuid8>-<UTC time>.npz
<world>/mujobots/recordings/t2-<uuid8>-<UTC time>.meta.json
```

Each robot records at most 30,000 frames, 600 simulated seconds or about 128 MiB, whichever comes first. `stop`, entity unload and server shutdown all export automatically.

## 2. Load in Python

```sh
pip install "minepilot[numpy]"
```

```python
import numpy as np
from minepilot.recording import load_recording

r = load_recording("t2-01234567-20261110-120000.npz")
t = r.time[:, 0] - r.time[0, 0]               # seconds
print(r.meta["source"], r.meta["reference"])   # "sim"; clip info when a G1 tracks a reference
print(r.joint_names[:5], r.qpos.shape)         # joints sorted by name bytes
travel = r.root_pose[-1, :3] - r.root_pose[0, :3]
feet = r.foot_wrench.reshape(len(r), len(r.foot_names), 6)
print(travel, feet[:, :, 2].mean(axis=0))      # distance travelled, mean normal force per foot (N)
```

## 3. What is inside

| Array | Shape | Meaning |
|---|---|---|
| `time`, `native_step` | N × 1 | scene simulation time (s) and native step |
| `root_pose` | N × 7 | root body position (m) and quaternion (WXYZ) |
| `qpos`, `qvel` | N × J | joint angles (rad) and velocities (rad/s), in `joint_names` order |
| `action`, `action_valid` | N × J, N × 1 | policy network output aligned to joint order, and whether it is valid |
| `walk_command` | N × 3 | requested forward and left speed (m/s), yaw rate (rad/s) |
| `foot_wrench` | N × 6F | force (N) and torque (N·m) on each foot from static terrain |
| `body_pose` | N × 7B | pose of every body, in `body_names` order |
| `reference_id`, `reference_frame` | N × 1 | tracked reference clip and frame (−1 if none) |

Frame: absolute MuJoCo world coordinates, right-handed, Z up, identical to the [body-pose stream](/en/research/python/); Minecraft coordinates are `(x, z, −y)`. Positions do not jump when the scene is rebuilt (a GameTest checks this). `model_path` in `meta.json` is relative to the mod's asset root, so it never exposes your home directory. `meta.json` also carries `format_version` (currently 2), `source` (always `sim` for now; `real` is reserved for future hardware logs), the model file's SHA-256 and a written description of every convention.

Joints and bodies are sorted by the **UTF-8 bytes of their names**, and the name lists are stored in the file, so simulated data and future real-robot logs line up by name.

## 4. Verify independently

`check-recording.py` writes the root pose and joint angles of every frame into an independent MuJoCo model, runs forward kinematics and compares every recorded body pose:

```sh
python -I scripts/check-recording.py t2-...npz --output check.json
```

Measured before release: a 10 s T2 walk (500 frames) and a 30 s G1 walk (1500 frames) both have a maximum body position error of 0 m. This verifies export fidelity, not dynamics replay.

## 5. Towards a LeRobot dataset

The exporter is not built yet; the fields map like this: one file is one episode; `observation.state` is `qpos` (optionally with `qvel`, root pose and contact forces); `action` is `walk_command` (semantic-command dataset) or `action` where `action_valid=1` (policy-output dataset); `timestamp` is `time - time[0]`. Policy network outputs are not joint targets, so do not relabel them as radians. Full details are in `docs/recording.md` in the MujoBots repository.
