# Tasks

- [x] Task 1: 后端需求收集模块实现
  - [x] SubTask 1.1: 创建 `backend/requirement_collector.py`，实现 `RequirementCollector` 类
  - [x] SubTask 1.2: 实现会话状态管理（session_id、轮次计数、需求摘要、对话历史）
  - [x] SubTask 1.3: 实现主动询问 prompt 设计（根据轮次生成不同侧重点的追问）
  - [x] SubTask 1.4: 实现需求摘要生成（从对话历史中提取关键需求信息）
  - [x] SubTask 1.5: 实现对话阶段判断逻辑（需求收集/检索就绪）

- [x] Task 2: 后端对话端点改造
  - [x] SubTask 2.1: 修改 `ConversationRequest` 模型，增加 `session_id` 字段
  - [x] SubTask 2.2: 修改 `/api/conversation` 端点，集成 `RequirementCollector`
  - [x] SubTask 2.3: 新增 `/api/conversation/stream` 流式对话端点
  - [x] SubTask 2.4: 修改 `/api/search/stream` 和 `/api/report/stream`，支持 `requirement_summary` 参数
  - [x] SubTask 2.5: 在对话端点返回中增加 `round_count`、`ready_for_search`、`requirement_summary` 字段

- [x] Task 3: 前端对话交互流程改造
  - [x] SubTask 3.1: 在 `api/client.js` 新增 `conversationStream()` 方法
  - [x] SubTask 3.2: 修改 `api/client.js` 的检索/综述方法，支持传入 `requirement_summary`
  - [x] SubTask 3.3: 在 `App.jsx` 新增对话阶段状态管理（conversationPhase、sessionId、roundCount、requirementSummary）
  - [x] SubTask 3.4: 修改 `App.jsx` 的 `handleSend` 逻辑，需求收集阶段调用对话端点而非检索端点
  - [x] SubTask 3.5: 实现对话阶段到检索阶段的切换逻辑
  - [x] SubTask 3.6: 在 `ChatMessage.jsx` 中支持显示"开始检索"按钮
  - [x] SubTask 3.7: 实现"开始检索"按钮点击后使用需求摘要触发检索的流程

- [x] Task 4: 端到端测试与调试
  - [x] SubTask 4.1: 测试多轮对话流程（3 轮追问后显示检索按钮）
  - [x] SubTask 4.2: 测试流式对话输出
  - [x] SubTask 4.3: 测试从对话切换到检索的完整流程
  - [x] SubTask 4.4: 测试用户提前触发检索的场景

# Task Dependencies
- Task 2 依赖 Task 1
- Task 3 依赖 Task 2
- Task 4 依赖 Task 1、Task 2、Task 3
