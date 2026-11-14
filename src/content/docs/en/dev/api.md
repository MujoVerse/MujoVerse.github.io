---
title: Mod developer API
description: "Control robots, read physical state, or plug in a new physics backend from your own mod."
---

The Java API is for other Fabric mods in the same JVM. External programs should use the [local bridge](/en/research/protocol/).

## Controlling robots: `dev.mujobots.api`

Both T2 and G1 implement `ControllableRobot`. Check capabilities, not entity classes:

| Type | Purpose |
|---|---|
| `ControllableRobot` | capabilities, current control source, claim/release, recovery request, latest observation |
| `RobotCapabilities` | speed and head ranges, whether shooting is available |
| `RobotControlSource` | your callbacks: `beforeStep(context)` before each native control step, `controlsApplied`, `afterTick(observation)`, release notice |
| `RobotControlContext` | one control step's observation plus four semantic actions: `walk`, `head`, `shoot`, `recover` |
| `RobotObservation` | UUID, root position, yaw and yaw rate, body-frame velocity, uprightness, native step and time, head angles, recovery state |
| `RobotAppearance` (optional) | body colour and shirt number (T2) |
| `RefereeResettable` (optional) | referee placement (T2) |
| `PhysicalRobot` (optional, unstable) | native body view: step counts, uprightness, body indices, foot bodies, render samples |

Rules:

- A successful `claimControl(source)` zeroes any previous WALK/SHOOT request; a second source cannot take over an existing claim.
- Control is semantic only: no root-pose writes, torque arrays or native handles.
- Recovery has top priority; WALK/SHOOT cannot override its torques while it runs.
- Every callback runs on the server thread for the current native step. Sources and player identities are never saved.

| | T2 | G1 |
|---|---|---|
| Forward / lateral / yaw | −1.5…3 m/s, ±1 m/s, ±2 rad/s | 0…1.5 m/s, lateral only with matching references, ±1 rad/s |
| Head | yaw ±1.134 rad, pitch −0.349…0.436 rad | none |
| Get-up | yes | no (`requestRecovery()` returns false) |

## Physics: `dev.mujocraft`

- **`PhysicsBackend`**: an engine-neutral physics interface. Bodies, joints, actuators and sensors are addressed by name; SI units, Z up, WXYZ quaternions; `jointLayout(names)` gives each joint's qpos/qvel width and offset, so never assume MuJoCo's layout. MuJoCo is the only implementation and the default.
- **Capability flags**: `CONTACT_WRENCH`, `CONTACT_WRENCH_BETWEEN`, `EXTERNAL_WRENCH`, `IMPULSE`, `IMPULSE_AT`. Unsupported capabilities throw `UnsupportedOperationException`; another engine is never substituted silently.
- **Snapshots**: opaque bytes tagged with backend id and model version; restoring into another backend or model is refused. A world picks its backend at creation, and saves never migrate across backends.
- **`PhysicsWorld.addStepListener`**: called once per 2 ms native step before integration (server thread) with the step index and simulation time. MinePilot's 500 Hz body-pose stream is built on it.
- **`PhysicsParticipant`**: lets your entity join the shared scene and take part in contacts with robots, rigid structures and terrain.
- **`Impulsable`**: lets the Physics Hammer hit your entity.

Full details: `docs/robot-control-api.md` in MujoBots and `docs/backend.md` in MujoCraft.
