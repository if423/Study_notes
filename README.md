# Agent 算法研究员 · 个人学习笔记

> 一个用于个人学习的项目，借助 Claude Code 自定义学习系统，系统化掌握 **AI Agent（智能体）** 领域的知识与实践。

## 关于本项目

这是一个纯个人学习用途的仓库。我通过 Claude Code 的「learn-anything」学习系统，围绕 **Agent 算法研究员** 这一主题进行结构化学习：由 AI 讲解概念、生成练习文件到本地 IDE 动手实践，并通过知识地图追踪掌握进度。

## 学习主题

目前仅有一条学习路径：**Agent 算法研究员**（未来会继续添加其他学习路径）。该主题覆盖以下领域：

- **Agent 基础架构** — Agent 定义与范式、感知-规划-执行循环、ReAct 模式、工具使用与 Function Calling、记忆系统设计
- **推理与规划** — 思维链推理、思维树与图推理、规划算法、自我反思与修正、多步推理优化
- **多 Agent 系统** — 通信协议、协作与竞争、角色分配、辩论与共识、群体智能
- **工具与代码执行** — Function Calling 机制、代码沙箱、RAG 检索增强、动态工具学习
- **评估与安全** — 评估基准、安全对齐、奖励模型设计、鲁棒性与可靠性
- **前沿研究方向** — 自主 Agent 架构、世界模型、Computer Use、长期自主、具身智能

## 目录结构

```
.
├── .claude/                 # Claude Code 自定义技能与命令（学习系统）
│   ├── skills/              # learn-anything 系列技能
│   └── commands/learn/      # /learn:* 斜杠命令
├── .learn/                  # 学习数据（自动生成，无需手动编辑）
│   └── topics/agent-算法研究员/
│       ├── knowledge-map.md # 知识地图（掌握进度）
│       ├── state.json       # 主题状态（概念、置信度、练习次数）
│       ├── sessions/        # 讲解记录
│       └── exercises/       # 实践练习（starter.py + README）
├── .venv/                   # Python 虚拟环境
└── test.py                  # 临时测试脚本
```

## 使用方法

通过斜杠命令与 Claude 交互学习：

| 命令 | 作用 |
|---|---|
| `/learn:topic` | 选择或查看学习主题 |
| `/learn:explain` | AI 讲解某个概念（可递归深入） |
| `/learn:practice` | 生成练习文件到 IDE 动手实践 |
| `/learn:quiz` | 生成测验检验掌握程度 |
| `/learn:review` | 复习已学内容 |
| `/learn:status` | 查看学习进度 |

## 学习进度

进度由 `.learn/topics/agent-算法研究员/knowledge-map.md` 与 `state.json` 自动追踪，可通过 `/learn:status` 查看实时状态。

---

*仅供个人学习使用，不用于生产或对外发布。*
