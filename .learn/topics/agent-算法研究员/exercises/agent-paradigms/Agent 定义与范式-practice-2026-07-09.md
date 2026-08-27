# Practice Session - 2026-07-09

## Concept Practiced
- Concept: Agent 定义与范式 | Difficulty: 🟢 Beginner | Exercise: GridWorld 清洁 Agent

## User's Submitted Code
```python
# 5 个 Agent 范式全部实现，见 starter.py

# ReactiveCleaner: 一行式 IF-THEN（功能正确，代码可读性差）
# ModelBasedCleaner: 内部地图 + 已知脏→探索未知→随机 fallback
# GoalBasedCleaner: BFS 搜索 + 计划执行（有隐蔽 bug）
# UtilityBasedCleaner: 三维效用函数 + max 选优
# BDICleaner: Belief→Desire→Intention + 意图重考虑
```

## Test Results
```
[OK] Reactive（反应式）:   9 steps
[OK] ModelBased（模型式）:  7 steps
[OK] GoalBased（目标驱动）:  7 steps
[OK] UtilityBased（效用驱动）: 7 steps
[OK] BDI:                  7 steps
5/5 Agent 完成清扫任务
```

## AI Feedback
整体表现扎实——5 个范式全部达到功能正确。五大范式的核心特征区分清晰：反应式无记忆、模型式维护内部地图、目标驱动做 BFS 规划、效用驱动多维打分、BDI 有意图持续性。

需要关注的改进点：
1. TODO 1 一行式代码可读性差，建议拆为 if/elif/else
2. TODO 3 `return "clean"` 被注释掉——靠 BFS 计划的末尾 "clean" 步骤兜底，耦合脆弱
3. TODO 3 `visited = set(start)` 得到 `{0}` 而非 `{(0,0)}`——靠类型不匹配巧合避过
4. TODO 5 `(inf, inf)` 哨兵值风险——空 options 时 Intention 被设置为无效坐标

## Assessment
- Understanding: Solid — 五个范式的核心特征都在代码中正确体现
- Status: in_progress → in_progress | Confidence: 0.1 → 0.25
