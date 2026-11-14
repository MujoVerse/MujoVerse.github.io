---
title: Robot catalogue
description: "33 robot exhibits, pedestals and info cards."
---

The catalogue holds 33 robots built from public models: humanoids, quadrupeds, bipeds, arms, dexterous hands, mobile manipulators and drones. Each one ships with its upstream licence.

## Placing exhibits

Open the **MujoBots** creative tab; every robot is a **Robot Capsule** (live robots first, then exhibits by category). Right-click the ground with one and the robot stands there, facing you.

| Action | Effect |
|---|---|
| Right-click an exhibit | next motion (poses, dances, joint sweeps, …) |
| Sneak + right-click | pause / resume |
| Look at an exhibit | an info card appears top right: name, maker, year, number of joints, height, model licence |
| Left-click in Creative | remove it |

Exhibits only replay precomputed motion and run no physics, so dozens of them barely affect performance.

## Robot Pedestal

The **Robot Pedestal** is a craftable block: three smooth stone slabs / iron ingot, redstone, iron ingot / three polished deepslate, making two.

Give a pedestal a redstone signal (button, lever, pressure plate) and every robot standing on that group of **connected** pedestals restarts its motion together. Use it to make a row of robots perform in sync.

## Commands

| Command | Effect |
|---|---|
| `/mujobots robots [category]` | list every robot (click to spawn) |
| `/mujobots spawn <robot> [x y z] [yaw]` | spawn one |
| `/mujobots exhibit gallery [category]` | lay out all of them (or one category) |
| `/mujobots exhibit play\|pause\|restart\|next\|remove [targets]` | control the nearest exhibit, or the selected ones |
| `/mujobots exhibit speed <factor> [targets]` | playback speed |
| `/mujobots exhibit clip <motion> <targets>` | pick a motion |

`[targets]` accepts entity selectors such as `@e[type=mujobots:exhibit,distance=..8]`, so all of this works from command blocks.
