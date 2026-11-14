---
title: Robots
description: "Five live physical robots: Booster T2, K1 and T1, Unitree G1 and Go1."
---

MujoBots has two kinds of robots:

- **Live physical robots**: Booster T2, K1 and T1, Unitree G1 and Go1. Every joint is driven by motor torque and every step is chosen by the robot's own learned policy, so they can be pushed over and they can trip.
- **Exhibits**: the 33 robots in the catalogue. They replay precomputed motion and run no physics; see [Robot catalogue](/en/guide/exhibits/).

Each live robot lives in its own robot pack: install a pack to get that robot.

| Robot | Walking | Gets up | Ball |
|---|---|---|---|
| Booster T2 | learned WALK policy | yes | pushes the ball by walking |
| Unitree G1 | SONIC tracking reference motion | no | dribble motion |
| Booster K1 | B-Human 2026 code-release networks | no | in-walk kick |
| Booster T1 | B-Human 2026 code-release networks | no | in-walk kick |
| Unitree Go1 | MuJoCo Playground joystick policy | no | — |

## Spawning

In creative mode, the **MujoBots** tab has a **Robot Capsule** for every installed robot. Use it on the ground and the robot appears there, facing you.

## Making it walk

| Action | Effect |
|---|---|
| Right-click a robot with the **Robot Remote** | walk slowly forward; right-click again to stop |
| Sneak + right-click | stop and stand |
| Take the driver's seat with [MinePilot](/en/guide/driving/) | drive it freely, like a mech |
| Hand it to a program or an AI | use MinePilot's localhost bridge, Python package or MCP server |

The remote sends a velocity command; the actual motion comes from the robot's own policy, joint torques and physical contacts.

## Falling and getting up

When T2 is knocked down or falls from a height it can stand up by itself:

- right-click the fallen T2 with the remote;
- or run `/mujobots getup`;
- or enable `/gamerule mujobotsAutoGetUp true` and fallen T2s get up automatically.

The other robots don't get up by themselves. In [MineArena football](/en/guide/football/) the referee picks up a robot that has been down for more than 5 seconds, puts it back at the sideline, and play continues.

## Commands (operator permission)

| Command | Effect |
|---|---|
| `/mujobots spawn <robot> [x y z] [yaw]` | spawn a robot, e.g. `booster_k1` |
| `/mujobots robots [category]` | list installed robots |
| `/mujobots list [targets]` | list robots in the world and their state |
| `/mujobots walk [targets] <forward> <left> <turn>` | velocity command (m/s, m/s, rad/s) |
| `/mujobots stop [targets]` | stop |
| `/mujobots getup [targets]` | make a fallen robot that can recover get up |

`targets` is an ordinary entity selector; without it the command applies to the nearest live robot within 64 m. Velocities are limited to the range each robot pack declares.
