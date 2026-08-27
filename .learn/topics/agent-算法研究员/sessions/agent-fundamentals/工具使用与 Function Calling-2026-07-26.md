# 工具使用与 Function Calling — 学习会话

> **日期:** 2026-07-26
> **主题:** Agent 算法研究员
> **路径:** Agent 基础架构 → 工具使用与 Function Calling
> **难度:** 入门→进阶

---

## 定位

在 Agent 基础架构的五个概念中，这是连接「理论设计」与「工程落地」的枢纽。前三个概念（Agent 范式、ReAct 模式、SPA 循环）定义了 Agent **应该怎么做**；工具使用与 Function Calling 定义了 Agent **能做什么**——以及如何用工程手段让"能做什么"变得可靠、可扩展、可维护。它一端连着 ReAct 的 Action 层，另一端连着 LLM API 的原生协议。

---

## 核心机制

### 一、两种工具调用范式：Text-based vs Native Function Calling

在 LLM Agent 中，让模型使用工具有两种根本不同的方式：

#### 方式 A：文本格式（Text-based Action Parsing）

这就是你在 ReAct 练习中实现的方式：

```
Action: calculator[127 * 34]
```

**规则**：
1. 在 prompt 中以自然语言描述工具
2. LLM 以固定文本格式（如 `Action: name[input]`）输出调用意图
3. Agent 代码用正则/解析器从 LLM 的文本输出中提取工具名和参数
4. Agent 执行工具，将结果以 `Observation:` 格式追加回 prompt

**优点**：任何 LLM 都支持，不依赖 API 特性。
**缺点**：
- 解析不可靠——LLM 可能输出格式错误（少括号、多空格、工具名拼错）
- 参数只能是纯文本字符串，无法传递结构化数据（嵌套对象、数组等）
- 没有类型检查——LLM 可能传字符串给需要数字的参数

#### 方式 B：原生 Function Calling（Native Function Calling / Tool Use）

现代 LLM API（OpenAI、Anthropic）在协议层原生支持工具调用：

**完整流程**：

```
1. 你定义 tools 数组（JSON Schema 格式），随请求一起发送
2. LLM 不生成文本，而是生成一个结构化的 tool_use 块
3. API 返回的不是文本，而是一个 tool_calls 数组
4. 你执行函数，将结果以 tool_result 格式发回
5. LLM 收到结果后决定继续调用工具还是生成最终文本
```

**严格区别**：

| | Text-based | Native Function Calling |
|---|---|---|
| 工具定义位置 | Prompt 文本 | API 请求的 `tools` 参数 |
| 输出格式 | 自由文本（需正则解析） | 结构化 JSON（类型安全） |
| 参数类型 | 只支持字符串 | 字符串、数字、布尔、对象、数组、枚举 |
| 并行调用 | 不支持（需手动拆分文本） | 原生支持（一次返回多个 tool_use） |
| 解析失败率 | 1-5%（格式错误） | 0%（协议保证结构化） |
| 模型支持 | 任何 LLM | OpenAI、Anthropic、部分开源模型 |

### 二、工具定义：JSON Schema 规范

原生 Function Calling 的核心是**用 JSON Schema 定义工具接口**。这是整个机制中最重要也最容易出错的环节。

#### Anthropic 格式（Tool Use）

```json
{
  "name": "get_weather",
  "description": "获取指定城市的当前天气信息",
  "input_schema": {
    "type": "object",
    "properties": {
      "city": {
        "type": "string",
        "description": "城市名称，使用中文，例如'北京'、'上海'"
      },
      "unit": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"],
        "description": "温度单位，默认 celsius"
      }
    },
    "required": ["city"]
  }
}
```

#### OpenAI 格式

```json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "获取指定城市的当前天气信息",
    "parameters": {
      "type": "object",
      "properties": {
        "city": {
          "type": "string",
          "description": "城市名称，使用中文，例如'北京'、'上海'"
        },
        "unit": {
          "type": "string",
          "enum": ["celsius", "fahrenheit"],
          "description": "温度单位，默认 celsius"
        }
      },
      "required": ["city"]
    }
  }
}
```

**Schema 设计的五个铁律**：

1. **`description` 是写给 LLM 看的，不是写给程序员看的**。不要写"城市参数，字符串类型"——LLM 不需要知道类型（schema 已经声明了）。写"使用中文城市名，例如'北京'而非'Beijing'"——这是在告诉 LLM 传什么语义值。

2. **`enum` 优先于 `description` 中的约束**。如果参数只有 3 个合法值，用 `enum` 而非在 description 里写"只能是 A、B 或 C"。`enum` 是硬约束，description 是软建议。

3. **`required` 数组必须实事求是**。把可选参数放进 `required` → LLM 必须每次都传，可能被迫编造值。把必填参数漏掉 → LLM 可能不传，导致函数执行失败。

4. **嵌套对象的深度不超过 2 层**。LLM 对深层嵌套结构的填充准确率急剧下降。如果参数需要复杂结构，考虑拆成多个工具或扁平化。

5. **每个工具的职责必须互斥且完备**。如果两个工具的功能有重叠（如 `search_web` 和 `search_docs`），LLM 的选择会不稳定。如果某个场景没有对应的工具，LLM 会强行用不合适的工具。

### 三、工具选择策略：LLM 如何决定用哪个工具

当 prompt 中同时有 5 个、10 个甚至 50 个工具时，LLM 如何选择？

**选择过程（黑盒但有规律）**：

1. **语义匹配**：LLM 将用户意图与每个工具的 `name` + `description` 做语义相似度匹配。这是最重要的信号。
2. **参数兼容性**：如果用户的问题中能提取出的信息恰好匹配某个工具的参数，该工具的权重上升。
3. **上下文惯性**：如果前一步调用了工具 A，LLM 倾向于继续调用 A 或 A 的关联工具。
4. **`tool_choice` 参数强制**：API 提供了对工具选择的控制：
   - `"auto"`（默认）：LLM 自己决定
   - `"any"` / `"required"`：必须调用一个工具
   - `{"type": "tool", "name": "get_weather"}`：强制调用特定工具

**工具数量与准确率的关系**：

| 工具数量 | 选择准确率 | 建议 |
|---|---|---|
| 1-5 | ~95% | 直接放，不需优化 |
| 5-20 | ~85% | 按领域分组，根据上下文动态注入 |
| 20-50 | ~70% | 需要工具检索（Tool Retrieval）——先搜再选 |
| 50+ | <60% | 必须用 RAG 预筛选 + 分层工具组 |

### 四、多工具编排（Orchestration）

单个工具的调用很简单，真正的复杂度在**多个工具的协作**。

#### 模式 1：串行依赖（Sequential Dependency）

工具 B 的输入依赖工具 A 的输出。这是最常见的模式。

```
用户: "北京到上海的航班，最便宜的那班的出发机场天气如何？"

步骤 1: search_flights("北京", "上海") → [{price: 580, flight: "CA1234", departure: "PEK"}]
步骤 2: get_weather("北京首都国际机场") → {temp: 25, condition: "晴"}
```

**实现要点**：不需要你做任何特别的事——LLM 看到第一个工具的结果后，自然会在下一轮决定调用第二个工具。ReAct 的 T→A→O 循环天然支持串行依赖。

#### 模式 2：并行调用（Parallel Calls）

多个工具互不依赖，可以同时调用。

```
用户: "北京和上海今天天气分别怎么样？"

→ 同时调用:
  get_weather("北京") → {temp: 25, ...}
  get_weather("上海") → {temp: 30, ...}
```

**实现要点**：
- Anthropic：LLM 在单次响应中可以返回多个 `tool_use` 块
- OpenAI：设置 `parallel_tool_calls=True`（默认）
- 你需要收集所有结果，统一发回

#### 模式 3：竞争调用（Speculative / Fallback）

对同一个目标尝试多种工具，取最先成功或最好的结果。

```
用户: "Python 3.12 发布时间？"

→ 同时调用:
  search_web("Python 3.12 release date")
  search_docs("python.org 3.12 release")
  
→ 取两个结果中信息更完整的那一个
```

#### 模式 4：条件分支（Conditional Branching）

根据中间结果决定下一步工具选择。这依赖 LLM 的推理能力。

```
步骤 1: get_order_status(order_id) → {status: "shipped", carrier: "SF"}
步骤 2: if status == "shipped" → track_package(tracking_id, carrier)
        else → cancel_order(order_id)
```

### 五、错误处理与重试

工具调用不是总能成功。一个健壮的 Agent 需要三层防御：

**第一层：Schema 层防御**

在定义工具时就防止可预期的错误：

```json
{
  "city": {
    "type": "string",
    "description": "城市名。必须是中国城市的标准中文名称，如'北京'而非'北京市'或'beijing'。"
  }
}
```

LLM 可能仍然传错，但概率大幅降低。

**第二层：执行层防御**

在 `_execute_action` 中捕获异常，返回结构化的错误 Observation：

```python
def execute_tool(name, args):
    try:
        result = tool_func(**args)
        return {"status": "success", "data": result}
    except ValueError as e:
        return {"status": "error", "error_type": "invalid_argument", "message": str(e)}
    except Exception as e:
        return {"status": "error", "error_type": "execution_failed", "message": str(e)}
```

**关键**：错误信息必须足够详细，让 LLM 能理解"为什么错了"并修正。`"执行失败"` 没用；`"参数 city='北精' 不是有效的城市名，可用城市：北京、上海、广州"` 有用。

**第三层：LLM 层重试**

LLM 收到错误 Observation 后，在下一轮 ReAct 循环中修正参数并重试。这是 ReAct 的反馈闭环在工具调用上的具体体现。

```python
# Agent 看到:
# Observation: {"status": "error", "message": "城市 '北精' 不存在。可用: 北京、上海、广州"}

# LLM 的下一步 Thought:
# "我把'北精'拼错了，应该是'北京'。修正参数重试。"
# Action: get_weather("北京")
```

**重试次数限制**：必须设置上限。同一工具连续失败 3 次 → 放弃并告知用户，而非无限重试。

---

## 类比

把 Native Function Calling 和 Text-based 的对比想象成**餐厅点餐的两种方式**：

- **Text-based**：你在餐巾纸上手写"我要一份宫保鸡丁少辣"，服务员要辨认你的字迹（解析），可能把"少辣"看成"多辣"（解析错误）。
- **Native Function Calling**：你在一张标准点餐卡上勾选——菜名从菜单里选（`enum`），辣度从 {不辣, 微辣, 中辣, 特辣} 中圈一个（类型约束），数量写数字（类型检查）。厨房收到的是一份结构化的 JSON，不会出错。

> ⚠️ 这个类比的局限：餐厅点餐卡是封闭选项（只有菜单上的菜），而 LLM 的工具选择是开放语义匹配——它能够根据自然语言描述推断你想用哪个工具，即使你的措辞不完全匹配。点餐卡做不到"我想吃点清淡的"→自动推荐白灼菜心。

---

## 代码示例

以下是一个对比实现：先用 Text-based 方式（对应 ReAct 练习），再用 Native Function Calling 方式（Anthropic SDK），展示两者的工程差异。

```python
"""
工具使用与 Function Calling —— Text-based vs Native 对比实现
"""

import json
import re
from dataclasses import dataclass
from typing import Any


# ============================================================
# 1. 共享的工具实现
# ============================================================
def get_weather(city: str, unit: str = "celsius") -> dict:
    """获取天气（模拟）"""
    weather_data = {
        "北京": {"celsius": 25, "fahrenheit": 77, "condition": "晴"},
        "上海": {"celsius": 30, "fahrenheit": 86, "condition": "多云"},
    }
    data = weather_data.get(city)
    if not data:
        return {"status": "error", "message": f"未知城市: {city}"}
    return {
        "status": "success",
        "city": city,
        "temperature": data[unit],
        "unit": unit,
        "condition": data["condition"],
    }


# ============================================================
# 2. 方式 A: Text-based（ReAct 风格 —— 你对这个已经很熟了）
# ============================================================
class TextBasedAgent:
    """
    工具通过 prompt 文本描述，LLM 输出文本格式的 Action，
    Agent 用正则解析。
    """

    def _build_prompt(self, question: str) -> str:
        return f"""可用工具：
- get_weather: 获取城市天气。参数: city(必填,城市名), unit(可选,celsius/fahrenheit)

回复格式：
Thought: <推理>
Action: get_weather[city=北京, unit=celsius]
（Observation 由系统提供）

问题：{question}
"""

    def _parse_action(self, response: str) -> tuple[str | None, dict | None]:
        """正则解析 —— 脆弱点！LLM 格式稍有偏差就失败"""
        m = re.search(r'Action:\s*(\w+)\[(.*)\]', response)
        if not m:
            return None, None

        tool_name = m.group(1)
        args_str = m.group(2)

        # 手动解析 "city=北京, unit=celsius" → {"city": "北京", "unit": "celsius"}
        args = {}
        for part in args_str.split(","):
            part = part.strip()
            if "=" in part:
                key, val = part.split("=", 1)
                args[key.strip()] = val.strip()

        return tool_name, args

    def run(self, question: str, llm_call: callable) -> str:
        prompt = self._build_prompt(question)

        for _ in range(5):
            response = llm_call(prompt)
            tool_name, args = self._parse_action(response)

            if tool_name is None:
                prompt += f"\n{response}\nObservation: 格式错误，"
                prompt += '请使用 Action: 工具名[参数1=值1, 参数2=值2]'
                continue

            # 执行工具
            if tool_name == "get_weather":
                result = get_weather(**args)  # 可能因参数不匹配崩溃
            else:
                result = {"status": "error", "message": f"未知工具: {tool_name}"}

            prompt += (
                f"\n{response}\n"
                f"Observation: {json.dumps(result, ensure_ascii=False)}\n"
            )

            if result.get("status") == "success":
                return f"{args.get('city', '未知')}天气: {result['temperature']}°"
        return "失败"


# ============================================================
# 3. 方式 B: Native Function Calling（Anthropic SDK 风格）
# ============================================================
@dataclass
class ToolDefinition:
    """工具的 JSON Schema 定义 —— 类型安全、结构化"""
    name: str
    description: str
    input_schema: dict


GET_WEATHER_TOOL = ToolDefinition(
    name="get_weather",
    description="获取指定城市的当前天气信息",
    input_schema={
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "城市名称，使用中文，例如'北京'、'上海'",
            },
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "温度单位，默认 celsius",
            },
        },
        "required": ["city"],
    },
)


class NativeFunctionCallingAgent:
    """
    工具通过 JSON Schema 定义，LLM 返回结构化 tool_use 块，
    不需正则解析，参数类型有保证。
    """

    def __init__(self, tools: list[ToolDefinition]):
        self.tools = {t.name: t for t in tools}
        self.tool_funcs = {"get_weather": get_weather}

    def _tools_to_api_format(self) -> list[dict]:
        """将 ToolDefinition 转为 Anthropic API 格式"""
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_schema,
            }
            for t in self.tools.values()
        ]

    def run(self, question: str, api_call: callable) -> str:
        """
        简化的 Native Function Calling 循环。

        真实项目中 api_call 的实现：
            import anthropic
            client = anthropic.Anthropic()
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                tools=self._tools_to_api_format(),
                messages=[{"role": "user", "content": question}],
            )
            # response.content 中包含 text 块和 tool_use 块
        """
        messages = [{"role": "user", "content": question}]

        for _ in range(5):
            response = api_call(messages, self._tools_to_api_format())

            # response.content 是一个混合列表:
            # [TextBlock(text="..."), ToolUseBlock(name="get_weather", input={...})]

            tool_uses = [
                block for block in response.get("content", [])
                if block.get("type") == "tool_use"
            ]

            if not tool_uses:
                # 没有工具调用 → LLM 直接回答了
                text_blocks = [
                    b["text"] for b in response["content"]
                    if b["type"] == "text"
                ]
                return "\n".join(text_blocks)

            # 执行所有工具（支持并行调用）
            tool_results = []
            for tool_use in tool_uses:
                tool_name = tool_use["name"]
                tool_input = tool_use["input"]  # 已经是 dict，类型安全！

                func = self.tool_funcs.get(tool_name)
                if func:
                    try:
                        result = func(**tool_input)
                    except Exception as e:
                        result = {
                            "status": "error",
                            "error_type": type(e).__name__,
                            "message": str(e),
                            # 附带参数信息帮 LLM 修正
                            "received_args": tool_input,
                        }
                else:
                    result = {
                        "status": "error",
                        "message": f"未知工具: {tool_name}",
                        "available": list(self.tool_funcs.keys()),
                    }

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use["id"],
                    "content": json.dumps(result, ensure_ascii=False),
                })

            # 将结果发回 —— LLM 决定下一步
            messages.append({
                "role": "assistant",
                "content": response["content"],
            })
            messages.append({
                "role": "user",
                "content": tool_results,
            })

        return "达到最大步数限制"


# ============================================================
# 4. 对比演示
# ============================================================
if __name__ == "__main__":
    # --- Text-based 演示 ---
    print("=" * 50)
    print("Text-based Agent")
    print("=" * 50)

    step = [0]
    def text_llm(prompt: str) -> str:
        step[0] += 1
        if step[0] == 1:
            return (
                "Thought: 用户想知道北京天气\n"
                "Action: get_weather[city=北京, unit=celsius]"
            )
        return "Thought: 信息足够了\nFinish: 完成"

    agent1 = TextBasedAgent()
    result1 = agent1.run("北京天气怎么样？", text_llm)
    print(f"结果: {result1}")
    print(f"工具定义: 在 prompt 文本中")
    print(f"参数解析: 正则 'city=北京, unit=celsius' → dict")

    # --- Native Function Calling 演示 ---
    print("\n" + "=" * 50)
    print("Native Function Calling Agent")
    print("=" * 50)

    def native_api(messages: list, tools: list) -> dict:
        """模拟 Anthropic API 响应"""
        return {
            "content": [
                {
                    "type": "tool_use",
                    "id": "tool_001",
                    "name": "get_weather",
                    "input": {"city": "北京", "unit": "celsius"},
                }
            ]
        }

    agent2 = NativeFunctionCallingAgent(tools=[GET_WEATHER_TOOL])
    result2 = agent2.run("北京天气怎么样？", native_api)
    print(f"结果: {result2}")
    print(f"工具定义: JSON Schema (类型安全)")
    print(f"参数获取: tool_use['input'] → 直接是 dict")
```

**代码走读**：

| 模块 | 关键设计 |
|---|---|
| `TextBasedAgent._parse_action()` | 正则 `r'Action:\s*(\w+)\[(.*)\]'` + 手动 `split(",")` + `split("=")` ——三层解析，每一层都可能因 LLM 输出格式微小偏差而失败 |
| `NativeFunctionCallingAgent._tools_to_api_format()` | 将 Python 对象转为 API 要求的 JSON 格式——Schema 定义和 API 调用分离 |
| `GET_WEATHER_TOOL` | 工具定义的黄金标准：`name` + `description`（写给 LLM）+ `input_schema`（JSON Schema 类型系统）。`enum` 约束 + `required` 数组 + `description` 带有示例值 |
| 错误处理对比 | Text-based: `get_weather(**args)` 直接崩；Native: try/except 包裹 + 返回结构化错误 + `received_args` 帮助 LLM 修正 |
| `tool_results` 结构 | `type: "tool_result"` + `tool_use_id`（关联到具体的调用）+ `content`（结果 JSON）——这是 Anthropic API 要求的格式 |

**如何将 Text-based Agent 升级为 Native Function Calling**：

```python
# 之前（ReAct 练习）
action_format = "Action: calculator[127 * 34]"

# 之后（原生 Function Calling）
tool_definition = {
    "name": "calculator",
    "description": "执行数学计算。支持基本运算、sqrt、log、pi。",
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "数学表达式，如 '3 + 5 * 2' 或 'sqrt(34)'",
            }
        },
        "required": ["expression"],
    },
}
# LLM 返回的不再是文本，而是 {"name": "calculator", "input": {"expression": "127 * 34"}}
```

---

## 常见误区

1. **"Native Function Calling 和 Text-based 只是格式不同"** ❌
   根本区别是**可靠性契约**。Text-based 的契约是"LLM 会尽力遵循文本格式"——这是软约束。Native Function Calling 的契约是"API 协议保证返回结构化数据"——这是硬约束。前者有 1-5% 的解析失败率，后者为零。

2. **"Schema 写得越详细越好"** ❌
   Schema 的 description 字段有边际效用递减。超过 3 句话的 description 反而降低准确率——LLM 的注意力被稀释。每个 description 控制在 1-2 句，用示例代替长篇说明。

3. **"工具越多 Agent 越强大"** ❌
   10 个精挑细选、互斥的工具 > 50 个功能重叠的工具。工具选择是分类问题——类别越多准确率越低。50 个工具时选择准确率可能降到 60% 以下。

4. **"工具调用失败让 Agent 自己重试就行"** ❌
   盲目重试浪费 token 且可能进入死循环。好的错误处理是**告诉 LLM 具体哪里错了 + 如何修正**。"参数错误"是不合格的错误消息；"city 参数 '北jing' 不是合法中文城市名，请使用'北京'"是合格的。

---

## 苏格拉底式检验

> 🤔 **问题 1**：你的 ReAct 练习中用的是 Text-based 工具调用。如果要把 `calculator`、`search`、`get_current_time` 升级为 Native Function Calling，哪个工具的 Schema 最难设计？为什么？

> 🤔 **问题 2**：如果用户的请求是"帮我比较一下北京、上海、广州、深圳、杭州、成都、武汉、南京这 8 个城市的天气，找出最凉快的那个"——Agent 应该串行调用 8 次 `get_weather`，还是并行调用？哪种方式会遇到什么工程问题？

---

## 快速总结

- **Text-based vs Native**：Text-based 是正则解析 LLM 文本，有 1-5% 失败率；Native 是 API 协议层结构化返回，零解析失败
- **JSON Schema 是工具定义的工程标准**：`name` + `description`（给 LLM 看）+ `input_schema`（类型约束）。description 控制在 1-2 句，用示例而非长篇说明
- **工具选择是分类问题**：5 个以内 ~95% 准确率，50 个以上 <60%——需要工具检索（RAG 预筛选）
- **多工具编排有四种模式**：串行依赖（最常见）、并行调用（互不依赖）、竞争调用（多选一）、条件分支（LLM 推理驱动）
- **错误处理需要三层防御**：Schema 层（预防）→ 执行层（捕获+结构化错误）→ LLM 层（理解错误+修正重试）

## 下一步

（将在用户选择子话题方向后更新）
