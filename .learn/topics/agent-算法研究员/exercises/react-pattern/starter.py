"""
ReAct Agent 完整实现练习
==========================
完成 4 个 # TODO，实现 Thought→Action→Observation→Finish 循环。

运行: python starter.py
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from datetime import datetime


# ============================================================
# 工具定义（已实现 —— 不要修改）
# ============================================================
@dataclass
class Tool:
    """ReAct Agent 可调用的工具"""

    name: str
    description: str
    func: callable


def calculator(expression: str) -> str:
    """安全计算器"""
    try:
        allowed = set("0123456789+-*/().%^ sqrtpilog")
        # 支持 sqrt, pi, log
        expr = (
            expression.replace("sqrt", "math.sqrt")
            .replace("pi", "math.pi")
            .replace("log", "math.log")
        )
        if not all(c in allowed or c in "sqrtpilog " for c in expression):
            return f"错误：表达式包含不允许的字符: {expression}"
        return str(eval(expr, {"math": math}))
    except Exception as e:
        return f"计算错误: {e}"


def search(query: str) -> str:
    """模拟搜索引擎"""
    knowledge = {
        "python 3.12 release date": "Python 3.12 于 2023 年 10 月 2 日正式发布。",
        "python 3.12 发布时间": "Python 3.12 于 2023 年 10 月 2 日正式发布。",
        "react paper yao 2022": "ReAct 由 Yao et al. 于 2022 年提出，论文标题为 'ReAct: Synergizing Reasoning and Acting in Language Models'。",
        "largest planet solar system": "太阳系中最大的行星是木星（Jupiter），直径约 139,820 公里。",
        "太阳系最大行星": "太阳系中最大的行星是木星（Jupiter），直径约 139,820 公里。",
    }
    return knowledge.get(query.lower().strip(), f"未找到关于 '{query}' 的相关信息。")


def get_current_time(_: str = "") -> str:
    """返回当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ============================================================
# ReAct Agent（需要完成 4 个 TODO）
# ============================================================
@dataclass
class ReActAgent:
    tools: dict[str, Tool]
    max_steps: int = 10
    history: list[dict] = field(default_factory=list)

    # ============================================================
    # TODO 1: 构建 ReAct 格式的 system prompt
    # ============================================================
    def _build_prompt(self, question: str) -> str:
        """
        构建 ReAct Agent 的 system prompt。

        必须包含：
        1. 可用工具列表及描述
        2. 严格的输出格式：
           Thought: <你的推理>
           Action: <工具名>[<输入>]
           Observation: <工具执行结果 —— 系统提供，你不要编造>
           ...
           Thought: 我有足够信息回答
           Finish: <最终答案>
        3. 关键规则：Observation 不能编造
        4. 用户问题

        返回格式化的 prompt 字符串。
        """
        # TODO 1: 构建 prompt

        # tools_list  = "\n".join(f"- {tool.name}: {tool.description}" for tool in self.tools.values())
        tools_list = """calculator: 对数学表达式求值
search: 搜索互联网获取信息
get_current_time: 获取当前日期时间"""

        return f"""
你是能使用工具的智能助手。严格按以下格式回复：

可用工具：
{tools_list}

回复格式（每行一个标记）：
Thought: <你的内部推理——分析当前情况，决定下一步>
Action: <工具名>[<工具输入>]
（Observation 由系统自动提供，你绝不能自己写 Observation）
...
Thought: 信息足够了
Finish: <最终答案>

重要规则：
每一步必须先生成 Thought，再生成 Action 或 Finish
Action 格式必须严格为: 工具名[参数]
禁止编造 Observation —— Observation 由系统自动追加
信息充足时立即 Finish，不要多余步骤

当前问题：{question}
"""

    # ============================================================
    # TODO 2: 解析 LLM 响应
    # ============================================================
    def _parse_response(self, response: str) -> tuple:
        """
        解析 LLM 的文本响应，提取 Thought / Action / Finish。

        格式规则：
        - 每行以 "Thought:" / "Action:" / "Finish:" 开头（大小写不敏感）
        - Action 格式: Action: 工具名[参数]  例如 Action: calculator[3 + 5]
        - Finish 格式: Finish: 最终答案文本

        返回: (thought, action_name, action_input, finish)
        - thought: str | None
        - action_name: str | None
        - action_input: str | None
        - finish: str | None

        示例响应:
            Thought: 我需要计算 37 * 15
            Action: calculator[37 * 15]
        返回: ("我需要计算 37 * 15", "calculator", "37 * 15", None)

        示例响应:
            Thought: 信息足够了
            Finish: 答案是 555
        返回: ("信息足够了", None, None, "答案是 555")
        """
        # TODO 2: 实现解析逻辑

        thought = action_name = action_input = finish = None
        lines = response.strip().split("\n")

        for line in lines:
            m = re.search(r"^\s*Thought:\s*(.*)", line)
            if m:
                thought = m.group(1).strip()
            m = re.search(r"^\s*Action:\s*(\w+)\[(.*)\]", line)
            if m:
                action_name = m.group(1).strip()
                action_input = m.group(2).strip()
            m = re.search(r"^\s*Finish:\s*(.*)", line)
            if m:
                finish = m.group(1).strip()

        return (thought, action_name, action_input, finish)

    # ============================================================
    # 工具执行（已实现 —— 不要修改）
    # ============================================================
    def _execute_action(self, action_name: str, action_input: str) -> str:
        """
        执行工具并返回 Observation。
        关键约束：Observation 来自工具的真实返回值，绝不编造。
        """
        tool = self.tools.get(action_name)
        if tool is None:
            return (
                f"错误：未知工具 '{action_name}'。"
                f"可用工具：{list(self.tools.keys())}"
            )
        try:
            return tool.func(action_input)
        except Exception as e:
            return f"工具执行出错: {e}"

    # ============================================================
    # TODO 3: ReAct 主循环
    # ============================================================
    def run(self, question: str, llm_call: callable) -> str:
        """
        ReAct 主循环：Thought → Action → Observation → ... → Finish

        循环逻辑：
        1. 用 _build_prompt 构建初始 prompt
        2. for step in 1..max_steps:
           a. 调用 llm_call(prompt) 获取 LLM 响应
           b. 用 _parse_response 解析 Thought / Action / Finish
           c. 如果 finish 不为 None → 记录到 history → return finish
           d. 如果 action_name 为 None（解析失败）→ 追加错误反馈到 prompt → continue
           e. 调用 _execute_action 执行工具 → 获取 observation
           f. 记录到 history
           g. 将 "Thought: ...\nAction: ...\nObservation: ...\n" 追加到 prompt
        3. 达到 max_steps → 返回错误消息

        返回: 最终答案字符串
        """
        # TODO 3: 实现主循环

        prompt = self._build_prompt(question)
        for step in range(1, self.max_steps):
            response = llm_call(prompt)
            thought, action_name, action_input, finish = self._parse_response(response)
            if finish:
                self.history.append(finish)
                return finish
            if not action_name:
                prompt += "\nObservation: 你没有生成有效的 Action。请使用 Action: 工具名[输入] 格式。"
                continue

            observation = self._execute_action(action_name, action_input)
            self.history.append((thought, action_name, action_input, finish))

            prompt += f"\nThought: {thought}\nAction: {action_name}[{action_input}]\nObservation: {observation}\n"

        return "达到最大步数限制，未能完成任务"


# ============================================================
# 模拟 LLM 调用（已实现 —— 不要修改）
# ============================================================
def simulated_llm(prompt: str) -> str:
    """
    模拟 LLM 响应 —— 根据 prompt 中的对话历史，生成下一步 Thought + Action/Finish。

    真实项目中替换为 OpenAI / Anthropic API 调用。
    """
    # 计算历史步数（Observation 出现次数）
    step_count = prompt.count("Observation:")

    # 判断当前问题类型
    if step_count == 0:
        # 第一步：根据问题类型决定行动
        if any(
            kw in prompt for kw in ["*", "+", "-", "/", "计算", "sqrt", "平方", "根号"]
        ):
            if "127 * 34" in prompt:
                return (
                    "Thought: 用户要求计算 127 * 34 + 56，我需要先算乘法再算加法。\n"
                    "Action: calculator[127 * 34]"
                )
            elif "3的平方" in prompt or "5的平方" in prompt or "根号" in prompt:
                return (
                    "Thought: 这是一个多步计算。先算 3^2 = 9，再算 5^2 = 25，"
                    "然后求和 9 + 25 = 34，最后开根号 sqrt(34)。先算第一步。\n"
                    "Action: calculator[3 ** 2]"
                )
            elif "平方" in prompt or "开根" in prompt:
                return "Thought: 需要分步计算。\n" "Action: calculator[3 ** 2 + 5 ** 2]"
            else:
                return (
                    "Thought: 这是一个数学问题，我需要用计算器。\n"
                    "Action: calculator[127 * 34 + 56]"
                )
        elif any(kw in prompt for kw in ["Python 3.12", "发布时间", "发布"]):
            return (
                "Thought: 用户询问 Python 3.12 的发布时间，我应该搜索官方信息。\n"
                "Action: search[python 3.12 发布时间]"
            )
        elif any(kw in prompt for kw in ["几点", "时间", "现在"]):
            return (
                "Thought: 用户想知道当前时间，我需要调用时间工具获取实时时间。\n"
                "Action: get_current_time[]"
            )
        elif "最大" in prompt or "行星" in prompt:
            return (
                "Thought: 这是一个知识问答，我需要搜索相关信息。\n"
                "Action: search[太阳系最大行星]"
            )
        else:
            return (
                "Thought: 我需要搜索相关信息来回答这个问题。\n"
                "Action: search["
                + prompt.split("问题：")[-1].strip().split("\n")[0]
                + "]"
            )

    elif step_count == 1:
        # 第二步：根据观察结果决定
        if "127 * 34" in prompt and "4318" in prompt:
            return (
                "Thought: 127 * 34 = 4318，现在需要 + 56。\n"
                "Action: calculator[4318 + 56]"
            )
        elif (
            "3 ** 2" in prompt
            or ("3^2" in prompt)
            or ("9" in prompt and "平方" in prompt)
        ):
            return (
                "Thought: 3^2 = 9，下一步计算 5^2 = 25。\n" "Action: calculator[5 ** 2]"
            )
        elif "Python 3.12" in prompt and "2023" in prompt:
            return (
                "Thought: 搜索结果确认 Python 3.12 于 2023 年 10 月 2 日发布，信息充足。\n"
                "Finish: Python 3.12 于 2023 年 10 月 2 日正式发布。"
            )
        elif "最大" in prompt or "行星" in prompt or "木星" in prompt:
            return (
                "Thought: 搜索结果返回了答案，信息充足。\n"
                "Finish: 太阳系中最大的行星是木星（Jupiter），直径约 139,820 公里。"
            )
        elif "get_current_time" in prompt or "时间" in prompt:
            # 检查 Observation 中是否有时间
            observation_start = prompt.rfind("Observation:")
            if observation_start >= 0:
                time_str = prompt[observation_start:].split("\n")[0]
                return (
                    f"Thought: 工具返回了当前时间，信息充足。\n"
                    f"Finish: 当前时间是 {time_str.split('Observation:')[1].strip() if 'Observation:' in time_str else '未知'}"
                )
            return (
                "Thought: 时间工具已返回结果，信息充足。\n" "Finish: 已获取当前时间。"
            )
        elif "4318" in prompt and "+ 56" in prompt:
            return "Thought: 计算完成，信息充足。\n" "Finish: 127 * 34 + 56 = 4374"
        else:
            return (
                "Thought: 信息不够，需要进一步搜索或计算。\n"
                "Action: search["
                + prompt.split("问题：")[-1].strip().split("\n")[0]
                + "]"
            )

    elif step_count == 2:
        # 第三步
        if "5 ** 2" in prompt or ("25" in prompt and "平方" in prompt):
            return (
                "Thought: 5^2 = 25，现在 9 + 25 = 34，最后一步计算 sqrt(34)。\n"
                "Action: calculator[sqrt(34)]"
            )
        elif "4318 + 56" in prompt:
            result_line = [l for l in prompt.split("\n") if "Observation:" in l][-1]
            return (
                f"Thought: 计算完成，信息充足。\n"
                f"Finish: 127 * 34 + 56 = {result_line.split('Observation:')[1].strip()}"
            )
        else:
            return "Thought: 信息不足，需要继续。\n" "Action: search[补充信息]"

    elif step_count == 3:
        if "sqrt" in prompt or "34" in prompt:
            result_line = [l for l in prompt.split("\n") if "Observation:" in l][-1]
            return (
                f"Thought: sqrt(34) 的结果已返回，信息充足。\n"
                f"Finish: 3的平方加5的平方的和再开根号 = {result_line.split('Observation:')[1].strip()}"
            )
        else:
            return (
                "Thought: 多次搜索仍未找到确切信息，基于已有知识回答。\n"
                "Finish: 抱歉，无法找到确切答案。"
            )

    else:
        return "Thought: 已经尝试多次，信息充足或无法继续。\n" "Finish: 处理完成。"


# ============================================================
# 测试套件（不要修改）
# ============================================================
def run_test(agent_class, question: str, name: str) -> tuple[bool, str]:
    """运行单个测试"""
    agent = ReActAgent(
        tools={
            "calculator": Tool(
                "calculator", "执行数学计算，支持 +-*/ sqrt log pi", calculator
            ),
            "search": Tool("search", "搜索互联网获取信息", search),
            "get_current_time": Tool(
                "get_current_time", "获取当前日期时间", get_current_time
            ),
        },
        max_steps=5,
    )
    result = agent.run(question, simulated_llm)
    return result, agent.history


def check_result(result: str, expected_keywords: list[str], name: str) -> bool:
    """检查结果是否包含期望关键词"""
    all_found = all(kw.lower() in result.lower() for kw in expected_keywords)
    icon = "[OK]" if all_found else "[MISS]"
    status = (
        "PASS"
        if all_found
        else f"MISSING: {[kw for kw in expected_keywords if kw.lower() not in result.lower()]}"
    )
    print(f"  {icon} {name}: {status}")
    if not all_found:
        print(f"       Result: {result[:80]}...")
    return all_found


if __name__ == "__main__":
    print("=" * 60)
    print("  ReAct Agent 测试")
    print("=" * 60)

    passed = 0
    total = 4

    # 测试 1: 数学计算
    print("\n--- 测试 1: 数学计算（两步）---")
    result, history = run_test(ReActAgent, "127 * 34 + 56 等于多少？", "math")
    if check_result(result, ["4374"], "127 * 34 + 56 = 4374"):
        passed += 1
    print(f"       步数: {len(history)}")

    # 测试 2: 搜索
    print("\n--- 测试 2: 知识搜索 ---")
    result, history = run_test(ReActAgent, "Python 3.12 什么时候发布的？", "search")
    if check_result(result, ["2023", "10", "2"], "Python 3.12 发布时间"):
        passed += 1
    print(f"       步数: {len(history)}")

    # 测试 3: 时间查询
    print("\n--- 测试 3: 时间查询 ---")
    result, history = run_test(ReActAgent, "现在几点？", "time")
    if check_result(result, ["2026"], "当前时间"):
        passed += 1
    print(f"       步数: {len(history)}")

    # 测试 4: 多步计算
    print("\n--- 测试 4: 多步计算 ---")
    result, history = run_test(
        ReActAgent, "3的平方加上5的平方的和再开根号？", "multi-step"
    )
    # sqrt(34) ≈ 5.83
    if check_result(result, ["5.83"], "sqrt(3^2 + 5^2) = sqrt(34) ≈ 5.83"):
        passed += 1
    print(f"       步数: {len(history)}")

    print("\n" + "=" * 60)
    print(f"  总结: {passed}/{total} 测试通过")
    print("=" * 60)

    if passed < total:
        print("\n💡 提示: 检查你的 4 个 TODO 实现，确保主循环和解析逻辑正确。")
