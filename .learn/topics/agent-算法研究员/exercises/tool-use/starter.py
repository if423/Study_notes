"""
Native Function Calling 练习
=============================
完成 5 个 # TODO，实现结构化工具调用（对比 Text-based 的 ReAct 练习）。

运行: python starter.py
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable


# ============================================================
# 工具实现（只读 —— 不要修改）
# ============================================================
def calculator(expression: str) -> str:
    """执行数学计算"""
    try:
        expr = (
            expression.replace("sqrt", "math.sqrt")
            .replace("pi", "math.pi")
            .replace("log", "math.log")
        )
        allowed = set("0123456789+-*/().%^ ")
        # 检查原始表达式（替换前）是否含非法字符
        if not all(c in allowed or c in "sqrtpilog " for c in expression):
            return f"错误：表达式包含不允许的字符: {expression}"
        return str(eval(expr, {"math": math}))
    except Exception as e:
        return f"计算错误: {e}"


def search(query: str) -> str:
    """搜索（模拟）"""
    knowledge = {
        "python 3.12 release date": "Python 3.12 于 2023 年 10 月 2 日发布。",
        "python 3.12 发布时间": "Python 3.12 于 2023 年 10 月 2 日发布。",
        "largest planet": "太阳系最大行星是木星（Jupiter）。",
    }
    return knowledge.get(query.lower().strip(), f"未找到 '{query}' 的信息")


def get_current_time(_: str = "") -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ============================================================
# 工具定义（TODO 1 需完成 define_tools）
# ============================================================
@dataclass
class ToolDefinition:
    """工具的 JSON Schema 定义"""

    name: str
    description: str
    input_schema: dict
    func: Callable


class NativeAgent:
    """Native Function Calling Agent"""

    def __init__(self):
        self.tools: dict[str, ToolDefinition] = {}
        self.failure_counts: dict[str, int] = {}  # 每工具连续失败次数
        self.max_retries: int = 3

    # ============================================================
    # TODO 1: 定义工具（JSON Schema）
    # ============================================================
    def define_tools(self) -> None:
        """
        用 JSON Schema 定义 3 个工具，填充 self.tools。

        工具：
        1. calculator: 执行数学计算
           - expression (string, required): 数学表达式，如 "3 + 5 * 2" 或 "sqrt(34)"
        2. search: 搜索信息
           - query (string, required): 搜索关键词
        3. get_current_time: 获取当前时间
           - 无参数（input_schema 的 required 为空数组）

        每个 ToolDefinition 的字段:
        - name: 工具名
        - description: 写给 LLM 的语义说明（1-2 句，带示例）
        - input_schema: JSON Schema（type/properties/required）
        - func: 对应的函数（calculator / search / get_current_time）

        关键：description 写语义（如"用中文关键词"），不写类型（schema 已声明）。
        """
        # TODO 1: 定义 3 个工具
        {
            "name": "calculator",
            "description": "执行数学计算",
            "input_schema": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，如 '3 + 5 * 2' 或 'sqrt(34)'",
                    }
                },
                "required": [""],
            },
            "sync": "calculator",
        }

    # ============================================================
    # TODO 2: 转换为 API 格式
    # ============================================================
    def _tools_to_api_format(self) -> list[dict]:
        """
        将 self.tools 转为 API 请求的 tools 参数格式。

        Anthropic 格式：
        [
            {"name": ..., "description": ..., "input_schema": {...}},
            ...
        ]

        注意：不要包含 func 字段（那是本地执行用的，不是发给 API 的）。
        """
        # TODO 2: 返回 API 格式的工具列表
        pass

    # ============================================================
    # TODO 3: 执行工具 + 三层错误防御
    # ============================================================
    def _execute_tool(self, name: str, args: dict) -> dict:
        """
        执行工具，返回结构化的结果。

        三层防御：
        1. 未知工具 → 返回 error + 可用工具列表
        2. 执行异常 → 捕获，返回 error + error_type + message + received_args
        3. 成功 → 返回 success + data

        返回结构：
        {"status": "success", "data": ...} 或
        {"status": "error", "error_type": ..., "message": ..., "received_args": ...}
        """
        # TODO 3: 实现执行 + 错误防御
        pass

    # ============================================================
    # TODO 4: Native Function Calling 主循环
    # ============================================================
    def run(self, question: str, api_call: Callable) -> str:
        """
        Native Function Calling 主循环。

        参数:
            question: 用户问题
            api_call: 模拟 LLM API。签名 (messages, tools) -> response
                      response 格式见 simulated_api_call 的注释。

        循环逻辑：
        1. messages = [{"role": "user", "content": question}]
        2. for _ in range(max_steps):
           a. response = api_call(messages, self._tools_to_api_format())
           b. 从 response["content"] 筛出 tool_use 块
           c. 如果没有 tool_use → 拼接 text 块返回
           d. 对每个 tool_use 执行工具 → tool_result
           e. 构造 assistant 消息（含原 content）+ user 消息（含 tool_results）
           f. 追加到 messages
        3. 返回兜底消息

        关键：tool_result 必须带 tool_use_id 关联到具体调用。
        """
        # TODO 4: 实现主循环
        pass

    # ============================================================
    # TODO 5: 错误重试逻辑
    # ============================================================
    def _should_retry(self, name: str, result: dict) -> bool:
        """
        判断是否应该继续重试某个工具。

        规则：
        - 如果 result 是 success → 重置该工具失败计数，返回 True（继续）
        - 如果 result 是 error：
            * 失败计数 +1
            * 失败计数 < max_retries → True（允许重试）
            * 失败计数 >= max_retries → False（停止，避免死循环）

        返回 True 表示"可以继续"（无论成功还是可重试的失败），
        False 表示"应停止"（达到重试上限）。
        """
        # TODO 5: 实现重试判断
        pass


# ============================================================
# 模拟 LLM API（只读 —— 不要修改）
# ============================================================
def simulated_api_call(messages: list, tools: list) -> dict:
    """
    模拟 Anthropic API 响应。
    根据对话历史生成 tool_use 块或 text 块。

    返回格式:
    {
        "content": [
            {"type": "tool_use", "id": "...", "name": "...", "input": {...}},
            # 或多个 tool_use 块（并行调用）
            # 或 {"type": "text", "text": "..."}（最终答案）
        ]
    }
    """
    # 统计历史中 tool_use 的次数
    tool_use_count = sum(
        1
        for msg in messages
        if isinstance(msg.get("content"), list)
        for block in msg["content"]
        if block.get("type") == "tool_use"
    )

    question = messages[0]["content"] if messages else ""

    if tool_use_count == 0:
        # 第一步：根据问题决定调用
        if "python" in question.lower() and "发布时间" in question:
            return {
                "content": [
                    {
                        "type": "tool_use",
                        "id": "call_001",
                        "name": "search",
                        "input": {"query": "python 3.12 发布时间"},
                    }
                ]
            }
        elif "计算" in question or "*" in question or "+" in question:
            return {
                "content": [
                    {
                        "type": "tool_use",
                        "id": "call_001",
                        "name": "calculator",
                        "input": {"expression": "127 * 34 + 56"},
                    }
                ]
            }
        elif "几点" in question or "时间" in question:
            return {
                "content": [
                    {
                        "type": "tool_use",
                        "id": "call_001",
                        "name": "get_current_time",
                        "input": {},
                    }
                ]
            }
        # 并行调用：两个独立查询
        elif "比较" in question or "都" in question:
            return {
                "content": [
                    {
                        "type": "tool_use",
                        "id": "call_001",
                        "name": "calculator",
                        "input": {"expression": "3 * 4"},
                    },
                    {
                        "type": "tool_use",
                        "id": "call_002",
                        "name": "calculator",
                        "input": {"expression": "5 * 6"},
                    },
                ]
            }
        else:
            return {
                "content": [
                    {
                        "type": "tool_use",
                        "id": "call_001",
                        "name": "search",
                        "input": {"query": question},
                    },
                ]
            }

    # 后续步骤：根据已有结果决定
    last_result = None
    for msg in messages:
        if isinstance(msg.get("content"), list):
            for block in msg["content"]:
                if block.get("type") == "tool_result":
                    last_result = block.get("content", "")

    if tool_use_count >= 1 and last_result:
        # 检查是否是错误结果（需要重试）
        if "error" in last_result and "错误" not in last_result:
            # 第一次错误：修正参数重试
            return {
                "content": [
                    {
                        "type": "tool_use",
                        "id": "call_002",
                        "name": "search",
                        "input": {"query": "python 3.12 release date"},
                    }
                ]
            }

        # 成功：给出最终答案
        if "2023" in last_result or "4374" in last_result or ":" in last_result:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"最终答案：{last_result}",
                    }
                ]
            }

    # 兜底
    return {"content": [{"type": "text", "text": "无法回答"}]}


# ============================================================
# 测试套件（不要修改）
# ============================================================
def test_scenario(
    agent: NativeAgent, question: str, name: str, expected_keywords: list[str]
) -> bool:
    """运行单个场景并检查结果"""
    agent.failure_counts.clear()
    result = agent.run(question, simulated_api_call)
    all_found = all(kw in result for kw in expected_keywords)
    icon = "[OK]" if all_found else "[MISS]"
    print(f"  {icon} {name}")
    if not all_found:
        print(f"       Result: {result[:80]}...")
        print(f"       Missing: {[kw for kw in expected_keywords if kw not in result]}")
    return all_found


if __name__ == "__main__":
    print("=" * 60)
    print("  Native Function Calling 测试")
    print("=" * 60)

    agent = NativeAgent()
    agent.define_tools()

    # 先测试 TODO 1：工具定义
    print("\n--- 检查工具定义 ---")
    if len(agent.tools) == 3:
        print(f"  [OK] 定义了 {len(agent.tools)} 个工具: {list(agent.tools.keys())}")
        schema_ok = all(
            "input_schema" in t.__dict__ or t.input_schema for t in agent.tools.values()
        )
        print(f"  [OK] 每个工具有 input_schema: {schema_ok}")
    else:
        print(f"  [FAIL] 工具数量: {len(agent.tools)} (应为 3)")

    # 测试 TODO 2：API 格式
    print("\n--- 检查 API 格式 ---")
    api_tools = agent._tools_to_api_format()
    no_func = all("func" not in t for t in api_tools)
    print(f"  [{'OK' if no_func else 'FAIL'}] API 格式不包含 func: {no_func}")

    # 测试场景
    print("\n--- 测试场景 ---")
    passed = 0
    total = 4

    if test_scenario(agent, "Python 3.12 什么时候发布的？", "单步搜索", ["2023"]):
        passed += 1

    if test_scenario(agent, "127 * 34 + 56 等于多少？", "单步计算", ["4374"]):
        passed += 1

    if test_scenario(agent, "现在几点？", "时间查询", ["20"]):  # 年份包含 20
        passed += 1

    if test_scenario(
        agent, "比较一下 3*4 和 5*6 分别等于多少？", "并行计算", ["12", "30"]
    ):
        passed += 1

    print("\n" + "=" * 60)
    print(f"  总结: {passed}/{total} 测试场景通过")
    print("=" * 60)

    if passed < total:
        print("\n💡 提示: 检查 TODO 4 主循环的 tool_use 处理和 tool_result 构造。")
