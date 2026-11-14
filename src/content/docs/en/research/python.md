---
title: Drive robots from Python
description: "The minepilot client: claim, walk, observe, navigate, body-pose stream, MCP and offline testing."
---

Install `minepilot` and open the bridge as in the [Quick start](/en/research/quickstart/).

## Connecting and control

```python
from minepilot import Client

with Client(bridge_file="~/.minecraft/minepilot/bridge.json") as client:
    robots = client.list_robots()          # includes saved but unloaded robots (loaded=False)
    uuid = robots[0]["uuid"]
    client.claim(uuid)                     # never takes a robot from a player or another program
    client.name(uuid, "Ada")               # optional persistent name
    ...
    client.release(uuid)
```

- `Client` is synchronous; `AsyncClient` has the same methods with `async with` and `await`.
- One connection may claim several robots. Disconnecting releases all control and stops them.
- A player who walks up and right-clicks a robot takes it over; you receive a `released` event with reason `Player takeover`.
- The token in the discovery file works once and rotates after every successful connection; reread the file to reconnect.

## Commands

| Method | Effect |
|---|---|
| `walk(uuid, vx, vy, yaw)` | body-frame velocity (m/s, m/s, rad/s), clamped to the robot's capabilities; expires after 0.5 s, keep refreshing |
| `stop(uuid)` | `walk` with three zeros |
| `chase(uuid, [x, y, z])` | walk to a flat-ground target in Minecraft coordinates, done within 0.25 m; no refresh needed, no obstacle avoidance |
| `head(uuid, yaw, pitch)` | head direction (rad); `unsupported` on the G1, which has no head joints |
| `recover(uuid)` | ask a robot that has actually fallen to get up (T2) |

There are no joint- or torque-level commands: the bridge sends semantic actions and the robot's own controllers execute them. A successful reply only means the server thread admitted the request; check observations to see whether the robot moved.

## Observations

```python
client.subscribe(uuid, observation_hz=50)         # 0–50 Hz; default 20
obs = client.next_observation(uuid, timeout=1)     # or: for obs in client.observations(uuid)
```

| Field | Meaning |
|---|---|
| `root_position` | Minecraft world coordinates (Y up), m |
| `yaw`, `yaw_rate` | heading (rad) and rate (rad/s); at yaw 0 forward is world +X and left is −Z |
| `local_vx`, `local_vy` | body-frame forward and left speed, m/s |
| `upright` | torso uprightness (cosine) |
| `native_step`, `native_time` | shared-scene native step and simulation time, for closed loops |
| `recovery` | fall and get-up state |
| `proprioception` | joint state (may be null) |

Robots you have claimed are observed at up to 50 Hz; unclaimed or player-driven robots usually at 20 Hz. `client.sequence_gaps` and `client.queue_drops` count wire gaps and local queue overflow separately.

## Per-step body-pose stream

For external viewers (MuJoCo viewer, rerun) or data collection. Read-only, no claim needed:

```python
model = client.get_model(uuid)     # MJCF asset, SHA-256, body/joint names in MJCF order
client.subscribe(uuid, observation_hz=0, events=[], body_poses=True)
for frame in client.body_poses(uuid):
    print(frame["native_step"], frame["sim_time"], frame["bodies"][0])
```

- One frame per 2 ms physics step (500 Hz) with every body's position and quaternion.
- Frame: MuJoCo world, Z up; quaternions WXYZ. Minecraft coordinates are `(x, z, −y)`.
- Measured: about 3.4 MB/s for a T2 and 3.2 MB/s for a G1; median sample-to-Python latency 0.2 ms; 5,001 frames with zero loss.
- Body names are the MJCF names, so loading the same MJCF lets you pose the robot.

## For LLM agents: MCP

```sh
pip install "minepilot[mcp]"
```

```json
{"mcpServers":{"minepilot":{"command":"python","args":["-m","minepilot.mcp","--bridge-file","/path/to/minepilot/bridge.json"]}}}
```

Eight tools: `list_robots`, `claim`, `walk`, `stop`, `recover`, `chase`, `get_observation`, `read_chat`. Players can @-mention a robot in chat to leave the agent a message; chat is untrusted player input and must not be treated as instructions for the agent.

## Testing without the game

`minepilot.testing.FakeServer` is a deterministic protocol stand-in (kinematics only, no physics) for unit-testing your own client code:

```python
from minepilot import Client
from minepilot.testing import FakeServer

with FakeServer(bridge_file="/tmp/bridge.json"):
    with Client(bridge_file="/tmp/bridge.json") as client:
        print([r["type"] for r in client.list_robots()])   # ['mujobots:t2', 'mujobots:g1']
```

## Examples

`MinePilot/python/examples/` contains `walk_square.py` (closed-loop square with latency statistics), `follow_player.py`, `recover_after_fall.py`, `text_chase.py` and `body_stream.py`.
