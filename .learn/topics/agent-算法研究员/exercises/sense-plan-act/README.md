# 🛠️ 练习：SPA 循环——探矿 Agent

> **难度**: 🟡 中级 &nbsp;|&nbsp; **概念**: 感知-规划-执行循环 &nbsp;|&nbsp; **语言**: Python

---

## 📋 背景

SPA 循环（Sense → Plan → Act → 反馈闭环）是所有 Agent 的元模式。之前你实现的五种范式 Agent 和 ReAct Agent，本质上都是在 SPA 骨架上填充不同的 Plan 策略。

本次练习聚焦于**SPA 循环本身**——在不同的 Plan 策略之间切换时，Sense 和 Act 如何保持不变，反馈闭环如何统一运作。

---

## 🎯 场景

你是一个**探矿机器人**，在 5×5 的未知矿区中寻找金矿。每次移动消耗能量，你需要找到尽可能多的金矿。

```
5×5 矿区（Agent 视角）:
┌───┬───┬───┬───┬───┐
│ ? │ ? │ ? │ ? │ ? │    ?  = 未探索
├───┼───┼───┼───┼───┤    ⛏  = Agent
│ ? │ ? │ ? │ ? │ ? │    ✨  = 发现的金矿
├───┼───┼───┼───┼───┤    ·  = 空地
│ ? │ ? │ ⛏│ ? │ ? │
├───┼───┼───┼───┼───┤
│ ? │ ? │ ? │ ? │ ? │
├───┼───┼───┼───┼───┤
│ ? │ ? │ ? │ ? │ ? │
└───┴───┴───┴───┴───┘
  视野: 相邻 4 格（曼哈顿距离 1）
```

---

## ✅ 需要完成的任务（5 个 TODO）

打开 `starter.py`，按顺序完成：

| # | 方法 | 内容 | 核心考察 |
|---|---|---|---|
| TODO 1 | `sense()` | 从环境获取感知，生成状态估计 | 部分可观测性处理：已知 / 未知 / 推断 |
| TODO 2 | `plan_reactive()` | 反应式：最近的金矿 → 移过去；没有 → 探索未知 | 最简单的 Plan |
| TODO 3 | `plan_utility()` | 效用式：多维度打分选最优（距离 + 确定性 + 能耗） | 效用函数设计 |
| TODO 4 | `act()` | 执行行动，返回执行结果 + 预期效果 | 执行监控——行动是否按预期完成 |
| TODO 5 | `run()` 主循环 | SPA 循环 + **反馈闭环**：实际 vs 预期对比 | SPA 的灵魂——闭环 |

---

## 💡 提示

<details>
<summary>🔍 提示 1 — sense() 的三层信息</summary>

```python
# sense() 返回的结构:
{
    "position": (r, c),         # 当前位置
    "known_map": [[...], ...],  # 已知地图: -1=未知, 0=空地, 1=金矿
    "visible": {                # 当前视野内
        "up": 0或1或-1, "down": ..., "left": ..., "right": ...
    },
    "energy": int,              # 剩余能量
    "gold_collected": int,      # 已采集
}
```
</details>

<details>
<summary>🔍 提示 2 — 反馈闭环的核心代码</summary>

```python
# 在 run() 中，执行行动后:
expected = {...}   # act() 返回的预期效果
actual = sense()   # 重新感知

# 反馈闭环检查:
if actual["position"] != expected["position"]:
    # 移动失败（被墙挡住？）→ 更新地图
if actual["known_map"][r][c] != expected["map_change"]:
    # 预期外的情况（金矿已经被采？）→ 修正信念
```
</details>

<details>
<summary>🔍 提示 3 — 效用函数维度建议</summary>

```python
# plan_utility() 给每个候选行动打分:
#   gold_proximity:  距已知金矿的曼哈顿距离 → 1/(1+dist)
#                    无已知金矿 → 0
#   explore_value:   距最近未知格子的距离 → 1/(1+dist)
#                    无未知格子 → 0
#   energy_cost:     移动 = -0.1, 采集 = -0.05
#   权重: gold=0.5, explore=0.3, energy=0.2
```
</details>

---

## 🔗 相关概念

- **Agent 定义与范式** — SPA 是所有范式的元模式
- **ReAct 模式** — SPA 在 LLM 上的 Prompt 工程实例
- **工具使用与 Function Calling** — SPA 的 Act 层工程化

---

## 📊 评分标准

| 维度 | ✅ Strong | 🟡 Partial | 🔴 Weak |
|---|---|---|---|
| Sense 状态估计 | 正确处理已知/未知/推断 | 能更新但未区分 | 只复制原始感知 |
| Plan 策略 | 两个策略都正确且区分清晰 | 一个策略正确 | 两个都有误 |
| Act 执行监控 | 返回预期效果供反馈闭环 | 能执行但不返回预期 | 只调 env 方法 |
| 反馈闭环 | 对比预期 vs 实际 + 修正 | 有对比但未修正 | 无闭环 |
| 能量耗尽处理 | 合理终止 | 能终止但晚 | 死循环 |

---

完成后告诉我，我会 review 你的代码！
