---
title: Quick start
description: "From pip install to walking a physical humanoid from Python."
---

MujoVerse runs a shared MuJoCo scene inside Minecraft: Booster T2 and Unitree G1 run their original controllers at a 2 ms physics step and 50 Hz policy rate, and 33 robots from MuJoCo Menagerie and other sources are available as exhibits. Python drives them over a local WebSocket bridge, reading observations and every body pose at every step. Runs on macOS (Apple silicon), Linux x64 and Windows x64.

## 1. Install the Python package

```sh
pip install minepilot            # driving and observation; depends only on websockets
pip install "minepilot[numpy]"   # plus reading recordings
pip install "minepilot[mcp]"     # plus an MCP server for LLM agents
```

Python 3.10 or newer.

## 2. Start the simulation

The first release still needs a Minecraft instance with the mods, either:

- **With a window:** Minecraft Java 1.21.1 + Fabric Loader + Fabric API, plus the MujoCraft, MujoBots and MinePilot mods (see [Install](/en/guide/install/)). Create a world with cheats enabled.
- **Headless:** a Fabric 1.21.1 dedicated server with the same mods. Type the commands below into the server console; no game client or online player is needed.

Then run:

```text
/mujobots spawn t2         # spawn a T2 (or g1, booster_k1, booster_t1, unitree_go1)
/minepilot bridge start    # open the bridge, listening on 127.0.0.1 only
```

The bridge writes its port and a one-time token to `<game dir>/minepilot/bridge.json` (`.minecraft` for single player, the server folder for a server).

## 3. Make it walk

```python
import sys
import time
from minepilot import Client

bridge_file = sys.argv[1] if len(sys.argv) > 1 else "minepilot/bridge.json"
with Client(bridge_file=bridge_file) as client:
    robot = next(r for r in client.list_robots() if r["loaded"] and r["controlled_by"] == "none")
    uuid = robot["uuid"]
    client.claim(uuid)
    client.subscribe(uuid, observation_hz=50)
    start = time.monotonic()
    while time.monotonic() - start < 3:           # walk for 3 seconds
        client.walk(uuid, vx=0.5)                 # each WALK lasts 0.5 s: keep refreshing
        obs = client.next_observation(uuid, timeout=1)
    print(robot["type"], "moved to", obs["root_position"], "at native step", obs["native_step"])
    client.stop(uuid)
    client.release(uuid)
```

```sh
python walk_forward.py ~/.minecraft/minepilot/bridge.json
```

Each WALK command expires after 0.5 s, so the script keeps refreshing it; disconnecting releases control and stops the robot immediately. A nearby player can take the robot over at any time, and you then receive a `released` event.

## Next

- [Drive robots from Python](/en/research/python/): observations, navigation, async client, body-pose stream, MCP.
- [Record a gait](/en/research/recording/): export NPZ and verify it independently.
- [Bridge protocol reference](/en/research/protocol/): clients in other languages.
