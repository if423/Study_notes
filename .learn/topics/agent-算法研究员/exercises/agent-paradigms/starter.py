"""
Agent 五大范式练习 — 网格世界清洁 Agent
============================================
完成 5 个 # TODO，实现五种 Agent 范式。

运行: python starter.py
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
import random


# ============================================================
# 环境：3×3 网格世界（只读——不要修改）
# ============================================================
@dataclass
class GridWorld:
    """
    3×3 网格，每个格子: 0=干净, 1=脏
    Agent 从 (0,0) 出发，只能看到相邻 4 格（上下左右）。
    """

    size: int = 3
    grid: list[list[int]] = field(default_factory=list)
    agent_pos: tuple[int, int] = (0, 0)
    steps: int = 0

    def __post_init__(self):
        if not self.grid:
            self.grid = [
                [0, 1, 0],
                [1, 0, 1],
                [0, 1, 0],
            ]

    def perceive(self) -> dict:
        """返回 Agent 当前位置 + 相邻 4 格的状态（-1 = 越界）"""
        r, c = self.agent_pos
        neighbors = {}
        for dr, dc, name in [
            (-1, 0, "up"),
            (1, 0, "down"),
            (0, -1, "left"),
            (0, 1, "right"),
        ]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                neighbors[name] = self.grid[nr][nc]
            else:
                neighbors[name] = -1
        return {"position": self.agent_pos, "neighbors": neighbors}

    def clean_current(self):
        """清扫当前位置"""
        r, c = self.agent_pos
        self.grid[r][c] = 0

    def move(self, direction: str) -> bool:
        """移动 Agent，返回是否成功"""
        r, c = self.agent_pos
        moves = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}
        if direction in moves:
            dr, dc = moves[direction]
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                self.agent_pos = (nr, nc)
                self.steps += 1
                return True
        return False

    def all_clean(self) -> bool:
        """检查是否所有格子都干净了"""
        return all(cell == 0 for row in self.grid for cell in row)

    def dirty_positions(self) -> list[tuple[int, int]]:
        """返回所有脏格子的位置"""
        return [
            (r, c)
            for r in range(self.size)
            for c in range(self.size)
            if self.grid[r][c] == 1
        ]


# ============================================================
# Agent 基类（提供通用工具方法）
# ============================================================
class CleanerAgent(ABC):
    """清洁 Agent 基类——子类只需实现 decide()"""

    def __init__(self, name: str):
        self.name = name
        self.env: GridWorld | None = None

    def bind(self, env: GridWorld):
        self.env = env

    @abstractmethod
    def decide(self, percept: dict) -> str:
        """
        根据感知决定行动。
        返回: "clean" | "up" | "down" | "left" | "right" | "wait"
        """
        ...

    def run(self, env: GridWorld, max_steps: int = 50) -> int:
        """运行 Agent 直到完成或达到最大步数（不要修改此方法）"""
        self.bind(env)
        for _ in range(max_steps):
            if env.all_clean():
                break
            percept = env.perceive()
            action = self.decide(percept)
            if action == "clean":
                env.clean_current()
            elif action in ("up", "down", "left", "right"):
                env.move(action)
            # "wait" = 什么都不做
        return env.steps


# ============================================================
# TODO 1: 反应式清洁 Agent
# ============================================================
class ReactiveCleaner(CleanerAgent):
    """
    纯反应式：仅基于当前感知做 IF-THEN 决策。
    无记忆、无规划、不维护任何内部状态。

    规则：感知到相邻有脏格子 → 移过去清扫；都没有 → 随机移动
    """

    def __init__(self):
        super().__init__("Reactive")

    def decide(self, percept: dict) -> str:
        neighbors = percept["neighbors"]

        # TODO 1: 实现反应式逻辑
        # 1. 如果当前位置是脏的 → "clean"
        # 2. 如果相邻有脏格子 → 移动到第一个脏格子的方向
        # 3. 都没有 → 随机选一个方向移动
        #
        # 提示: neighbors 是 {"up": 0|1|-1, "down": ..., "left": ..., "right": ...}
        #       0=干净, 1=脏, -1=越界

        return (
            "clean"
            if self.env.grid[percept["position"][0]][percept["position"][1]] == 1
            else (
                next((k for k, v in neighbors.items() if v == 1), None)
                if 1 in neighbors.values()
                else random.choice([k for k, v in neighbors.items() if v != -1])
            )
        )  # ← 替换为你的实现


# ============================================================
# TODO 2: 模型式清洁 Agent
# ============================================================
class ModelBasedCleaner(CleanerAgent):
    """
    模型式：维护一个内部地图模型（belief_map）。
    对未观测区域做默认假设，结合感知和模型共同决策。

    关键特征：模型"补全"未感知到的信息。
    """

    def __init__(self):
        super().__init__("ModelBased")
        # 内部地图: -1=未知, 0=干净, 1=脏
        self.belief_map: list[list[int]] = [[-1] * 3 for _ in range(3)]

    def update_belief(self, percept: dict):
        """更新信念地图（已实现）"""
        r, c = percept["position"]
        self.belief_map[r][c] = self.env.grid[r][c]  # 当前位置已知
        for direction, state in percept["neighbors"].items():
            dr, dc = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}[
                direction
            ]
            nr, nc = r + dr, c + dc
            if state != -1:
                self.belief_map[nr][nc] = state

    def decide(self, percept: dict) -> str:
        self.update_belief(percept)
        r, c = percept["position"]

        # TODO 2: 实现模型式逻辑
        # 1. 如果当前位置在 belief 中是脏的 → "clean"
        # 2. 如果相邻有已知的脏格子 → 移过去
        # 3. 如果相邻有未知格子（-1）→ 去探索（默认假设策略）
        # 4. 都没有 → 随机移动
        #
        # 提示: 用 self.belief_map 查询任意格子的状态

        if self.belief_map[r][c] == 1:
            return "clean"
        for direction, dr, dc in {
            ("up", -1, 0),
            ("down", 1, 0),
            ("left", 0, -1),
            ("right", 0, 1),
        }:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 3 and 0 <= nc < 3 and self.belief_map[nr][nc] == 1:
                return direction
        for direction, dr, dc in {
            ("up", -1, 0),
            ("down", 1, 0),
            ("left", 0, -1),
            ("right", 0, 1),
        }:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 3 and 0 <= nc < 3 and self.belief_map[nr][nc] == -1:
                return direction
        valid = []
        for direction, (dr, dc) in [
            ("up", (-1, 0)),
            ("down", (1, 0)),
            ("left", (0, -1)),
            ("right", (0, 1)),
        ]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                valid.append(direction)
        return random.choice(valid) if valid else "wait"

        # ← 替换为你的实现


# ============================================================
# TODO 3: 目标驱动清洁 Agent
# ============================================================
class GoalBasedCleaner(CleanerAgent):
    """
    目标驱动：使用 BFS 搜索从当前位置到最近脏格子的最短路径。

    关键特征：会"向前看"规划多步行动序列。
    """

    def __init__(self):
        super().__init__("GoalBased")
        self.known_dirty: set = set()  # 已知脏格子集合
        self.visited: set = set()  # 已访问过的格子
        self.plan: list[str] = []  # 当前行动计划

    def update_knowledge(self, percept: dict):
        """更新已知信息（已实现）"""
        r, c = percept["position"]
        self.visited.add((r, c))
        for direction, state in percept["neighbors"].items():
            dr, dc = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}[
                direction
            ]
            nr, nc = r + dr, c + dc
            if state == 1:
                self.known_dirty.add((nr, nc))

    def bfs_plan(self, start: tuple, targets: set) -> list[str]:
        """
        BFS 搜索从 start 到最近 target 的最短路径。
        返回行动序列（字符串列表），如 ["right", "down", "clean"]。
        如果没有可达的 target → 返回探索未访问格子的路径。
        """
        # TODO 3a: 实现 BFS 搜索
        # 1. 如果 targets 非空 → 搜索到最近目标的路径
        # 2. 如果 targets 为空 → 搜索到最近未访问格子的路径
        # 3. 返回行动序列（第一步是移动方向，最后一步是 "clean"）
        #
        # 提示:
        #   queue = deque([(start, [])])
        #   合法移动: up/down/left/right（不越界）
        #   如果目标是脏格子 → 到达相邻格后追加 "clean"

        queue = deque([(start, [])])
        visited = set(start)
        cur, path = (), []

        while queue:
            cur, path = queue.popleft()

            if cur in targets:
                self.plan = path
                self.plan.append("clean")
                return self.plan

            if not targets and cur not in self.visited:
                self.plan = path
                return self.plan

            for direction, (dr, dc) in [
                ("up", (-1, 0)),
                ("down", (1, 0)),
                ("left", (0, -1)),
                ("right", (0, 1)),
            ]:
                nr, nc = cur[0] + dr, cur[1] + dc
                if 0 <= nr < 3 and 0 <= nc < 3 and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append(((nr, nc), path + [direction]))
        # ← 替换为你的实现

    def decide(self, percept: dict) -> str:
        self.update_knowledge(percept)

        # TODO 3b: 实现 decide 逻辑
        # 1. 如果当前位置是脏的 → "clean" 并从 known_dirty 移除
        # 2. 如果 plan 非空 → 返回 plan 的下一个行动
        # 3. 否则调用 bfs_plan 生成新计划
        # 4. 如果计划为空 → 随机移动探索

        if self.env.grid[percept["position"][0]][percept["position"][1]] == 1:
            self.known_dirty.discard((percept["position"][0], percept["position"][1]))
            # return "clean"
        if self.plan != []:
            plan = self.plan[0]
            self.plan.pop(0)
            return plan
        else:
            self.bfs_plan(percept["position"], self.known_dirty)
            if self.plan == []:
                valid = []
                for direction, state in percept["neighbors"].items():
                    if state != -1:
                        valid.append(direction)
                return random.choice(valid) if valid else "wait"

        # ← 替换为你的实现


# ============================================================
# TODO 4: 效用驱动清洁 Agent
# ============================================================
class UtilityBasedCleaner(CleanerAgent):
    """
    效用驱动：不是找"能到的"路径，而是用多维效用函数选"最优"行动。

    效用维度：
      - 清洁效用：行动能否直接清扫脏格子（权重 0.5）
      - 距离效用：是否接近已知脏格子（权重 0.3）
      - 探索效用：是否探索未知区域（权重 0.2）

    关键特征：处理目标冲突——通过加权打分做出折中。
    """

    def __init__(self):
        super().__init__("UtilityBased")
        self.known_map: list[list[int]] = [[-1] * 3 for _ in range(3)]
        self.visited: set = set()

    def update_map(self, percept: dict):
        """更新已知地图（已实现）"""
        r, c = percept["position"]
        self.visited.add((r, c))
        self.known_map[r][c] = self.env.grid[r][c]
        for direction, state in percept["neighbors"].items():
            dr, dc = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}[
                direction
            ]
            nr, nc = r + dr, c + dc
            if state != -1:
                self.known_map[nr][nc] = state

    def utility(self, action: str, percept: dict) -> float:
        """
        计算某个行动的总效用（0~1）。

        三个维度加权求和：
          clean_utility:  行动 = "clean" 且当前位置脏 → 1.0
          dirty_proximity: 移动后离已知脏格子更近 → 高
          explore_utility: 移动后进入未访问/未知区域 → 高

        权重: clean=0.5, proximity=0.3, explore=0.2
        """
        # TODO 4a: 实现效用函数
        # 1. 如果 action == "clean" → 清洁效用（当前位置是否脏）
        # 2. 如果 action 是移动方向 → 计算移动后的三个效用并加权求和
        # 3. 返回总分
        #
        # 提示: 用曼哈顿距离衡量"接近"程度:
        #   dist = abs(r - target_r) + abs(c - target_c)
        #   距离效用 = 1 / (1 + dist)  （越近越高）

        total_utility = 0
        r, c = percept["position"]
        dr, dc = {
            "up": (-1, 0),
            "down": (1, 0),
            "left": (0, -1),
            "right": (0, 1),
            "clean": (0, 0),
        }[action]
        nr, nc = r + dr, c + dc

        clean_utility = 1 if self.known_map[r][c] == 1 and action == "clean" else 0

        dirty_proximity = explore_utility = 0
        if action != "clean":
            targets = [
                (i, j)
                for i, states in enumerate(self.known_map)
                for j, state in enumerate(states)
                if state == 1
            ]
            for tr, tc in targets:
                dist = abs(nr - tr) + abs(nc - tc)
                util = 1 / (1 + dist)
                dirty_proximity = max(dirty_proximity, util)

            targets = [
                (i, j)
                for i, states in enumerate(self.known_map)
                for j, state in enumerate(states)
                if state == -1
            ]
            for tr, tc in targets:
                dist = abs(nr - tr) + abs(nc - tc)
                util = 1 / (1 + dist)
                explore_utility = max(explore_utility, util)

        total_utility = (
            clean_utility * 0.5 + dirty_proximity * 0.3 + explore_utility * 0.2
        )

        return total_utility

        # ← 替换为你的实现

    def decide(self, percept: dict) -> str:
        self.update_map(percept)

        # TODO 4b: 实现决策逻辑
        # 1. 候选行动: "clean" + 四个合法移动方向
        # 2. 对每个候选行动调用 self.utility() 打分
        # 3. 选择效用最高的行动

        candidates = {"clean": 0, "up": 0, "down": 0, "left": 0, "right": 0}

        for direction, (dr, dc) in [
            ("up", (-1, 0)),
            ("down", (1, 0)),
            ("left", (0, -1)),
            ("right", (0, 1)),
        ]:
            nr, nc = percept["position"][0] + dr, percept["position"][1] + dc
            if not 0 <= nr < 3 or not 0 <= nc < 3:
                del candidates[direction]

        for direction in candidates:
            candidates[direction] = self.utility(direction, percept)

        return max(candidates, key=candidates.get)

        # ← 替换为你的实现


# ============================================================
# TODO 5: BDI 清洁 Agent
# ============================================================
class BDICleaner(CleanerAgent):
    """
    BDI Agent：
      Belief  — 对世界地图的认知（可能不完整）
      Desire  — 希望所有格子都干净
      Intention — 承诺清扫当前目标脏格子（有持续性）

    关键特征：
      - Intention 持续性：一旦承诺清扫某个脏格子，坚持执行到完成
      - Intention 重考虑：如果发现更近的脏格子 → 评估是否切换意图
    """

    def __init__(self):
        super().__init__("BDI")
        # Belief: 已知的地图状态
        self.belief_map: list[list[int]] = [[-1] * 3 for _ in range(3)]
        # Intention: 当前承诺清扫的格子 (r, c)，None 表示无承诺
        self.intention: tuple[int, int] | None = None
        # 探索记录
        self.visited: set = set()

    def belief_revision(self, percept: dict):
        """Belief Revision Function — 根据感知修正信念（已实现）"""
        r, c = percept["position"]
        self.visited.add((r, c))
        self.belief_map[r][c] = self.env.grid[r][c]
        for direction, state in percept["neighbors"].items():
            dr, dc = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}[
                direction
            ]
            nr, nc = r + dr, c + dc
            if state != -1:
                self.belief_map[nr][nc] = state

    def generate_options(self) -> list[tuple[int, int]]:
        """根据 Belief + Desire 生成可选目标（已实现）"""
        options = []
        for r in range(3):
            for c in range(3):
                if self.belief_map[r][c] == 1:  # 已知的脏格子
                    options.append((r, c))
        return options

    def reconsider(
        self, new_options: list[tuple[int, int]], current_pos: tuple
    ) -> bool:
        """
        意图重考虑：是否应该放弃当前 Intention，切换到新目标？

        规则：
        - 如果当前 Intention 对应格子已经不在 options 中（已干净）→ 必须重考虑 (True)
        - 如果存在一个距离 < 当前 Intention 距离一半的新目标 → 重考虑 (True)
        - 否则 → 保持当前 Intention (False)
        """
        # TODO 5a: 实现意图重考虑逻辑
        # 1. 如果 self.intention 为 None → True（需要新意图）
        # 2. 如果 self.intention 不在 options 中 → True（目标已达）
        # 3. 计算当前意图距离 vs 最近新选项距离
        #    如果最近新选项距离 < 当前意图距离/2 → True
        # 4. 否则 → False（保持当前意图）

        if self.intention is None or self.intention not in new_options:
            return True

        r, c = current_pos
        if new_options != []:
            option = new_options[0]
            for tr, tc in new_options:
                if abs(r - option[0]) + abs(c - option[1]) > abs(r - tr) + abs(c - tc):
                    option = (tr, tc)
            if (
                abs(r - option[0]) + abs(c - option[1])
                < abs(r - self.intention[0]) + abs(c - self.intention[1]) >> 1
            ):
                return True
        return False

        # ← 替换为你的实现

    def decide(self, percept: dict) -> str:
        self.belief_revision(percept)
        pos = percept["position"]
        r, c = pos

        # TODO 5b: 实现 BDI 决策逻辑
        # 1. 如果当前位置是脏的 → "clean"
        # 2. generate_options() → 获取所有已知脏格子
        # 3. reconsider() → 判断是否需要切换意图
        #    如果需要 → 选择最近的新目标作为 Intention
        # 4. 根据 Intention 选择移动方向（朝目标走一步）
        # 5. 如果没有 Intention 且没有脏格子 → 探索未知/未访问区域
        #
        # 提示: 朝目标 (tr, tc) 移动时，比较 |r-tr| 和 |c-tc| 决定先走哪个方向

        if self.belief_map[r][c] == 1:
            return "clean"

        tr, tc = float("inf"), float("inf")
        options = self.generate_options()
        if self.reconsider(options, pos):
            for option in options:
                if abs(r - option[0]) + abs(c - option[1]) < abs(r - tr) + abs(c - tc):
                    tr, tc = min(options, key=lambda o: abs(r - o[0]) + abs(c - o[1]))

            self.intention = (tr, tc)

        if self.intention is not None:
            tr, tc = self.intention
        else:
            unknown = [
                (i, j)
                for i in range(3)
                for j in range(3)
                if self.belief_map[i][j] == -1
            ]
            if unknown:
                tr, tc = unknown[0]
            else:
                valid = [d for d, s in percept["neighbors"].items() if s != -1]
                return random.choice(valid) if valid else "wait"

        if abs(r - tr) > abs(c - tc):
            return "up" if r - tr > 0 else "down"
        else:
            return "left" if c - tc > 0 else "right"

        # ← 替换为你的实现


# ============================================================
# 测试框架（不要修改）
# ============================================================
def test_agent(agent_class, name: str):
    """运行单个 Agent 并输出结果"""
    env = GridWorld()
    agent = agent_class()
    steps = agent.run(env)
    all_clean = env.all_clean()
    icon = "[OK]" if all_clean else "[FAIL]"
    print(f"  {icon} {name}: {steps} steps, all_clean={all_clean}")
    return all_clean, steps


if __name__ == "__main__":
    print("=" * 55)
    print("  Agent 五大范式 — 网格世界清洁 Agent 测试")
    print("=" * 55)

    agents = [
        (ReactiveCleaner, "Reactive（反应式）"),
        (ModelBasedCleaner, "ModelBased（模型式）"),
        (GoalBasedCleaner, "GoalBased（目标驱动）"),
        (UtilityBasedCleaner, "UtilityBased（效用驱动）"),
        (BDICleaner, "BDI"),
    ]

    results = []
    for agent_class, name in agents:
        results.append(test_agent(agent_class, name))

    print("\n" + "=" * 55)
    passed = sum(1 for ok, _ in results if ok)
    print(f"  总结: {passed}/{len(results)} 个 Agent 完成清扫任务")
    print("=" * 55)

    if passed < 5:
        print("\n💡 提示: 检查你的 # TODO 实现，确保每个 Agent 都能独立完成任务。")
