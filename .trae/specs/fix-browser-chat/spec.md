# 浏览器对话功能问题修复 Spec

## Why
用户反馈浏览器对话功能仍然存在问题，需要检查并修复前端聊天功能。

## What Changes
- 检查前端 API 请求配置（代理设置）
- 验证 SSE 流式处理逻辑
- 确保前端正确接收和显示后端响应
- 检查 CORS 配置是否正确

## Impact
- Affected specs: 前端聊天功能
- Affected code:
  - `frontend/vite.config.js` - Vite 代理配置
  - `frontend/src/api/client.js` - API 客户端
  - `frontend/src/App.jsx` - 聊天状态管理

## ADDED Requirements
### Requirement: 前端 API 代理配置
前端在开发环境通过 Vite 代理访问后端 API，确保浏览器能正确发送请求到后端。

#### Scenario: 开发环境 API 请求
- **WHEN** 前端发起 `/api/*` 请求
- **THEN** Vite 开发服务器将请求代理到后端 `http://localhost:8000`

#### Scenario: 生产环境 API 请求
- **WHEN** 前端发起 `/api/*` 请求
- **THEN** 请求直接发送到同源或配置的后端地址

## MODIFIED Requirements
### Requirement: API_BASE_URL 配置
API 客户端应使用相对路径，由 Vite 代理处理请求转发。

## REMOVED Requirements
### Requirement: N/A
无删除需求

## 问题诊断步骤

1. **检查 vite.config.js 代理配置**
   - 确保 `/api` 请求被正确代理到后端
   - 检查 `changeOrigin` 设置

2. **检查 client.js API 地址**
   - 确保使用相对路径而非硬编码的 `localhost:8000`

3. **检查后端 CORS 配置**
   - 确保 `main.py` 中的 CORS 中间件允许前端域名

4. **检查 SSE 流式响应处理**
   - 验证 `streaming_chunk` 事件能正确更新 UI
   - 验证 `chat_complete` 事件能正确结束流式状态