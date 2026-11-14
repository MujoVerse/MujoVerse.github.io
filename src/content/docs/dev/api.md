---
title: 模组开发 API
description: "让你的模组控制机器人、读取物理状态，或者接入新的物理后端。"
---

MujoVerse 的 Java API 面向同一个 JVM 里的其他 Fabric 模组。外部程序请用[本机桥接](/research/protocol/)。

## 控制机器人：`dev.mujobots.api`

T2 和 G1 都实现 `ControllableRobot`。按能力判断，不要按实体类判断：

| 类型 | 作用 |
|---|---|
| `ControllableRobot` | 能力、当前控制源、认领/释放、请求起身、最新观测 |
| `RobotCapabilities` | 速度和头部的可用范围、是否能射门 |
| `RobotControlSource` | 你实现的回调：每个原生控制步之前的 `beforeStep(context)`、`controlsApplied`、`afterTick(observation)`、释放通知 |
| `RobotControlContext` | 一个控制步的观测，加上 `walk`、`head`、`shoot`、`recover` 四个语义动作 |
| `RobotObservation` | UUID、根位置、偏航和角速度、机身速度、竖直度、原生步号和时间、头部角度、恢复状态 |
| `RobotAppearance`（可选） | 机身颜色和球衣号码（T2） |
| `RefereeResettable`（可选） | 裁判摆位（T2） |
| `PhysicalRobot`（可选，不稳定） | 原生刚体视图：步数、竖直度、刚体索引、脚部刚体、渲染采样 |

规则：

- `claimControl(source)` 成功会清零之前的 WALK/SHOOT 请求；第二个控制源不能抢走已有的控制。
- 控制只通过语义动作：没有根位姿写入、力矩数组或原生句柄。
- 起身拥有最高优先级，起身期间 WALK/SHOOT 不能覆盖它的力矩。
- 所有回调都在服务器线程上、针对当前原生步调用。控制源和玩家身份不会写进存档。

| | T2 | G1 |
|---|---|---|
| 前进 / 横移 / 转向 | −1.5…3 m/s，±1 m/s，±2 rad/s | 0…1.5 m/s，横移需对应参考动作，±1 rad/s |
| 头部 | 偏航 ±1.134 rad，俯仰 −0.349…0.436 rad | 无 |
| 起身 | 有 | 无（`requestRecovery()` 返回 false） |

## 物理：`dev.mujocraft`

- **`PhysicsBackend`**：与引擎无关的物理接口。按名字访问 body、joint、actuator、sensor；坐标 SI 单位、Z 向上，四元数 WXYZ；`jointLayout(names)` 给出每个关节的 qpos/qvel 维度和偏移，不要自己假设 MuJoCo 的排列。MuJoCo 是唯一的实现，也是默认实现。
- **能力标志**：`CONTACT_WRENCH`、`CONTACT_WRENCH_BETWEEN`、`EXTERNAL_WRENCH`、`IMPULSE`、`IMPULSE_AT`。不支持的能力抛出 `UnsupportedOperationException`，绝不悄悄换成别的引擎。
- **快照**：不透明字节，带后端 ID 和模型版本；恢复到别的后端或模型会被拒绝。世界在创建时选定后端，存档不跨后端迁移。
- **`PhysicsWorld.addStepListener`**：每个 2 ms 原生步在积分前调用一次（服务器线程），传入步号和仿真时间。MinePilot 的 500 Hz 刚体位姿流就是用它实现的。
- **`PhysicsParticipant`**：让你的实体加入共享场景，和机器人、刚体结构、地形一起参与接触。
- **`Impulsable`**：让物理重锤能敲动你的实体。

完整说明：MujoBots 仓库的 `docs/robot-control-api.md`，MujoCraft 仓库的 `docs/backend.md`。
