# Practice Session - 2026-07-26

## Concept Practiced
- Concept: ReAct 模式 | Difficulty: 🟢 Beginner | Exercise: ReAct Agent 完整实现

## User's Submitted Code
```python
# _build_prompt(): 三段式结构 — 工具列表 + 语法格式 + 铁律 + 问题
# _parse_response(): 逐行正则解析 Thought/Action/Finish，锚定行首，单次搜索
# run() 主循环: build → call LLM → parse → finish? → execute → append to prompt
```

## Test Results
```
[OK] 数学计算（两步）:  3 steps
[OK] 知识搜索:          2 steps
[OK] 时间查询:          2 steps
[OK] 多步计算:          4 steps
4/4 测试通过
```

## AI Feedback
整体表现扎实。ReAct 循环的四个核心组件全部正确实现：
- `_build_prompt`: 三段式结构清晰，工具描述格式化正确
- `_parse_response`: 逐行正则解析，变量初始化、单次搜索、`^\s*` 锚定都正确
- `run()`: Thought→Action→Observation 交替完整，finish 终止、解析失败重试、错误反馈用 Observation 格式、Action 括号正确

遇到的坑及解决：
- 工具描述中的 `+-*/` 污染了 simulated_llm 的关键词匹配 → 手写工具描述去掉特殊字符
- `simulated_llm` 生成 `math.sqrt(34)` 而 calculator 期望 `sqrt(34)` → 模拟 LLM 的 bug，已修复

关键学习点：prompt 中的每个字符都会影响 LLM 行为——工具描述是 prompt 工程的一部分，不能简单拼接原始字符串。

## Assessment
- Understanding: Solid — ReAct 循环机制理解到位，四组件实现正确
- Status: in_progress → in_progress | Confidence: 0.15 → 0.30
