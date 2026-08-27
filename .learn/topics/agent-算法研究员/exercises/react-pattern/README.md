# 🛠️ 练习：ReAct Agent 完整实现

> **难度**: 🟢 入门 &nbsp;|&nbsp; **概念**: ReAct 模式 &nbsp;|&nbsp; **语言**: Python

---

## 📋 背景

ReAct（**Re**asoning + **Act**ing）是 LLM Agent 的核心推理模式：

```
Thought₁ → Action₁ → Observation₁ → Thought₂ → Action₂ → Observation₂ → ... → Finish
```

你需要完成一个完整的 ReAct Agent，它能使用三个工具来回答问题：计算器、搜索引擎（模拟）、当前时间查询。

---

## 🎯 练习目标

实现 `ReActAgent` 类的核心循环，让以下测试全部通过：

```
场景 1: "127 * 34 + 56 等于多少？"        → 应该用计算器
场景 2: "Python 3.12 什么时候发布的？"     → 应该用搜索引擎
场景 3: "现在几点？"（trick: 模型可能不知道）→ 应该用时间工具
场景 4: 两步任务 "3的平方加上5的平方的和再开根号？" → 应该多次调用计算器
```

---

## ✅ 需要完成的任务

打开 `starter.py`，找到所有 `# TODO` 标记（共 4 个）：

| # | 位置 | 内容 |
|---|---|---|
| TODO 1 | `_parse_response()` | 解析 LLM 响应的 Thought / Action / Finish |
| TODO 2 | `_execute_action()` | 执行工具并返回 Observation（绝不能编造） |
| TODO 3 | `run()` 主循环 | 完整的 Thought→Action→Observation→...→Finish 循环 |
| TODO 4 | `_build_prompt()` | 构建 ReAct 格式的 system prompt |

---

## 💡 提示

<details>
<summary>🔍 提示 1 — 解析 Thought/Action/Finish</summary>

```python
# LLM 响应的格式（逐行）：
#   Thought: <推理文本>
#   Action: <工具名>[<参数>]
#   Thought: 信息足够了
#   Finish: <最终答案>

# 正则提取 Action:  r"(\w+)\[(.*)\]"
# 大小写不敏感的 startswith("thought:") / startswith("action:") / startswith("finish:")
```
</details>

<details>
<summary>🔍 提示 2 — Observation 的正确来源</summary>

```python
# Observation 必须来自 tool.func(tool_input) 的真实返回值
# 绝不能由模型文本生成 —— 这是 ReAct 最核心的约束
# 未知工具 → Observation = "错误：未知工具 'xxx'。可用工具：[列表]"
```
</details>

<details>
<summary>🔍 提示 3 — 主循环的终止条件</summary>

```python
# while steps < max_steps:
#   1. llm_call(prompt) → response
#   2. _parse_response(response) → thought, action, finish
#   3. if finish: 记录 → return finish
#   4. if action is None: prompt += feedback → continue
#   5. observation = _execute_action(action)
#   6. prompt += f"Thought: {thought}\nAction: ...\nObservation: {observation}\n"
#   7. steps += 1
```
</details>

<details>
<summary>🔍 提示 4 — Prompt 设计关键点</summary>

```python
# 必须包含：
#   1. 可用工具列表及描述
#   2. 严格的输出格式要求（Thought/Action/Observation/Finish）
#   3. 重要规则："Observation 由系统提供，你绝不能编造"
#   4. 当前用户问题
```
</details>

---

## 🔗 相关概念

- **Agent 定义与范式** — ReAct 连接了经典范式与现代 LLM
- **感知-规划-执行循环** — ReAct 是 SPA 的 LLM 特化
- **工具使用与 Function Calling** — ReAct 的 Action 层工程化

---

## 📊 评分标准

| 维度 | ✅ Strong | 🟡 Partial | 🔴 Weak |
|---|---|---|---|
| 解析逻辑 | 正确处理 Thought/Action/Finish 三种标记 | 能解析但遗漏边界情况 | 解析失败 |
| 主循环 | 正确的 T→A→O 交替 + 终止条件 | 循环正确但终止不对 | 死循环或不执行 |
| Observation | 全部来自工具真实返回值 | 部分来自工具 | 模型编造 |
| 测试通过 | 4/4 场景通过 | 2-3 通过 | <2 通过 |

---

完成或遇到困难时告诉我，我会 review 你的代码！
