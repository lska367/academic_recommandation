# 多模态学术推荐系统

基于多模态重排的学术内容推荐系统，使用豆包模型提供智能论文推荐和学术报告生成。

## 功能特性

- 📚 **arXiv 论文爬虫** - 自动获取和下载学术论文
- 🔍 **多模态检索** - 支持文本和图像的多模态理解
- 📊 **智能重排序** - LLM 驱动的论文重排序
- 📝 **学术报告生成** - 自动生成综合学术综述
- 💬 **对话式界面** - React 前端，友好的用户交互

## 快速开始

### 前置要求

- Python 3.13+
- Node.js 18+
- uv (Python 包管理)
- Volcengine API Key

### 1. 配置 API Key

编辑 `backend/.env` 文件，填入你的 Volcengine API Key：

```env
VOLCENGINE_API_KEY=your_actual_api_key_here
```

### 2. 启动后端

```bash
cd backend
uv sync
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端将自动：
- 检查数据是否充足
- 如果不足，自动从 arXiv 获取 50+ 篇论文
- 处理 PDF 并构建索引

### 3. 启动前端（新终端）

```bash
cd frontend
npm install
npm run dev
```

### 4. 访问应用

打开浏览器访问：`http://localhost:5173`

## 项目结构

```
academic_recommandation/
├── backend/              # Python 后端
│   ├── arxiv_crawler.py     # arXiv 爬虫
│   ├── pdf_processor.py      # PDF 处理
│   ├── embedding_module.py   # 多模态 Embedding
│   ├── vector_store.py       # 向量存储
│   ├── reranker.py           # 重排序模块
│   ├── report_generator.py   # 报告生成
│   ├── multimodal_retrieval.py # 检索集成
│   └── main.py               # FastAPI 入口
├── frontend/             # React 前端
│   └── src/
│       ├── components/       # UI 组件
│       └── api/              # API 客户端
└── start.sh              # 启动脚本
```

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | API 信息 |
| `/health` | GET | 健康检查 |
| `/api/search` | POST | 论文搜索 |
| `/api/report` | POST | 学术报告生成 |
| `/api/conversation` | POST | 对话交互 |
| `/api/data/check` | GET | 数据状态检查 |
| `/api/index/stats` | GET | 索引统计 |

## 使用说明

### 论文检索模式

1. 在前端选择 "📚 论文检索" 模式
2. 输入你感兴趣的主题或关键词
3. 系统将返回相关论文列表

### 学术综述模式

1. 选择 "✨ 学术综述" 模式
2. 输入主题
3. 系统将生成一份完整的学术综述报告

## 配置项

在 `backend/.env` 中可配置：

- `TARGET_PAPER_COUNT` - 目标论文数量（默认 50）
- `EMBEDDING_MODEL` - Embedding 模型
- `CHAT_MODEL` - 对话模型
- `CHROMA_DB_PATH` - 向量数据库路径
