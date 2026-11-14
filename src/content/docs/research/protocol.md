---
title: 桥接协议参考
description: "MinePilot 本机桥接 v1：WebSocket + JSON，可以用任何语言写客户端。"
---

Python 包只是这个协议的一个实现。任何能连 WebSocket、收发 JSON 的语言都可以直接写客户端。本页是摘要，完整规范（含所有字段、错误码和坐标换算）见 [`docs/bridge-protocol.md`](https://github.com/MujoVerse/MinePilot/blob/main/docs/bridge-protocol.md)。

## 启动与鉴权

```text
/minepilot bridge start [port]   # 默认 8765；0 表示随机端口；需要 OP 权限
/minepilot bridge status
/minepilot bridge stop
```

- 默认关闭，重启世界后也是关闭的。只监听 `127.0.0.1`，没有远程访问和 TLS。
- 启动后写入 `<游戏目录>/minepilot/bridge.json`：`{"v":1,"host":"127.0.0.1","port":8765,"token":"..."}`。macOS/Linux 上文件权限是 0600。
- 第一条消息必须是 `hello` 并带上令牌。令牌只能用一次，连接成功后立刻换新并写回文件。5 秒内不鉴权会被断开。
- 带浏览器 `Origin` 头的握手一律拒绝，网页无法连上桥接。单条消息上限 64 KiB，不接受二进制消息。

## 消息格式

每条消息都带 `"v": 1`。请求带 `id` 和 `type`，回复带同一个 `id`，可以同时有多个请求在途：

```json
{"v":1,"id":12,"type":"walk","robot":"<uuid>","vx":0.5,"vy":0,"yaw":0}
{"v":1,"id":12,"ok":true,"result":{"vx":0.5,"vy":0,"yaw":0,"expires_ms":500}}
{"v":1,"id":13,"ok":false,"error":{"code":"not_owner","message":"Claim this robot first"}}
```

错误码：`auth`、`version`、`invalid_request`、`unknown_type`、`robot_unavailable`、`controlled`、`not_owner`、`unsupported`、`invalid_target`、`recovery_unavailable`、`name_conflict`、`io`。

## 请求

| 类型 | 字段 | 说明 |
|---|---|---|
| `hello` | `token` | 必须是第一条消息；返回会话号、协议版本 1、`command_timeout_ms: 500` |
| `robots.list` | — | 所有机器人记录，含已保存但未加载的 |
| `players.list` | — | 在线玩家的 UUID、名字、位置、维度 |
| `claim` / `release` | `robot` | 认领 / 释放控制；不会抢走他人的控制 |
| `name` | `robot, name` | 1–32 个字母、数字、`_`、`-`，不区分大小写、全局唯一 |
| `walk` | `robot, vx, vy, yaw` | 机身坐标系速度，返回裁剪后的值和 `expires_ms: 500` |
| `head` | `robot, yaw, pitch` | 头部朝向，弧度 |
| `recover` | `robot` | 倒地后请求起身 |
| `chase` | `robot, target: [x, y, z]` | 走到 48 格内的平地目标 |
| `subscribe` | `robot, observation_hz (0–50), events, body_poses?` | 观测频率、事件（`recovery`、`fall`、`released`、`chat`）、刚体位姿流 |
| `get_observation` | `robot` | 单次观测，不需要认领 |
| `robot.model` | `robot` | MJCF 资产、哈希、根刚体、按 MJCF 顺序的 body/joint 名字 |

`walk`、`head`、`recover`、`chase`、`name` 需要先 `claim`。没有关节级、力矩级或根位姿指令，发送这类请求会返回 `unknown_type`。

## 控制规则

- 玩家优先：玩家接管时，程序收到原因为 `Player takeover` 的 `released` 事件。
- WALK 在 500 ms（墙钟时间）内不刷新就停止；CHASE 一直执行到到达 0.25 m 内、被新指令替换或释放。
- 断开连接立即释放全部控制并让机器人停下；认领时加载的区块保留 5 分钟后移除。
- 一个连接排队超过 256 条待发消息或 256 个待处理请求会被断开。

## 坐标

- 观测里的 `root_position` 是 Minecraft 世界坐标（Y 向上）；yaw 为 0 时前方是 +X，左方是 −Z。
- 刚体位姿流使用 MuJoCo 世界坐标（Z 向上），四元数 WXYZ；Minecraft 坐标为 `(x, z, −y)`。
