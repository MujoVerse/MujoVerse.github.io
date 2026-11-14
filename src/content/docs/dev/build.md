---
title: 从源码构建
description: "克隆四个仓库、拉取资产、构建发布用的 jar、运行测试。"
---

## 目录结构

四个模组是四个独立的 Git 仓库，但 Gradle 构建会从相邻目录引用彼此（`../MujoCraft` 等），所以要并排放在同一个文件夹里：

```text
MujoVerse/
├── MujoCraft/    # 物理核心（MuJoCo JNI）
├── MujoBots/     # 机器人、图鉴、渲染、控制 API
├── MinePilot/    # 驾驶、本机桥接、Python 包 python/
└── MineArena/    # 足球场地、GameController、比赛
```

```sh
mkdir MujoVerse && cd MujoVerse
for r in MujoCraft MujoBots MinePilot MineArena; do git clone https://github.com/MujoVerse/$r.git; done
```

## 工具链

- **JDK 21。** macOS（Apple 芯片）上 `MujoCraft/scripts/setup.sh` 会自动下载 Corretto 21 到 `MujoCraft/.tools/jdk`；其他平台自行安装 JDK 21 并设置 `JAVA_HOME`。
- 三个平台的 MuJoCo 原生库和 GameController 原生库已经预编译在 `MujoCraft/native/prebuilt/` 和 `MineArena/native/prebuilt/`，普通构建不需要 C++ 工具链。重新编译原生库的方法见各自的 `native/README.md`。

## 构建

```sh
cd MujoCraft && bash scripts/setup.sh
export JAVA_HOME=$PWD/.tools/jdk/Contents/Home     # 其他平台换成你的 JDK 21
./gradlew build
cd ../MujoBots && ./gradlew build
```

MujoBots 的机器人模型、权重和图鉴网格（约 300 MB）不在 Git 里，构建时由 `fetchAssets` 按 `assets.lock.json` 锁定的版本从 Hugging Face [MujoVerse/mujobots-assets](https://huggingface.co/MujoVerse/mujobots-assets) 下载到 `hf-assets/`，逐个校验 SHA-256。

MujoBots 的构建产出核心 jar 和三个机器人包（T2、G1、展品），并自动检查每个 jar：

- 每个文件都有对应的许可声明和来源记录；
- 受限文件按哈希清单拦截；
- G1 包内嵌的 ONNX Runtime 带有三个平台的原生库。

产物在每个仓库的 `build/libs/`。

## 测试

```sh
./gradlew test             # 单元测试
./gradlew runGametest      # 在真实的无界面 Minecraft 服务器里跑 GameTest
./gradlew runClient        # 开发用客户端
```

MinePilot 的构建会同时启动它自己和 MineArena 的 GameTest 服务器。两个游戏进程同时跑时，个别依赖物理时序的足球测试可能超时，建议加 `--max-workers=1`。

Python 包：

```sh
cd MinePilot/python
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -e '.[test,mcp]'
.venv/bin/pytest
```
