# Fix Frontend Backend Connection Issue Spec

## Why
前端应用在浏览器中显示错误，控制台出现 `ECONNREFUSED 127.0.0.1:8000` 错误。这表明前端开发服务器无法代理请求到后端 API 服务器（端口 8000），导致所有功能（认证、聊天、数据加载等）都无法正常工作。用户体验受到严重影响，系统基本不可用。

## What Changes
- **诊断并修复前后端连接问题**
- **增强错误处理和用户体验**：当后端不可用时提供清晰的错误提示
- **优化开发环境配置**：确保开发环境配置正确且易于使用

## Impact
- Affected specs: 所有前端功能（认证、聊天、推荐、设置）
- Affected code:
  - `frontend/vite.config.js` - 代理配置
  - `frontend/src/api/client.js` - API 客户端错误处理
  - `frontend/src/App.jsx` - 错误状态展示
  - `backend/main.py` - 后端服务启动和健康检查

## ADDED Requirements

### Requirement: 后端连接诊断与修复
系统 SHALL 确保前端能够成功连接到后端 API 服务，并提供清晰的连接状态反馈。

#### Scenario: 开发环境正常启动
- **WHEN** 用户同时启动前端和后端服务
- **THEN** 前端应能成功代理 API 请求到后端（localhost:8000）
- **AND** 所有功能（认证、聊天等）应正常工作

#### Scenario: 后端未启动时的优雅降级
- **WHEN** 后端服务未启动或无法访问
- **THEN** 前端应显示友好的错误提示，告知用户检查后端服务
- **AND** 不应显示技术性错误信息给最终用户

#### Scenario: 生产/远程部署环境支持
- **WHEN** 应用部署到远程服务器（如 kam.free.svipss.top）
- **THEN** 前端应能正确连接到远程后端服务
- **AND** 代理配置应支持灵活的目标地址配置

### Requirement: 错误处理增强
系统 SHALL 提供完善的错误处理机制，确保网络故障时用户体验良好。

#### Scenario: 网络连接失败
- **WHEN** API 请求因网络原因失败
- **THEN** 应显示可操作的错误提示（如"请确保后端服务已启动"）
- **AND** 提供重试机制或明确的解决步骤

#### Scenario: API 超时
- **WHEN** 后端响应时间过长
- **THEN** 应在合理时间内超时并提示用户
- **AND** 避免界面长时间无响应

## MODIFIED Requirements

### Requirement: Vite 代理配置优化
现有的 vite.config.js 代理配置需要增强，以支持：
- 更灵活的后端地址配置（支持环境变量）
- 更好的错误日志输出
- 支持多种部署场景（本地开发、远程部署）

### Requirement: API 客户端错误处理
现有的 client.js 需要改进：
- 区分"后端未启动"和其他网络错误
- 提供更具体的错误消息
- 添加连接状态检测功能

### Requirement: 前端错误展示
App.jsx 中的错误提示需要优化：
- 显示更友好的中文错误信息
- 提供明确的解决方案指引
- 在页面显著位置显示连接状态

## REMOVED Requirements
无
