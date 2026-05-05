# 修复前端对话内容返回问题 Spec

## Why
用户在使用SSH远程开发环境，通过浏览器工具进行对话时，前端无法正确显示对话内容。需要诊断并修复对话返回的问题。

## What Changes
- 诊断前端聊天功能不返回内容的根本原因
- 修复API客户端流式处理逻辑
- 确保流式响应正确更新UI状态

## Impact
- Affected specs: 前端聊天功能
- Affected code:
  - `frontend/src/api/client.js` - API客户端
  - `frontend/src/App.jsx` - 聊天状态管理
  - `frontend/src/components/ChatMessage.jsx` - 消息渲染

## ADDED Requirements
### Requirement: 流式聊天功能
系统 SHALL 通过SSE流式接口接收AI回复，并实时更新UI显示。

#### Scenario: 用户发送消息并接收回复
- **WHEN** 用户在输入框输入消息并点击发送
- **THEN** 系统显示用户消息，并实时显示AI流式回复
- **AND** 回复完成后，消息内容正确保存，不再显示loading状态

#### Scenario: 流式处理异常
- **WHEN** 流式响应出现错误或中断
- **THEN** 系统显示错误提示
- **AND** 清理临时状态，不留残留消息

## MODIFIED Requirements
### Requirement: sendChatMessage API客户端
当前端发送聊天消息时，需要正确处理SSE流式响应，并在完成时返回完整的响应数据。

## REMOVED Requirements
### Requirement: N/A
无删除需求

## 问题诊断

根据代码分析，可能的问题点：

1. **client.js 流式处理**: `xhr.onprogress` 可能在某些情况下无法正确处理SSE数据
2. **响应事件匹配**: 前端期望 `chat_complete` 事件，但后端发送的是 `chat_complete`
3. **状态更新时序**: `isStreaming` 和 `content` 的更新时序可能导致UI不更新

## 修复方案

1. 检查并修复 `client.js` 中的SSE解析逻辑
2. 确保 `streaming_chunk` 事件正确更新 `streamingContent`
3. 确保 `chat_complete` 事件正确设置最终 `content` 并关闭流式状态
4. 添加错误处理和超时机制