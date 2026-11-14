---
title: Physics tools (MujoCraft)
description: "Make block builds that really topple, then hit them with a hammer."
---

MujoCraft gives Minecraft a real physics engine. Besides making robots walk, it can turn any block build into a **rigid body**: one solid piece with real weight that can be pushed and knocked over.

## Assembly Wand

| Action | Effect |
|---|---|
| Left-click a block | corner A |
| Right-click a block | corner B (shows the outline and block count) |
| Sneak + right-click | turn the selection into one rigid body |

Mass follows the block volume (density 700 kg/m³, so about 700 kg per block). The body falls under gravity, collides with terrain and other bodies, and can be pushed by robots. In Survival the selection is limited to 512 blocks, and unbreakable blocks such as bedrock cannot be assembled.

Recipe: an amethyst shard and two copper ingots, placed diagonally.

## Physics Hammer

| Action | Effect |
|---|---|
| Left-click a body or a robot | shoves it from where you hit; off-centre hits spin and topple things |
| Fully charged swing | strongest hit |
| Sneak + hit | a light tap |
| Right-click / sneak + right-click | raise / lower the strength (five levels, ×0.25 to ×4) |

Heavy things move less: one hit makes a robot stagger and only rocks a house.

Recipe: three iron blocks on top; iron block, stick, iron block in the middle; a stick in the bottom centre.

## Commands

| Command | Effect |
|---|---|
| `/mujocraft assemble <from> <to>` | turn the blocks in a region into a rigid body |
| `/mujocraft impulse <x> <y> <z>` | shove the nearest body (bigger numbers push harder) |
| `/mujocraft list` | list bodies |
| `/mujocraft demo` | spawn a demo body next to you |

## Valkyrien Skies 2

MujoCraft also has a separate add-on for Minecraft 1.20.1 that lets our rigid bodies and VS2 ships collide with and push each other: a turntable flings blocks off, a crate knocks a sled away, and the hammer moves a ship. It is a standalone experimental build and does not install alongside the 1.21.1 mods.
