---
title: Robot football (MineArena)
description: "Run a robot match under RoboCup rules."
---

MineArena embeds the official RoboCup Humanoid League **GameController 7.0**: kick-off, pauses, halves, extra time, penalty shoot-outs and penalties all run on the official state machine. Every robot on the pitch is a real physical body.

## Quick start

1. On open flat ground, run `/minearena match create 1` (1v1) or `/minearena match create 5` (5v5). The pitch is built from vanilla blocks under your feet.
2. Press **M** to open the referee console and click READY → SET → PLAY.
3. With [MinePilot](/en/guide/driving/) installed you can climb into any robot on the pitch and play yourself; robots nobody drives dribble on their own.

## Common commands

| Command | Effect |
|---|---|
| `/minearena field [x y z]` | build the pitch only |
| `/minearena demo [robot] [x y z]` | build the pitch and run a demo: a robot walks from the corner to midfield and dribbles into the far goal |
| `/minearena match create <1..5>` | create a match |
| `/minearena match ready\|set\|play` | referee actions |
| `/minearena match status` | score, phase, remaining time |
| `/minearena roster home 1 2789E8` | set a player's number and shirt colour |
| `/minearena match clear` | remove the match robots and ball, keep the pitch |

Penalties, substitutions, set plays and other referee actions are listed by tab completion under `/minearena match`.

## Champion 3v3 showcase

MineArena can stage an adult 14 × 9 m pitch where Booster Champion simulation 3v3 strategy code drives K1 and T1 inside Minecraft. The strategy directory (`agent.toml`, `src/main.py` and so on) stays unchanged; MinePilot's localhost bridge acts as the robot backend and provides the same `play(context, players, store)` interface and GameController state.

1. Install the four mods plus the ONNX Runtime and K1 robot packs (the T2, G1 and T1 packs put more robots on the pitch).
2. On the machine that runs the server, prepare the Python package and the example strategy:

   ```sh
   cd MinePilot/python
   python3 -m venv .venv
   .venv/bin/python -m pip install -e .
   .venv/bin/python -m minepilot champion example --output ./champion-example
   ```

3. In game, build the pitch and open the bridge:

   ```text
   /minearena showcase champion
   /minepilot bridge start
   ```

4. Run the strategy for team A's three K1s:

   ```sh
   export MINEPILOT_BRIDGE=<game directory>/minepilot/bridge.json
   .venv/bin/python -m minepilot champion run --team 0 \
     --robots booster_k1,booster_k1,booster_k1 ./champion-example
   ```

Team B is driven by the builtin AI, with the third seat reserved for a player: walk up to B3 and right-click it with an empty hand, or use `/minepilot drive`. To stay off the pitch, `/minearena match slot away 3 builtin` hands it to the builtin AI too. Kick-off starts once everyone is present.

Notes:

- The example strategy (MIT, 李奇) comes unchanged from `BoosterRobotics/sim-3v3-simple-framework`, pinned to one commit with every file hash checked.
- `kick` uses the robot's installed ball skill (K1 and T1 ship an in-walk kick); robots without one push the ball by walking.
- A robot that has been down for more than 5 seconds and can't get up by itself is picked up by the referee and returned to the sideline after the penalty.
- This is an independent compatibility adapter, not affiliated with Booster Robotics, and its results don't stand for the official simulator's.
