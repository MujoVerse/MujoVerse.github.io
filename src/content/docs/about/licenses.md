---
title: 许可与致谢
description: "四个模组的许可证，以及机器人模型、动作和运行库的来源。"
---

四个模组（MujoCraft、MujoBots、MinePilot、MineArena）的代码都使用 **Apache-2.0** 许可。下面列出的模型、动作和库保留各自的许可证；需要随文件分发的许可证文本已经打包在对应的 jar 里。

## 机器人

### Booster T2

- **机器人模型、行走与起身控制：** 来自 Booster Robotics 的 T2 软件栈，行走和起身控制随 T2 出厂固件提供。Booster 也在 [booster_assets](https://github.com/BoosterRobotics/booster_assets) 以 BSD-3-Clause 公开了 T2 的机器人描述。
- **v3 外观网格、材质和贴图：** MujoVerse 团队制作。

### 宇树 G1

- **机器人模型和网格：** NVIDIA [GR00T-WholeBodyControl](https://github.com/NVlabs/GR00T-WholeBodyControl) 打包的 G1 29 自由度描述（Apache-2.0）。
- **全身控制器 SONIC 的权重：** [nvidia/GEAR-SONIC](https://huggingface.co/nvidia/GEAR-SONIC)，NVIDIA Open Model Agreement，未重新训练。许可证全文随 jar 分发。
- **行走、后退、侧移和转向的参考动作：** 用 [ARDY-G1](https://github.com/nv-tlabs/ardy) 生成（代码 Apache-2.0；模型权重为 NVIDIA Open Model Agreement，该协议不主张对生成结果的所有权）。提示词、随机种子和所选帧都记录在 jar 内的 `motions-provenance.json`。

### 图鉴里的 33 款机器人

来自 [MuJoCo Menagerie](https://github.com/google-deepmind/mujoco_menagerie) 和 [booster_assets](https://github.com/BoosterRobotics/booster_assets)，包括 Booster 公开的舞蹈动作。每款机器人的文件夹里都附有上游的 `LICENSE`（Apache-2.0、MIT、BSD-3-Clause 或 BSD-2-Clause），`robot.json` 记录了来源地址、提交号和文件校验值。网格做了减面和重新编码，其他内容未改动。

机器人的名称和品牌归各自所有者；出现在这里不代表它们为本项目背书。

## 物理与比赛

- **MuJoCo**（[google-deepmind/mujoco](https://github.com/google-deepmind/mujoco)）：Apache-2.0，原生库随 MujoCraft 分发，其上游第三方声明一并打包。
- **RoboCup GameController 7.0**（[RoboCup-HumanoidSoccerLeague/GameController](https://github.com/RoboCup-HumanoidSoccerLeague/GameController)）：MIT，随 MineArena 分发。
- **足球的物理参数：** 沿用团队的 RoboCup Arena 运行时。黑白足球贴图是团队原创。
- **Valkyrien Skies 2**：LGPL-3.0。VS2 适配模块只调用它的公开接口，不复制、不打包它的代码。

## 运行库

- **ONNX Runtime** Java 1.31.1：MIT，随 MujoBots 分发（Windows x64、Linux x64、macOS arm64）。
- **Minecraft** 是 Mojang/Microsoft 的产品；**Fabric Loader / Fabric API**（Apache-2.0）是前置依赖。两者都不包含在我们的文件里。

## 博物馆精装版

精装版整合包里的装饰模组、Sodium、Iris 和 Complementary 光影由整合包从 Modrinth 下载，遵循各自的许可证，不包含在我们分发的文件里。
