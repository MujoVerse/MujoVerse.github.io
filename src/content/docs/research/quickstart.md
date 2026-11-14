---
title: 快速开始
description: "从 pip install 到用 Python 让一台物理人形机器人走起来。"
---

MujoVerse 是一个跑在 Minecraft 里的 MuJoCo 共享场景：Booster T2 和宇树 G1 用原版控制器在 2 ms 物理步长、50 Hz 策略频率下运行，33 款 MuJoCo Menagerie 等来源的机器人可作展示。Python 通过本机 WebSocket 桥接驱动它们，读取观测和每一步的全部刚体位姿。macOS（Apple 芯片）、Linux x64、Windows x64 都可以运行。

## 1. 安装 Python 包

```sh
pip install minepilot            # 驱动和观测；只依赖 websockets
pip install "minepilot[numpy]"   # 另外读取录制文件
pip install "minepilot[mcp]"     # 另外给 LLM agent 用的 MCP 服务器
```

需要 Python 3.10 或更新。

## 2. 启动仿真

首发版本仍需要一个装好模组的 Minecraft 实例，二选一：

- **有界面：** Minecraft Java 1.21.1 + Fabric Loader + Fabric API，加上 MujoCraft、MujoBots、MinePilot 三个模组（见[安装](/guide/install/)）。新建一个开启作弊的世界。
- **无界面：** Fabric 1.21.1 专用服务器，装同样的模组。下面的命令直接在服务器控制台输入，不需要游戏客户端，也不需要有玩家在线。

然后执行：

```text
/mujobots spawn t2         # 生成一台 T2（也可以是 g1、booster_k1、booster_t1、unitree_go1）
/minepilot bridge start    # 打开桥接，只监听 127.0.0.1
```

桥接会把端口和一次性令牌写进 `<游戏目录>/minepilot/bridge.json`（单人游戏是 `.minecraft`，服务器是服务器目录）。

## 3. 让它走

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

每条 WALK 指令 0.5 秒后失效，所以脚本要持续刷新；断开连接会立即释放控制并让机器人停下。附近的玩家随时可以接管机器人，这时你会收到 `released` 事件。

## 下一步

- [用 Python 驱动机器人](/research/python/)：观测、导航、异步客户端、刚体位姿流、MCP。
- [录制一段步态](/research/recording/)：导出 NPZ 并独立校验。
- [桥接协议参考](/research/protocol/)：其他语言的客户端。
