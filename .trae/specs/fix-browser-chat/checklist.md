# Checklist

- [x] vite.config.js 代理配置正确，能将 /api 请求代理到后端
- [x] vite.config.js 添加了 ws: true 和 x-accel-buffering 配置支持 SSE
- [x] client.js 中 API_BASE_URL 使用相对路径
- [x] main.py 中 CORS 配置允许前端域名访问
- [x] main.py StreamingResponse 发送正确的 SSE 头
- [x] client.js SSE 流式处理逻辑正确
- [x] App.jsx 聊天状态更新逻辑正确
- [x] 代码通过 lint 检查