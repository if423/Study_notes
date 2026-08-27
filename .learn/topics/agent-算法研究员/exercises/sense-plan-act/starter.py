"""
SPA 循环练习 — 探矿 Agent
===========================
完成 5 个 # TODO，实现 Sense→Plan→Act→反馈闭环。

运行: python starter.py
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field


# ============================================================
# 环境：5×5 矿区（只读 —— 不要修改）
# ============================================================
@dataclass
class GoldMine:
    """
    5×5 矿区。每个格子: 0=空地, 1=金矿。
    Agent 只能看到曼哈顿距离 ≤1 的格子。
    """

    size: int = 5
    grid: list[list[int]] = field(default_factory=list)
    agent_pos: tuple[int, int] = (2, 2)
    energy: int = 30
    gold_collected: int = 0
    total_gold: int = 0

    def __post_init__(self):
        if not self.grid:
            # 随机生成 6-8 个金矿
            cells = [(r, c) for r in range(5) for c in range(5)]
            random.shuffle(cells)
            num_gold = random.randint(6, 8)
            self.grid = [[0] * 5 for _ in range(5)]
            for i in range(num_gold):
                r, c = cells[i]
                self.grid[r][c] = 1
            self.total_gold = num_gold
            # 起点不能有金矿
            self.grid[2][2] = 0

    def perceive(self) -> dict:
        """返回 Agent 视野内的信息（曼哈顿距离 ≤ 1 的格子）"""
        r, c = self.agent_pos
        visible = {}
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.size and 0 <= nc < self.size:
                    visible[(nr, nc)] = self.grid[nr][nc]
        return {
            "position": self.agent_pos,
            "visible": visible,
            "energy": self.energy,
        }

    def move(self, direction: str) -> bool:
        """移动 Agent，消耗 1 能量。返回是否成功。"""
        if self.energy <= 0:
            return False
        r, c = self.agent_pos
        moves = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}
        if direction in moves:
            dr, dc = moves[direction]
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                self.agent_pos = (nr, nc)
                self.energy -= 1
                return True
        return False

    def collect_gold(self) -> bool:
        """采集当前位置的金矿。消耗 1 能量。返回是否成功。"""
        if self.energy <= 0:
            return False
        r, c = self.agent_pos
        if self.grid[r][c] == 1:
            self.grid[r][c] = 0
            self.gold_collected += 1
            self.energy -= 1
            return True
        return False

    def all_gold_found(self) -> bool:
        """是否已采集所有金矿"""
        return self.gold_collected >= self.total_gold


# ============================================================
# SPA Agent 基类
# ============================================================
class SPAAgent(ABC):
    """SPA Agent —— 子类只需实现 sense / plan / act"""

    def __init__(self, name: str):
        self.name = name
        self.env: GoldMine | None = None
        self.known_map: list[list[int]] = []
        self.history: list[dict] = []
        self.steps: int = 0

    def bind(self, env: GoldMine):
        self.env = env
        self.known_map = [[-1] * env.size for _ in range(env.size)]

    # ============================================================
    # TODO 1: Sense —— 感知 + 状态估计
    # ============================================================
    def sense(self) -> dict:
        """
        从环境获取感知，生成完整的状态估计。

        必须包含:
        - position: 当前位置
        - known_map: 更新的已知地图（-1=未知, 0=空地, 1=金矿）
        - visible: 当前视野
        - energy: 剩余能量
        - gold_collected: 已采集金矿数

        关键: 用 percept["visible"] 更新 self.known_map，而非直接读 env.grid。
              只有视野内的格子才能更新（部分可观测性）。
        """
        percept = self.env.perceive()

        # TODO 1: 用 percept["visible"] 更新 self.known_map
        # 对 visible 中的每个 (r,c) → state，更新 known_map[r][c] = state

        self.steps += 1

        for (r, c), state in percept["visible"].items():
            self.known_map[r][c] = state

        return {
            "position": percept["position"],
            "known_map": [row.copy() for row in self.known_map],
            "visible": percept["visible"],
            "energy": percept["energy"],
            "gold_collected": self.env.gold_collected,
        }

    # ============================================================
    # TODO 2: Plan（反应式）—— 最简单的规划策略
    # ============================================================
    def plan_reactive(self, state: dict) -> str:
        """
        反应式规划：IF 条件 THEN 行动，不搜索、不前瞻。

        规则:
        1. 如果脚下有金矿 → "collect"
        2. 如果相邻格有已知金矿 → 移过去
        3. 如果相邻格有未知格子（-1）→ 移过去探索
        4. 都没有 → 随机走一个合法方向
        5. 能量 ≤ 2 → "stop"（安全终止）

        返回: "collect" | "up" | "down" | "left" | "right" | "stop"
        """
        # TODO 2: 实现反应式规划

        if state["energy"] <= 2:
            return "stop"

        r, c = state["position"]

        if self.known_map[r][c] == 1:
            return "collect"

        moves = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}
        for action, move in moves.items():
            dr, dc = move
            nr, nc = r + dr, c + dc
            moves[action] = (nr, nc)

        for action, move in moves.items():
            if (
                0 <= move[0] < 5
                and 0 <= move[1] < 5
                and self.known_map[move[0]][move[1]] == 1
            ):
                return action

        for action, move in moves.items():
            if (
                0 <= move[0] < 5
                and 0 <= move[1] < 5
                and self.known_map[move[0]][move[1]] == -1
            ):
                return action

        valid = []
        for action, move in moves.items():
            if move in state["visible"] and state["visible"][move] != -1:
                valid.append(action)
        return random.choice(valid) if valid else "stop"

    # ============================================================
    # TODO 3: Plan（效用驱动）—— 多维打分选最优
    # ============================================================
    def plan_utility(self, state: dict) -> str:
        """
        效用驱动规划：对每个候选行动计算多维效用，选最高分。

        候选行动: "collect" + 四个合法移动方向

        效用维度（加权求和，总和 0~1）:
        - gold_proximity (权重 0.5):  距最近已知金矿的距离 → 1/(1+dist)
                                       无已知金矿 → 0
        - explore_value  (权重 0.3):  距最近未知格子的距离 → 1/(1+dist)
                                       无未知格子 → 0
        - energy_cost    (权重 0.2):  移动 = 0.0（多远都得走）
                                      采集 = 1.0（立即收益）
                                      能量 ≤ 3 时权重翻倍（保守）

        能量 ≤ 2 → 强制返回 "stop"

        返回: "collect" | "up" | "down" | "left" | "right" | "stop"
        """
        # TODO 3: 实现效用驱动规划

        if state["energy"] <= 2:
            return "stop"

        total_utility = {}
        r, c = state["position"]
        moves = {
            "up": (-1, 0),
            "down": (1, 0),
            "left": (0, -1),
            "right": (0, 1),
            "collect": (0, 0),
        }

        for action, (dr, dc) in moves.items():
            nr, nc = r + dr, c + dc
            gold_proximity = explore_value = 0

            targets = [
                (i, j)
                for i, states in enumerate(self.known_map)
                for j, state in enumerate(states)
                if state == 1
            ]
            for tr, tc in targets:
                dist = abs(nr - tr) + abs(nc - tc)
                util = 1 / (1 + dist)
                gold_proximity = max(gold_proximity, util)

            targets = [
                (i, j)
                for i, states in enumerate(self.known_map)
                for j, state in enumerate(states)
                if state == -1
            ]
            for tr, tc in targets:
                dist = abs(nr - tr) + abs(nc - tc)
                util = 1 / (1 + dist)
                explore_value = max(explore_value, util)

            energy_cost = 1 if action == "collect" else 0
            if state["energy"] <= 3:
                energy_cost *= 2

            total_utility[action] = (
                gold_proximity * 0.5 + explore_value * 0.3 + energy_cost * 0.2
            )

        act = "collect"
        for action, utility in total_utility.items():
            act = act if total_utility[act] > utility else action

        return act

    # ============================================================
    # TODO 4: Act —— 执行行动 + 返回预期效果
    # ============================================================
    def act(self, action: str, state: dict) -> dict:
        """
        执行行动，返回执行结果和**预期效果**。

        预期效果用于反馈闭环——run() 中与实际感知对比。

        返回结构:
        {
            "action": str,           # 执行的行动
            "success": bool,         # 行动是否成功
            "expected_position": tuple,  # 预计执行后的位置
            "gold_collected_this_step": int,  # 这一步采了多少金矿
        }
        """
        # TODO 4: 执行行动并返回预期效果

        success = False
        r, c = state["position"]
        if action in ["up", "down", "left", "right"]:
            moves = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}
            success = self.env.move(action)
            if success:
                r, c = (r + moves[action][0], c + moves[action][1])
        elif action in ["collect"]:
            success = self.env.collect_gold()
        elif action in ["stop"]:
            success = True

        return {
            "action": action,
            "success": success,
            "expected_position": (r, c),
            "gold_collected_this_step": 1 if (action == "collect" and success) else 0,
        }

    # ============================================================
    # TODO 5: SPA 主循环 —— Sense→Plan→Act→反馈闭环
    # ============================================================
    def run(
        self, env: GoldMine, strategy: str = "reactive", max_steps: int = 50
    ) -> dict:
        """
        SPA 主循环。

        参数:
            env: 环境
            strategy: "reactive" 或 "utility"
            max_steps: 最大步数

        循环逻辑（每个迭代）:
        1. Sense: 调用 self.sense() → state
        2. Plan: 根据 strategy 选择 self.plan_reactive(state) 或 self.plan_utility(state)
        3. Act:  调用 self.act(action, state) → outcome
        4. ★ 反馈闭环 ★: 重新感知 → 对比预期 vs 实际
           - 如果位置 != 预期 → 记录异常（被墙挡？）
           - 如果脚下金矿状态 != 预期 → 更新 known_map（金矿已消失？）
        5. 记录到 history
        6. 终止条件: action == "stop" 或 gold_collected == total_gold 或 steps >= max_steps

        返回:
        {
            "steps": int,
            "gold_collected": int,
            "total_gold": int,
            "energy_left": int,
            "anomalies": int,       # 反馈闭环检测到的异常次数
            "history": [...],
        }
        """
        # TODO 5: 实现 SPA 主循环

        self.bind(env)
        action = ""
        gold_collected = 0
        anomalies = 0
        state = self.sense()

        while (
            action != "stop"
            and gold_collected != self.env.total_gold
            and self.steps < max_steps
        ):

            if strategy == "reactive":
                action = self.plan_reactive(state)
            elif strategy == "utility":
                action = self.plan_utility(state)

            outcome = self.act(action, state)
            if action == "collect":
                gold_collected += 1
            state = self.sense()

            # if state["position"] != outcome["expected_position"]:
            #     anomalies += 1

            if outcome["gold_collected_this_step"] == 1:
                r, c = state["position"]
                if state["known_map"][r][c] == 1:
                    self.known_map[r][c] = 0

            self.history.append(outcome)

        return {
            "steps": self.steps,
            "gold_collected": gold_collected,
            "total_gold": self.env.total_gold,
            "energy_left": state["energy"],
            "anomalies": anomalies,
            "history": self.history,
        }


# ============================================================
# 测试套件（不要修改）
# ============================================================
def test_agent(strategy: str, seed: int = 42):
    """运行单个 Agent 并评估"""
    random.seed(seed)
    env = GoldMine()
    total = env.total_gold

    agent = SPAAgent(f"SPA-{strategy}")
    result = agent.run(env, strategy=strategy)

    efficiency = result["gold_collected"] / max(result["steps"], 1)
    icon = "[OK]" if result["gold_collected"] >= total // 2 else "[FAIL]"

    print(
        f"  {icon} {strategy:12s} | "
        f"金矿: {result['gold_collected']}/{total} | "
        f"步数: {result['steps']} | "
        f"能量: {result['energy_left']} | "
        f"异常: {result['anomalies']} | "
        f"效率: {efficiency:.2f}"
    )

    # 反馈闭环必须检测到至少 0 次异常（没有异常也是合理的）
    return result["gold_collected"] >= total // 2


if __name__ == "__main__":
    print("=" * 70)
    print("  SPA 循环 — 探矿 Agent 测试")
    print("=" * 70)

    passed = 0
    for strategy in ["reactive", "utility"]:
        if test_agent(strategy):
            passed += 1
    # 多跑一次不同随机种子
    print("  --- 随机种子 123 ---")
    for strategy in ["reactive", "utility"]:
        if test_agent(strategy, seed=123):
            passed += 1

    print("\n" + "=" * 70)
    print(f"  总结: {passed}/4 次测试通过 (≥50% 金矿采集率)")
    print("=" * 70)

    if passed < 4:
        print("\n💡 提示: 检查你的 5 个 TODO 实现。")
        print("   重点排查: 反馈闭环是否正确对比了预期 vs 实际？")
