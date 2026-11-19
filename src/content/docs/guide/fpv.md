---
title: FPV 穿越机
description: MujoBots 四旋翼与 MinePilot 飞行视角。
---

这是 **Minecraft Java 1.21.1 / Fabric 的开发版功能**。手飞需要 Fabric API、MujoCraft、包含四旋翼的 MujoBots core 和带飞行支持的 MinePilot。无人机不需要人形或四足机器人包。网页博物馆试玩不运行此功能。

<video controls muted playsinline preload="none" poster="/media/fpv-flight.webp" src="/media/fpv-flight.mp4"></video>

## 试飞

从创造物品栏取 **FPV 穿越机套件**（`/give @s mujobots:drone_kit`），右键平地部署。瞄准飞机按 `R` 或右键接管。

| 按键 | 操作 |
| --- | --- |
| `Space` / `Shift` | 辅助模式爬升 / 下降；Acro 增 / 减油门 |
| `W A S D` | 辅助模式平移；Acro 控制俯仰和横滚角速度 |
| `←` / `→` | 偏航 |
| `V` | 地面 → FPV → 水平稳拍 |
| `↑` / `↓` | 调整镜头仰角 |
| `B` | 起飞后切换辅助 / Acro，与镜头模式独立 |
| `K` / `G` | 自动降落 / 退出驾驶并触发降落 |

飞手留在地面，遥控上限为 48 米，也受已追踪区块限制。Acro 松开方向键不会自动回正；失焦或出范围会尝试就地降落，不会自动返航。

## 实录与范围

视频是自动化单人客户端的游戏实录：穿越青门、侧倾并切换稳拍。该次飞行爬升 **3.69 米**，FPV 峰值横倾 **39.8°**。四旋翼是通用刚体模型，尚未按真机标定；这不是多人或真人手飞验收。
