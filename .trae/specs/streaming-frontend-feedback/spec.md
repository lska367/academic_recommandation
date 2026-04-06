# 前后端交互增强规格说明书

## Why
当前前端无法看到后端检索和重排序的详细流程，用户体验不够透明；报告生成采用非流式一次性返回，用户等待时间长且缺乏交互感。需要增强前后端交互，让用户实时了解系统处理进度，并实现流式"打字机"效果提升用户体验。

## What Changes
- 后端新增检索进度阶段推送接口（流式/SSE）
- 后端新增重排序进度推送接口（流式/SSE）
- 后端报告生成接口改造为流式输出
- 前端新增实时进度展示组件（检索阶段、重排阶段）
- 前端报告展示实现打字机流式输出效果
- 前端新增论文推荐详情展开功能

## Impact
- Affected specs: AC-5（多模态检索）、AC-6（多模态重排序）、AC-7（学术综述生成）、AC-8（React前端）
- Affected code:
  - backend/main.py（API改造）
  - backend/reranker.py（进度推送）
  - backend/report_generator.py（流式输出）
  - frontend/src/App.jsx（进度展示、打字机）
  - frontend/src/components/ChatMessage.jsx（消息组件增强）

## ADDED Requirements

### Requirement: 检索进度实时推送
后端在执行检索时，应通过SSE（Server-Sent Events）向前端实时推送检索进度各阶段的状态。

#### Scenario: 检索进度推送
- **WHEN** 用户发起检索请求
- **THEN** 后端立即返回检索开始状态
- **THEN** 后端推送query编码阶段完成
- **THEN** 后端推送向量搜索阶段完成
- **THEN** 后端推送初步检索结果数量
- **THEN** 后端推送最终结果

### Requirement: 重排序进度实时推送
后端在执行重排序时，应通过SSE向前端实时推送重排序进度。

#### Scenario: 重排序进度推送
- **WHEN** 检索结果需要重排序
- **THEN** 后端推送重排序开始状态
- **THEN** 后端推送正在对第N篇论文打分
- **THEN** 后端推送重排序完成及Top-K结果

### Requirement: 报告生成流式输出
后端在生成学术综述报告时，应采用流式输出方式，边生成边返回。

#### Scenario: 流式报告生成
- **WHEN** 用户请求生成学术综述
- **THEN** 后端采用stream=True方式调用LLM
- **THEN** 后端将LLM返回的chunk实时推送至前端
- **THEN** 前端实时将内容追加显示（打字机效果）

### Requirement: 前端进度展示组件
前端应提供清晰的可视化进度指示，展示当前正在执行的处理阶段。

#### Scenario: 检索进度展示
- **WHEN** 用户发起检索
- **THEN** 显示"正在检索相关论文..."
- **THEN** 显示各阶段进度（如"正在编码查询..."、"正在搜索向量库..."）
- **THEN** 完成后显示结果数量

#### Scenario: 重排序进度展示
- **WHEN** 检索结果需要重排序
- **THEN** 显示"正在进行多模态重排序..."
- **THEN** 显示重排序进度（如"已处理 3/10 篇论文"）

### Requirement: 打字机效果展示
前端在接收流式报告内容时，应实现逐字/逐段显示的打字机效果。

#### Scenario: 打字机显示报告
- **WHEN** 前端开始接收流式报告内容
- **THEN** 内容逐段追加显示
- **THEN** 用户可看到报告"正在生成"的过程
- **THEN** 报告完成后可完整复制或查看

## MODIFIED Requirements

### Requirement: 论文检索接口
现有检索接口 `/api/search` 需要支持可选的流式进度推送模式。

#### Scenario: 流式检索（可选）
- **WHEN** 请求参数中 `stream=true`
- **THEN** 使用SSE返回检索进度
- **THEN** 最终返回完整检索结果

### Requirement: 学术综述接口
现有报告生成接口 `/api/report` 需要改造为流式输出。

#### Scenario: 流式报告（默认行为）
- **WHEN** 请求 `/api/report`
- **THEN** 后端采用流式输出
- **THEN** 前端实时显示生成进度

## API Contract Changes

### GET /api/search (SSE模式)
**Request**: `POST /api/search` with `stream=true` in body
**Response**: `text/event-stream`
```
event: search_start
data: {"stage": "search_start", "message": "开始检索论文"}

event: query_encoding
data: {"stage": "query_encoding", "message": "查询编码完成"}

event: vector_search
data: {"stage": "vector_search", "message": "向量搜索完成", "found": 15}

event: search_complete
data: {"success": true, "results": [...]}
```

### POST /api/report (SSE模式)
**Request**: `POST /api/report` with `stream=true` in body
**Response**: `text/event-stream`
```
event: report_start
data: {"stage": "report_start", "message": "开始生成学术综述"}

event: report_chunk
data: {"stage": "report_chunk", "content": "第一章 引言..."}

event: report_complete
data: {"success": true, "citation_stats": {...}}
```

## Technical Constraints
- SSE比WebSocket更轻量，适合单向服务端推送场景
- LLM流式输出需使用OpenAI SDK的stream模式
- 前端SSE解析需处理重连和错误恢复
- 打字机效果需注意性能，避免频繁setState
