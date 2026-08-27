# Agent 算法研究员

> 0/28 mastered · 0% complete

## Agent 基础架构

- 🔵 **Agent 定义与范式** (in progress)
  - 反应式Agent
  - 模型式Agent
  - 目标驱动Agent
  - 效用驱动Agent
  - BDI模型
- 🔵 **感知-规划-执行循环** (in progress)
  - 环境感知
  - 状态表示
  - 行动空间
  - 反馈闭环
- 🔵 **ReAct 模式** (in progress)
  - Reasoning + Acting交错
  - 思维-行动-观察循环
  - 与纯推理/纯行动对比
- 🔵 **工具使用与 Function Calling** (in progress)
  - 工具定义Schema
  - 工具选择策略
  - 多工具编排
  - 错误处理与重试
- ⚪ **记忆系统设计** (unexplored)
  - 短期记忆/上下文窗口
  - 长期记忆/向量存储
  - 工作记忆
  - 记忆检索与遗忘机制

## 推理与规划

- ⚪ **思维链推理** (unexplored)
  - Zero-shot CoT
  - Few-shot CoT
  - 自一致性采样
  - 逐步验证
- ⚪ **思维树与图推理** (unexplored)
  - BFS/DFS搜索
  - 分支评估
  - 剪枝策略
  - Graph-of-Thoughts
- ⚪ **规划算法** (unexplored)
  - 任务分解
  - 层次规划
  - PDDL
  - 动态重规划
- ⚪ **自我反思与修正** (unexplored)
  - Reflexion框架
  - 自我批评机制
  - 迭代改进
  - 验证与纠错
- ⚪ **多步推理优化** (unexplored)
  - 中间步骤监督
  - 过程奖励模型(PRM)
  - 结果奖励模型(ORM)
  - 搜索预算分配

## 多 Agent 系统

- ⚪ **Agent 通信协议** (unexplored)
  - 消息传递
  - 共享内存
  - 发布订阅
  - ACL/KQML协议
- ⚪ **协作与竞争机制** (unexplored)
  - 合作博弈
  - 零和博弈
  - 混合动机
  - 纳什均衡
- ⚪ **角色分配与任务分解** (unexplored)
  - 专业化分工
  - 动态角色指派
  - 依赖图分析
  - 并行执行调度
- ⚪ **多 Agent 辩论与共识** (unexplored)
  - 多轮辩论
  - 一致性投票
  - 少数派意见聚合
  - 对抗性验证
- ⚪ **群体智能** (unexplored)
  - 涌现行为
  - 蚁群/粒子群优化
  - 分布式感知
  - 自组织

## 工具与代码执行

- ⚪ **Function Calling 机制** (unexplored)
  - OpenAI/Anthropic格式
  - 并行调用
  - 强制调用
  - 流式工具调用
- ⚪ **代码沙箱执行** (unexplored)
  - Docker沙箱
  - WebAssembly
  - 安全隔离
  - 资源限制
- ⚪ **RAG 与检索增强** (unexplored)
  - 向量数据库
  - Embedding模型
  - 混合检索
  - 上下文窗口管理
- ⚪ **动态工具学习** (unexplored)
  - 工具自动发现
  - API文档理解
  - 工具组合合成
  - 在线工具适应

## 评估与安全

- ⚪ **Agent 评估基准** (unexplored)
  - SWE-bench
  - GAIA
  - WebArena
  - AgentBench
  - OSWorld
- ⚪ **安全对齐** (unexplored)
  - RLHF
  - Constitutional AI
  - 红队测试
  - 越狱防御
- ⚪ **奖励模型设计** (unexplored)
  - 偏好标注
  - Bradley-Terry模型
  - DPO
  - 奖励攻击
- ⚪ **鲁棒性与可靠性** (unexplored)
  - 对抗鲁棒性
  - 分布外泛化
  - 幻觉检测
  - 故障恢复

## 前沿研究方向

- ⚪ **自主 Agent 架构** (unexplored)
  - AutoGPT
  - BabyAGI
  - MetaGPT
  - CrewAI
- ⚪ **世界模型** (unexplored)
  - 环境动态建模
  - 反事实推理
  - Dreamer系列
  - Sora/视频世界模型
- ⚪ **Computer Use 与 GUI Agent** (unexplored)
  - 桌面自动化
  - 屏幕理解
  - 操作定位
  - 跨应用编排
- ⚪ **长期自主与持续学习** (unexplored)
  - 终身学习
  - 灾难性遗忘
  - 经验回放
  - 课程学习
- ⚪ **具身智能** (unexplored)
  - 感知-行动耦合
  - 仿真到现实迁移
  - 操作与导航
  - 人机交互
