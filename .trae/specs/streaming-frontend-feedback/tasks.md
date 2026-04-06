# 前后端交互增强任务清单

## [x] Task 1: 后端 SSE 基础架构实现
- **Priority**: P0
- **Depends On**: None
- **Description**: 在后端实现SSE（Server-Sent Events）基础设施，支持流式事件推送
  - [ ] 1.1 创建 SSE 工具模块 `backend/sse_utils.py`
  - [ ] 1.2 实现 `SSEHandler` 类处理连接管理
  - [ ] 1.3 实现事件编码和发送工具函数
  - [ ] 1.4 在 main.py 中集成 SSE 中间件

## [x] Task 2: 检索流程 SSE 推送实现
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 将检索流程各阶段通过SSE向前端推送进度
  - [ ] 2.1 修改 `MultimodalRetrieval.search()` 支持回调机制
  - [ ] 2.2 在 `main.py` 实现 `/api/search/stream` 端点
  - [ ] 2.3 实现检索开始事件推送
  - [ ] 2.4 实现查询编码阶段事件推送
  - [ ] 2.5 实现向量搜索阶段事件推送
  - [ ] 2.6 实现结果返回事件推送

## [x] Task 3: 重排序流程 SSE 推送实现
- **Priority**: P0
- **Depends On**: Task 1, Task 2
- **Description**: 将重排序流程各阶段通过SSE向前端推送进度
  - [ ] 3.1 修改 `Reranker.rerank()` 支持回调机制
  - [ ] 3.2 在 `/api/search/stream` 端点集成重排序进度推送
  - [ ] 3.3 实现重排序开始事件推送
  - [ ] 3.4 实现论文打分进度事件推送
  - [ ] 3.5 实现重排序完成事件推送

## [x] Task 4: 报告生成流式输出实现
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 将报告生成改为流式输出，使用OpenAI SDK的stream模式
  - [ ] 4.1 修改 `ReportGenerator.generate_report()` 支持流式输出
  - [ ] 4.2 在 `main.py` 实现 `/api/report/stream` 端点
  - [ ] 4.3 实现报告开始生成事件推送
  - [ ] 4.4 实现报告内容chunk事件推送
  - [ ] 4.5 实现报告生成完成事件推送（含引用统计）

## [x] Task 5: 前端 SSE 客户端实现
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 在前端实现SSE客户端，接收后端推送
  - [ ] 5.1 在 `frontend/src/api/client.js` 添加 SSE 客户端方法
  - [ ] 5.2 实现 `searchWithProgress()` 方法
  - [ ] 5.3 实现 `generateSurveyWithProgress()` 方法
  - [ ] 5.4 实现错误处理和重连机制

## [x] Task 6: 前端进度展示组件
- **Priority**: P1
- **Depends On**: Task 5
- **Description**: 前端新增进度展示组件，实时显示处理阶段
  - [ ] 6.1 创建 `frontend/src/components/ProgressIndicator.jsx` 组件
  - [ ] 6.2 实现阶段显示（检索中、重排序中、生成报告中）
  - [ ] 6.3 实现进度条和百分比显示
  - [ ] 6.4 实现论文打分进度显示

## [x] Task 7: 前端打字机效果实现
- **Priority**: P1
- **Depends On**: Task 4, Task 5
- **Description**: 前端实现流式报告内容的打字机显示效果
  - [ ] 7.1 修改 `ChatMessage.jsx` 支持流式内容追加
  - [ ] 7.2 实现逐段显示动画效果
  - [ ] 7.3 添加打字机光标指示器
  - [ ] 7.4 完成后移除光标，保持内容稳定

## [x] Task 8: 前端状态管理改造
- **Priority**: P1
- **Depends On**: Task 5, Task 6, Task 7
- **Description**: 改造前端状态管理，支持实时进度更新
  - [ ] 8.1 在 App.jsx 添加进度状态管理
  - [ ] 8.2 实现检索结果实时追加显示
  - [ ] 8.3 实现流式报告内容追加
  - [ ] 8.4 处理加载状态和错误状态

## [x] Task 9: 端到端测试和调试
- **Priority**: P2
- **Depends On**: Task 2, Task 3, Task 4, Task 8
- **Description**: 完整流程测试和Bug修复
  - [ ] 9.1 测试检索流程SSE推送完整性
  - [ ] 9.2 测试重排序进度推送正确性
  - [ ] 9.3 测试报告流式生成和显示
  - [ ] 9.4 修复发现的问题

## Task Dependencies
- Task 2 依赖 Task 1
- Task 3 依赖 Task 1 和 Task 2
- Task 4 依赖 Task 1
- Task 5 依赖 Task 1
- Task 6 依赖 Task 5
- Task 7 依赖 Task 4 和 Task 5
- Task 8 依赖 Task 5, Task 6, Task 7
- Task 9 依赖 Task 2, Task 3, Task 4, Task 8
