---
title: 机器人足球（MineArena）
description: "用 RoboCup 规则组织一场机器人比赛。"
---

MineArena 内置 RoboCup 人形组官方 **GameController 7.0**，开球、暂停、半场、加时、点球和判罚都走官方状态机。场上每台机器人都是真实的物理身体。

## 快速开始

1. 在一片空旷平地上执行 `/minearena match create 1`（1v1）或 `/minearena match create 5`（5v5）。球场用原版方块搭在你脚下。
2. 按 **M** 打开裁判台，依次点 READY → SET → PLAY。
3. 装了 [MinePilot](/guide/driving/) 的话，可以随时坐进场上任意一台机器人亲自踢；没人驾驶的机器人会自己带球。

## 常用命令

| 命令 | 作用 |
|---|---|
| `/minearena field [x y z]` | 只搭球场 |
| `/minearena demo [机器人] [x y z]` | 搭球场并开始一段演示：机器人从角落走到中场，把球带进对方球门 |
| `/minearena match create <1..5>` | 创建一场比赛 |
| `/minearena match ready\|set\|play` | 裁判动作 |
| `/minearena match status` | 比分、阶段、剩余时间 |
| `/minearena roster home 1 2789E8` | 设置队员号码和球衣颜色 |
| `/minearena match clear` | 清除比赛中的机器人和球，保留球场 |

判罚、换人、定位球等更多裁判动作见游戏内 `/minearena` 的补全提示。

## 冠军赛 3v3 展示赛

MineArena 可以搭一块成年组 14 × 9 米球场，让 Booster Champion 仿真赛的 3v3 策略代码在 Minecraft 里直接驱动 K1 与 T1。策略目录（`agent.toml`、`src/main.py` 等）不需要改动；MinePilot 的本机桥接充当机器人后端，提供同样的 `play(context, players, store)` 接口和 GameController 状态。

1. 安装四个模组，以及 ONNX Runtime 和 K1 机器人包（装上 T2、G1、T1 包会有更多机器人上场）。
2. 在服务器所在的电脑上准备 Python 包和示例策略：

   ```sh
   cd MinePilot/python
   python3 -m venv .venv
   .venv/bin/python -m pip install -e .
   .venv/bin/python -m minepilot champion example --output ./champion-example
   ```

3. 在游戏里搭场地并打开桥接：

   ```text
   /minearena showcase champion
   /minepilot bridge start
   ```

4. 运行策略，接管 A 队三台 K1：

   ```sh
   export MINEPILOT_BRIDGE=<游戏目录>/minepilot/bridge.json
   .venv/bin/python -m minepilot champion run --team 0 \
     --robots booster_k1,booster_k1,booster_k1 ./champion-example
   ```

B 队由内置 AI 驾驶，第三个位置留给玩家：走到 B3 旁边空手右键，或用 `/minepilot drive` 坐进去。不想亲自上场时，`/minearena match slot away 3 builtin` 把它也交给内置 AI。人和策略都到齐后自动开球。

几点说明：

- 示例策略（MIT，李奇）原样来自 `BoosterRobotics/sim-3v3-simple-framework`，固定在一个具体提交上并校验每个文件的哈希。
- `kick` 使用机器人安装的踢球技能（K1、T1 自带行进中踢球）；没有踢球技能的机器人用走路推球代替。
- 倒地超过 5 秒、又不能自己起身的机器人，由裁判按规则拾起，判罚后放回场边。
- 这是独立的兼容适配器，与 Booster Robotics 无隶属关系，也不代表官方仿真环境的结果。
