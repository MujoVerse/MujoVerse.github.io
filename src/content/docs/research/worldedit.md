---
title: 用 WorldEdit 五分钟搭测试场
description: "用 WorldEdit 搭一条带碎石路、缓坡和台阶的行走测试道，让 T2 走一遍并分析录制。"
---

Minecraft 的方块是 1 米见方，直接用方块搭的坡是 1 米高的台阶，没有机器人走得上去。但 MujoCraft 采集地形时用的是每个方块真实的碰撞箱，所以可以用"不满一格"的方块做出细粒度的地形：

| 方块 | 碰撞高度 | 用途 |
|---|---|---|
| 地毯（carpet） | 6.25 cm | 小凸起、碎石路 |
| 雪层（snow，1–8 层） | (层数 − 1) × 12.5 cm | 缓坡、台阶；1 层没有碰撞 |
| 台阶（slab） | 50 cm | 高台阶、路沿 |

下面这条测试道用 [WorldEdit](https://modrinth.com/mod/worldedit) 7.3（Fabric 1.21.1）在 20 条命令内搭好，已在真实客户端里测过。

![测试道全景：地毯碎石区、雪层缓坡、25 cm 台阶](/media/test-course.webp)

## 1. 准备

- 在[快速开始](/research/quickstart/)的模组之外再装 WorldEdit。
- 新建一个**超平坦**、开启作弊的世界。超平坦地表在 y = −61，机器人站在 y = −60；如果你的地面高度不同，把下面命令里的 y 坐标整体平移。

## 2. 搭测试道

在聊天栏逐条输入（每条 WorldEdit 命令以 `//` 开头）：

```text
//pos1 -2,-61,-5
//pos2 64,-61,5
//set smooth_stone

//pos1 -2,-60,-5
//pos2 64,-50,5
//set air

//pos1 8,-60,-5
//pos2 15,-60,5
//set 35%white_carpet,65%air

//pos1 26,-60,-5
//pos2 32,-60,5
//set smooth_stone
//pos1 18,-61,-5
//pos2 40,-58,5
//snowsmooth 12

//pos1 50,-60,-5
//pos2 64,-60,5
//set snow[layers=3]
//desel
```

依次是：

1. 一条 67 × 11 米的光滑石板路面，并清空上方空间；
2. **x 8–15**：随机铺 35% 的地毯，6.25 cm 的随机凸起；
3. **x 18–40**：先放一块 1 米高的平台，再用 `//snowsmooth` 把周围平滑成雪层缓坡，最陡处每格升 12.5 cm；
4. **x 50 起**：一道 25 cm 高的雪层台阶（3 层雪）。

## 3. 让 T2 走一遍并录下来

```text
/mujobots spawn 1 -60 0
/mujobots record start
/mujobots walk 0.6 0 0
```

大约 100 秒后：

```text
/mujobots record stop
```

也可以用 [Python 客户端](/research/python/)驱动，换成你自己的速度曲线或控制器。

## 4. 分析

```python
import sys
import numpy as np
from minepilot.recording import load_recording

r = load_recording(sys.argv[1])
t = r.time[:, 0] - r.time[0, 0]
x, height = r.root_pose[:, 0], r.root_pose[:, 2]        # MuJoCo world: x = MC x, z = MC y
w, qx, qy, qz = r.root_pose[:, 3:].T
upright = 1 - 2 * (qx**2 + qy**2)                        # cosine between torso axis and vertical
for i in range(0, len(t), 250):
    print(f"t={t[i]:5.1f}s  x={x[i]:6.2f}  height={height[i]:7.3f}  upright={upright[i]:4.2f}")
if (upright < 0.5).any():
    i = int(np.argmax(upright < 0.5))
    print(f"fell at t={t[i]:.2f}s, x={x[i]:.2f}")
```

```sh
python analyze.py <世界>/mujobots/recordings/t2-....npz
```

我们实测的结果（T2 出厂 WALK 控制器，0.6 m/s）：

| 区段 | 结果 |
|---|---|
| 地毯碎石区 | 通过，竖直度保持 1.00 |
| 雪层缓坡（爬升约 0.5 m 再下坡） | 通过，竖直度最低 0.93 |
| 25 cm 台阶 | 在 x ≈ 51.2 处摔倒（t = 58 s） |

![T2 在 25 cm 台阶上摔倒](/media/test-course-fall.webp)

T2 的行走策略是在平地上训练的，越不过 25 cm 的台阶符合预期。换一个控制器、改台阶高度（`snow[layers=2]` 是 12.5 cm）或者打开 `/gamerule mujobotsAutoGetUp true` 让它摔倒后自己站起来，就能把这条测试道变成一组可重复的对比实验。

## 小技巧

- `//undo` 撤销上一步；`//set 20%stone_slab,80%air` 可以撒出 50 cm 的障碍物。
- `//snowsmooth` 的次数越多坡越缓；先用方块搭出大致高度，再平滑。
- 改动地形后，物理场景会自动重建，不需要重新生成机器人。
