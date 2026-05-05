# 论文检索前多轮对话交互 Spec

## Why
当前系统在用户输入查询后立即执行论文检索或综述生成，缺乏对用户需求的深入理解。通过在检索前增加至少三轮主动询问对话，系统可以更精准地把握用户的研究方向、关注点、时间范围等需求，从而提升检索结果和综述报告的质量与相关性。

## What Changes
- 后端新增会话状态管理机制，跟踪对话轮次和收集到的需求信息
- 后端新增 LLM 驱动的主动询问模块，根据已有对话内容生成追问
- 后端修改 `/api/conversation` 端点，增加对话阶段判断逻辑（需求收集阶段 vs 检索执行阶段）
- 后端新增 `/api/conversation/stream` 流式对话端点
- 前端修改交互流程，在需求收集阶段显示对话而非直接触发检索
- 前端新增"开始检索"按钮，在三轮对话后允许用户确认执行检索
- 前端支持流式显示助手追问内容

## Impact
- Affected specs: 论文检索流程、综述生成流程、对话交互流程
- Affected code:
  - `backend/main.py` — 修改对话端点，新增会话管理
  - `backend/requirement_collector.py` — 新增需求收集与主动询问模块
  - `frontend/src/App.jsx` — 修改交互流程，增加对话阶段状态管理
  - `frontend/src/api/client.js` — 新增对话 API 调用方法
  - `frontend/src/components/ChatInput.jsx` — 增加"开始检索"按钮

## ADDED Requirements

### Requirement: 会话状态管理
系统 SHALL 维护每个用户的对话会话状态，包括对话轮次计数、已收集的需求信息摘要、当前对话阶段（需求收集/检索就绪/检索执行）。

#### Scenario: 新会话创建
- **WHEN** 用户发送第一条消息
- **THEN** 系统创建新会话，初始化轮次计数为 1，阶段设为"需求收集"

#### Scenario: 对话轮次递增
- **WHEN** 用户在需求收集阶段发送消息
- **THEN** 系统递增对话轮次计数，更新已收集的需求信息

#### Scenario: 达到最低轮次
- **WHEN** 对话轮次达到 3 轮
- **THEN** 系统将阶段切换为"检索就绪"，在回复中附带 `ready_for_search: true` 标志

### Requirement: LLM 驱动的主动询问
系统 SHALL 使用 LLM 根据已有对话内容生成针对性的追问，主动了解用户的研究方向、关注的技术方法、时间范围偏好、应用场景等需求细节。

#### Scenario: 第一轮追问
- **WHEN** 用户发送第一条消息（如"我想了解深度学习"）
- **THEN** 系统使用 LLM 生成追问，询问更具体的研究方向（如"您对深度学习的哪个具体方向感兴趣？是计算机视觉、自然语言处理还是其他领域？"）

#### Scenario: 后续追问
- **WHEN** 用户回复追问后仍未达到 3 轮
- **THEN** 系统继续生成追问，逐步细化需求（如时间范围、关注的方法论、应用场景等）

#### Scenario: 需求已充分
- **WHEN** 对话轮次达到 3 轮
- **THEN** 系统总结已收集的需求，告知用户可以开始检索，并附带需求摘要

### Requirement: 对话阶段判断与检索触发
系统 SHALL 根据对话阶段决定是继续收集需求还是执行检索。在需求收集阶段，系统仅进行对话；在检索就绪阶段，用户确认后才执行检索。

#### Scenario: 需求收集阶段发送消息
- **WHEN** 用户在需求收集阶段（轮次 < 3）发送消息
- **THEN** 系统返回追问回复，不执行论文检索

#### Scenario: 检索就绪后用户确认检索
- **WHEN** 用户在检索就绪阶段点击"开始检索"或发送确认指令
- **THEN** 系统将收集到的需求整合为优化后的查询，执行论文检索/综述生成

#### Scenario: 用户提前触发检索
- **WHEN** 用户在需求收集阶段主动要求立即检索
- **THEN** 系统允许用户跳过对话，使用原始查询执行检索

### Requirement: 流式对话输出
系统 SHALL 支持对话回复的流式输出，使前端能够实时显示 LLM 生成的追问内容。

#### Scenario: 流式追问输出
- **WHEN** 系统生成追问回复
- **THEN** 通过 SSE 逐 token 推送回复内容到前端

### Requirement: 前端对话交互流程
前端 SHALL 在用户首次输入后进入对话模式，展示助手的追问，并在达到最低轮次后显示"开始检索"按钮。

#### Scenario: 首次输入进入对话
- **WHEN** 用户在搜索/综述模式下输入第一条消息
- **THEN** 前端进入对话模式，显示助手追问，不触发检索

#### Scenario: 对话中继续输入
- **WHEN** 用户在对话模式中继续输入
- **THEN** 前端将消息发送到对话端点，展示助手回复

#### Scenario: 三轮后显示检索按钮
- **WHEN** 对话轮次达到 3 轮且后端返回 `ready_for_search: true`
- **THEN** 前端在助手消息下方显示"开始检索"按钮

#### Scenario: 点击开始检索
- **WHEN** 用户点击"开始检索"按钮
- **THEN** 前端使用收集到的需求摘要作为查询，触发对应的检索/综述流程

## MODIFIED Requirements

### Requirement: 对话端点
原 `/api/conversation` 端点 SHALL 增加对话阶段判断逻辑：
- 接收 `session_id` 参数用于会话跟踪
- 返回 `round_count`（当前轮次）、`ready_for_search`（是否可检索）、`requirement_summary`（需求摘要）字段
- 当 `ready_for_search` 为 true 时，前端可选择触发检索

### Requirement: 检索端点
原 `/api/search/stream` 和 `/api/report/stream` 端点 SHALL 支持接收 `requirement_summary` 参数，用于将多轮对话收集的需求整合为优化查询。

## REMOVED Requirements
无
