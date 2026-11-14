---
title: 给图鉴添加机器人
description: "从 MJCF 导出展品：网格减面、姿态片段、许可证检查。"
---

图鉴里的展品只用来展示：减面后的可视网格（RVM1 格式）加上预先计算好的连杆位姿（RMR1 格式），不跑物理也不跑策略。`MujoBots/scripts/exhibits/catalog.json` 是唯一的数据来源，`scripts/export-exhibit.py` 把每个条目导出到 `hf-assets/exhibits/<id>/`，并重建索引和语言文件里的名称。

## 步骤

1. 把源仓库放到 `../robot-sources/` 下，**只当数据用，不运行其中的代码**。
2. 阅读它的 `LICENSE`（见下面的规则），在 `catalog.json` 里加一个条目：
   - `id`、`name`、`nameZh`、`maker`、`year`（首次公开的年份，不确定写 `null`）、`category`（`humanoid|quadruped|biped|arm|hand|mobile|aerial|other`）；
   - `blurb` / `blurbZh`：各一句事实陈述，不夸张、不写无法核实的内容；
   - `mjcf`、`license`、`spdx`、`source`、`commit`；
   - 显示相关：`keyframe`（优先用模型自带的 `home`/`stand`）、`pose`（关节覆盖值）、`groups`（可视/碰撞几何分组特殊时指定）、`triangles`（默认 40,000；机器人 25k–40k，无人机和小部件更少）、`mount`（`[rx, ry, rz]` 度，模型躺倒或侧向时使用）。机器人必须朝向 +x。
   - 动作片段：`{"kind": "pose"}`；机械臂、灵巧手和夹爪用 `{"kind": "sweep", "joints": "<正则>", "amplitude": 0.15}`；可再分发的动作数据用 `{"kind": "qpos", ...}`。**不要给足式机器人编造运动。**
3. 先导出到临时目录检查：

   ```sh
   .tools/exporter-venv/bin/python -I scripts/export-exhibit.py --catalog scripts/exhibits/catalog.json \
       --sources ../robot-sources --out temp/exhibits-build/out --only <id>
   ```

   如果某个片段低于展台表面，导出器会警告；调整姿态或减小摆动幅度。
4. 正式导出（加 `--lang src/main/resources/assets/mujobots/lang`），保持总量在约 90 MB 以内（`du -sh hf-assets/exhibits`），然后运行 `./gradlew compileClientJava test`。
5. 用 `scripts/hf-assets.py upload` 发布资产并更新 `assets.lock.json`。

## 许可证规则

- 只收录 `LICENSE` 允许再分发和修改的模型（Apache-2.0、MIT、BSD-2/3-Clause 等）。**不收录**非商用、禁止演绎或"保留所有权利"的资产。
- `spdx` 按实际的 `LICENSE` 文本填写，不按 README 徽章。MuJoCo Menagerie 的许可证是按模型目录分别给出的。
- 导出器会把 `LICENSE` 复制进每个展品目录，不要删掉：BSD 和 MIT 许可要求声明随网格一起分发。
- 动作数据也是资产，只有仓库许可覆盖时才能用（例如 booster_assets 整个仓库都是 BSD-3-Clause，包括 `motions/`）。
