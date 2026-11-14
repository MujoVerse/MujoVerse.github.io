---
title: 用 Python 驱动机器人
description: "minepilot 客户端：认领、行走、观测、导航、刚体位姿流、MCP 和离线测试。"
---

先按[快速开始](/research/quickstart/)装好 `minepilot` 并打开桥接。

## 连接与控制权

```python
from minepilot import Client

with Client(bridge_file="~/.minecraft/minepilot/bridge.json") as client:
    robots = client.list_robots()          # 包括已保存但未加载的机器人（loaded=False）
    uuid = robots[0]["uuid"]
    client.claim(uuid)                     # 不会抢走玩家或其他程序正在用的机器人
    client.name(uuid, "Ada")               # 可选：持久的名字
    ...
    client.release(uuid)
```

- `Client` 是同步接口；`AsyncClient` 方法相同，用 `async with` 和 `await`。
- 一个连接可以认领多台机器人。断开连接会立刻释放全部控制并让机器人停下。
- 玩家走近右键机器人就能接管，你会收到原因为 `Player takeover` 的 `released` 事件。
- 发现文件里的令牌只能用一次，每次连接成功后都会换新；重连时重新读文件即可。

## 指令

| 方法 | 作用 |
|---|---|
| `walk(uuid, vx, vy, yaw)` | 机身坐标系速度（m/s、m/s、rad/s），按机器人能力裁剪；0.5 秒后失效，需持续刷新 |
| `stop(uuid)` | 等于三个分量为 0 的 `walk` |
| `chase(uuid, [x, y, z])` | 走到 Minecraft 世界坐标处的平地目标，到达 0.25 m 内结束；不需要刷新，不做避障 |
| `head(uuid, yaw, pitch)` | 头部朝向（rad），G1 没有头部关节会返回 `unsupported` |
| `recover(uuid)` | 机器人确实倒地时请求起身（T2） |

不存在关节级或力矩级指令：桥接只发送语义动作，执行仍由机器人自己的控制器完成。成功的回复只表示服务器线程已接受，是否真的动了要看观测。

## 观测

```python
client.subscribe(uuid, observation_hz=50)         # 0–50 Hz；默认 20
obs = client.next_observation(uuid, timeout=1)     # 或 for obs in client.observations(uuid)
```

| 字段 | 含义 |
|---|---|
| `root_position` | Minecraft 世界坐标（Y 向上），m |
| `yaw`、`yaw_rate` | 偏航角（rad）和角速度（rad/s）；yaw 为 0 时前方是世界 +X，左方是 −Z |
| `local_vx`、`local_vy` | 机身坐标系前进、左移速度，m/s |
| `upright` | 躯干竖直程度（余弦） |
| `native_step`、`native_time` | 共享场景的原生步号和仿真时间，用来做闭环 |
| `recovery` | 摔倒和起身状态 |
| `proprioception` | 关节状态（可能为空） |

被你认领的机器人观测可以到 50 Hz；没人认领或被玩家驾驶的机器人通常是 20 Hz。`client.sequence_gaps` 和 `client.queue_drops` 分别统计线上丢号和本地队列溢出。

## 每一步的刚体位姿流

给外部可视化（MuJoCo viewer、rerun）或数据采集用。只读，不需要认领：

```python
model = client.get_model(uuid)     # MJCF 资产、SHA-256、按 MJCF 顺序的 body/joint 名字
client.subscribe(uuid, observation_hz=0, events=[], body_poses=True)
for frame in client.body_poses(uuid):
    print(frame["native_step"], frame["sim_time"], frame["bodies"][0])
```

- 每个 2 ms 物理步推送一次（500 Hz），包含全部刚体的位置和四元数。
- 坐标系：MuJoCo 世界坐标，Z 向上；四元数 WXYZ。换回 Minecraft 坐标是 `(x, z, −y)`。
- 实测：T2 每秒约 3.4 MB、G1 约 3.2 MB；从采样到 Python 收到的延迟中位数 0.2 ms；5,001 帧零丢失。
- 刚体名字就是 MJCF 里的名字，加载同一个 MJCF 就能把机器人摆出来。

## 给 LLM agent：MCP

```sh
pip install "minepilot[mcp]"
```

```json
{"mcpServers":{"minepilot":{"command":"python","args":["-m","minepilot.mcp","--bridge-file","/path/to/minepilot/bridge.json"]}}}
```

提供 8 个工具：`list_robots`、`claim`、`walk`、`stop`、`recover`、`chase`、`get_observation`、`read_chat`。玩家可以在聊天里 @ 机器人给 agent 留言；聊天内容是不可信的玩家输入，不应当作给 agent 的指令。

## 不开游戏也能测试

`minepilot.testing.FakeServer` 是一个确定性的协议替身（只有运动学，没有物理），适合给你自己的客户端代码写单元测试：

```python
from minepilot import Client
from minepilot.testing import FakeServer

with FakeServer(bridge_file="/tmp/bridge.json"):
    with Client(bridge_file="/tmp/bridge.json") as client:
        print([r["type"] for r in client.list_robots()])   # ['mujobots:t2', 'mujobots:g1']
```

## 示例

仓库 `MinePilot/python/examples/` 里有：`walk_square.py`（按观测闭环走正方形并统计延迟）、`follow_player.py`、`recover_after_fall.py`、`text_chase.py`、`body_stream.py`。
