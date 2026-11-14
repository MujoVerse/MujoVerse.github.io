---
title: Bridge protocol reference
description: "MinePilot local bridge v1 — WebSocket + JSON, so clients can be written in any language."
---

The Python package is one implementation of this protocol; any language that speaks WebSocket and JSON can be a client. This page is a summary; the full specification (every field, error code and coordinate transform) is [`docs/bridge-protocol.md`](https://github.com/MujoVerse/MinePilot/blob/main/docs/bridge-protocol.md).

## Starting and authentication

```text
/minepilot bridge start [port]   # default 8765; 0 picks a free port; OP required
/minepilot bridge status
/minepilot bridge stop
```

- Off by default, including after a restart. Listens on `127.0.0.1` only; there is no remote access or TLS.
- On start it writes `<game dir>/minepilot/bridge.json`: `{"v":1,"host":"127.0.0.1","port":8765,"token":"..."}`, with mode 0600 on macOS/Linux.
- The first message must be `hello` with the token. The token works once and is rotated (and rewritten to the file) after a successful connection. Unauthenticated sockets are closed after 5 s.
- Handshakes with a browser `Origin` header are rejected, so web pages cannot reach the bridge. Messages are capped at 64 KiB; binary messages are rejected.

## Message format

Every message carries `"v": 1`. Requests have an `id` and a `type`; replies echo the `id`, and several requests may be in flight:

```json
{"v":1,"id":12,"type":"walk","robot":"<uuid>","vx":0.5,"vy":0,"yaw":0}
{"v":1,"id":12,"ok":true,"result":{"vx":0.5,"vy":0,"yaw":0,"expires_ms":500}}
{"v":1,"id":13,"ok":false,"error":{"code":"not_owner","message":"Claim this robot first"}}
```

Error codes: `auth`, `version`, `invalid_request`, `unknown_type`, `robot_unavailable`, `controlled`, `not_owner`, `unsupported`, `invalid_target`, `recovery_unavailable`, `name_conflict`, `io`.

## Requests

| Type | Fields | Notes |
|---|---|---|
| `hello` | `token` | must be the first message; returns session id, protocol 1, `command_timeout_ms: 500` |
| `robots.list` | — | every robot record, including saved but unloaded ones |
| `players.list` | — | online players' UUID, name, position, dimension |
| `claim` / `release` | `robot` | take / give back control; never displaces another controller |
| `name` | `robot, name` | 1–32 letters, digits, `_`, `-`; case-insensitive and unique |
| `walk` | `robot, vx, vy, yaw` | body-frame velocity; returns the clamped values and `expires_ms: 500` |
| `head` | `robot, yaw, pitch` | head direction, radians |
| `recover` | `robot` | ask a fallen robot to get up |
| `chase` | `robot, target: [x, y, z]` | walk to a flat-ground target within 48 blocks |
| `subscribe` | `robot, observation_hz (0–50), events, body_poses?` | observation rate, events (`recovery`, `fall`, `released`, `chat`), body-pose stream |
| `get_observation` | `robot` | one observation, no claim needed |
| `robot.model` | `robot` | MJCF asset, hashes, root body, body/joint names in MJCF order |

`walk`, `head`, `recover`, `chase` and `name` require a `claim` first. There are no joint-, torque- or root-pose commands; such requests return `unknown_type`.

## Control rules

- Players win: when a player takes over, the program receives a `released` event with reason `Player takeover`.
- WALK stops unless refreshed within 500 ms of wall-clock time; CHASE runs until it is within 0.25 m, is replaced, or is released.
- Disconnecting releases all control and stops the robots; the chunks loaded for a claim are kept for 5 minutes, then removed.
- A connection with more than 256 queued outgoing messages or 256 pending requests is closed.

## Coordinates

- `root_position` in observations is Minecraft world coordinates (Y up); at yaw 0 forward is +X and left is −Z.
- The body-pose stream uses the MuJoCo world frame (Z up) with WXYZ quaternions; Minecraft coordinates are `(x, z, −y)`.
