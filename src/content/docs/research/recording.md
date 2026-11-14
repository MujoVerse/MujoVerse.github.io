---
title: 录制一段步态
description: "把 T2 或 G1 在 Minecraft 里的运动导出成 NPZ，用 NumPy 读取并独立校验。"
---

MujoBots 可以把机器人在 MC 场景里的运动按控制频率（WALK 和 SONIC 都是 50 Hz，物理步长 2 ms）完整录下来，导出为 NumPy 的 `.npz` 加一份 `.meta.json`。录制只旁观，不接管控制，也不会上传任何东西。

## 1. 录制

在有作弊权限的世界里：

```text
/mujobots spawn t2                    # 或其他机器人 id，例如 g1
/mujobots record start                # 录制 64 m 内最近的实时机器人
/mujobots walk 0.35 0 0               # 让它走几秒
/mujobots record stop
/mujobots record list                 # 正在录制的和等待重试的导出
```

`start` / `stop` 也接受实体选择器或 UUID，可以同时录多台：`/mujobots record start @e[type=mujobots:g1]`。

文件写在存档目录下：

```text
<world>/mujobots/recordings/t2-<uuid8>-<UTC 时间>.npz
<world>/mujobots/recordings/t2-<uuid8>-<UTC 时间>.meta.json
```

单台机器人最多录 30,000 帧、600 秒仿真时间或约 128 MiB，先到先停。`stop`、实体卸载和关服都会自动导出。

## 2. 用 Python 读取

```sh
pip install "minepilot[numpy]"
```

```python
import numpy as np
from minepilot.recording import load_recording

r = load_recording("t2-01234567-20261110-120000.npz")
t = r.time[:, 0] - r.time[0, 0]               # 秒
print(r.meta["source"], r.meta["reference"])   # "sim"；G1 跟踪参考动作时给出片段信息
print(r.joint_names[:5], r.qpos.shape)         # 关节按名字字节序排列
travel = r.root_pose[-1, :3] - r.root_pose[0, :3]
feet = r.foot_wrench.reshape(len(r), len(r.foot_names), 6)
print(travel, feet[:, :, 2].mean(axis=0))      # 前进距离，每只脚的平均法向力（N）
```

## 3. 数据内容

| 数组 | 形状 | 含义 |
|---|---|---|
| `time`、`native_step` | N × 1 | 场景仿真时间（秒）和原生步号 |
| `root_pose` | N × 7 | 根刚体位置（m）和四元数（WXYZ） |
| `qpos`、`qvel` | N × J | 关节角（rad）和角速度（rad/s），按 `joint_names` 顺序 |
| `action`、`action_valid` | N × J、N × 1 | 策略网络输出（已对齐到关节顺序）及其是否有效 |
| `walk_command` | N × 3 | 请求的前进、左移速度（m/s）和转向角速度（rad/s） |
| `foot_wrench` | N × 6F | 静态地形作用在每只脚上的力（N）和力矩（N·m） |
| `body_pose` | N × 7B | 所有刚体的位姿，按 `body_names` 顺序 |
| `reference_id`、`reference_frame` | N × 1 | 正在跟踪的参考片段和帧（没有则为 −1） |

坐标系：绝对的 MuJoCo 世界坐标，右手系、Z 轴向上，和[刚体位姿流](/research/python/)完全一致；换算回 Minecraft 坐标是 `(x, z, −y)`。场景重建时坐标不会跳变（有 GameTest 专门检查）。`meta.json` 里的 `model_path` 是相对模组资产根目录的路径，不会暴露你电脑上的用户目录。`meta.json` 还带有 `format_version`（当前为 2）、`source`（目前总是 `sim`，`real` 预留给以后的真机日志）、模型文件的 SHA-256 和每个约定的文字说明。

关节和刚体都按**名字的 UTF-8 字节序**排列，并把名字列表存进文件，这样仿真数据和以后导入的真机日志可以直接按名字对齐。

## 4. 独立校验

`check-recording.py` 用一份独立的 MuJoCo 模型逐帧写回根位姿和关节角、做正运动学，再和录下的每个刚体位姿比较：

```sh
python -I scripts/check-recording.py t2-...npz --output check.json
```

发布前的实测：T2 行走 10 秒（500 帧）和 G1 行走 30 秒（1500 帧），所有刚体的最大位置误差都是 0 m。注意这验证的是导出的保真度，不是动力学重放。

## 5. 转成 LeRobot 数据集

导出器还没做，字段可以这样对应：一个文件是一个 episode；`observation.state` 取 `qpos`（可附加 `qvel`、根位姿、接触力）；`action` 取 `walk_command`（语义指令数据集）或 `action_valid=1` 的 `action`（策略输出数据集）；`timestamp` 取 `time - time[0]`。策略网络输出不是关节目标角，不要直接当成弧度用。完整说明见 MujoBots 仓库的 `docs/recording.md`。
