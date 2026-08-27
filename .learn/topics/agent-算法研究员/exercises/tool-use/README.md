# 🛠️ 练习：Native Function Calling —— 从文本解析到结构化工具调用

> **难度**: 🟡 中级 &nbsp;|&nbsp; **概念**: 工具使用与 Function Calling &nbsp;|&nbsp; **语言**: Python

---

## 📋 背景

你在 ReAct 练习中实现的工具调用是 **Text-based** 方式——LLM 输出 `Action: calculator[127 * 34]`，你用正则解析。这种方式有 1-5% 的解析失败率。

本次练习你要把它升级为 **Native Function Calling**——用 JSON Schema 定义工具接口，LLM 返回结构化的 `tool_use` 块，**零解析失败**。

---

## 🎯 场景

同样的 3 个工具（calculator / search / get_current_time），但用两种方式对比实现。你要完成 Native 方式的核心组件。

---

## ✅ 需要完成的任务（5 个 TODO）

打开 `starter.py`：

| # | 方法 | 内容 | 考察点 |
|---|---|---|---|
| TODO 1 | `define_tools()` | 用 JSON Schema 定义 3 个工具 | `name`/`description`/`input_schema`、`enum`、`required` |
| TODO 2 | `_tools_to_api_format()` | 将定义转为 API 要求的格式 | 数据结构转换 |
| TODO 3 | `_execute_tool()` | 执行工具 + 三层错误防御 | 结构化错误返回 |
| TODO 4 | `run()` 主循环 | 处理 tool_use → 执行 → tool_result → 发回 | 串行 + 并行调用 |
| TODO 5 | 错误重试 | LLM 收到错误后修正参数重试 | 次数上限 |

---

## 💡 提示

<details>
<summary>🔍 提示 1 — JSON Schema 五铁律</summary>

```python
{
    "name": "get_weather",
    "description": "写给 LLM 看的语义说明（1-2 句，带示例值）",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "用中文城市名，如'北京'"},
            "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
        },
        "required": ["city"],   # 必填才写
    },
}
```
</details>

<details>
<summary>🔍 提示 2 — 执行层的结构化错误</summary>

```python
# 错误信息必须让 LLM 能理解"为什么错 + 如何修正"
try:
    result = func(**args)
    return {"status": "success", "data": result}
except Exception as e:
    return {
        "status": "error",
        "error_type": type(e).__name__,
        "message": str(e),
        "received_args": args,   # 帮 LLM 定位错在哪
    }
```
</details>

<details>
<summary>🔍 提示 3 — 主循环处理 tool_use 块</summary>

```python
# response.content 是混合列表:
#   [{"type": "text", "text": "..."}, {"type": "tool_use", "name": "...", "input": {...}}]

# 1. 筛选 tool_use 块（可能多个 → 并行）
# 2. 对每个 tool_use 执行工具 → 得到结果
# 3. 构造 tool_result 块（带 tool_use_id 关联）
# 4. 追加到 messages 发回
```
</details>

<details>
<summary>🔍 提示 4 — 重试上限</summary>

```python
# 记录每个工具的连续失败次数
# 同一工具失败 ≥ 3 次 → 停止重试，返回兜底答案
# 避免无限循环消耗 token
```
</details>

---

## 🔗 相关概念

- **ReAct 模式** — Text-based 工具调用的载体
- **感知-规划-执行循环** — SPA 的 Act 层工程化
- **记忆系统设计** — 工具结果与记忆的交汇

---

## 📊 评分标准

| 维度 | ✅ Strong | 🟡 Partial | 🔴 Weak |
|---|---|---|---|
| Schema 设计 | `enum`/`required`/`type` 正确使用 | 有 schema 但不完整 | 无 schema |
| 执行层防御 | 三层都实现 | 只有 try/except | 无防御 |
| 主循环 | 串行 + 并行都支持 | 只支持串行 | 无法发回结果 |
| 错误重试 | 带上限 + 修正参数 | 重试但无上限 | 不重试 |
| 测试通过 | 4/4 | 2-3 | <2 |

---

完成后告诉我，我会 review 你的代码！
