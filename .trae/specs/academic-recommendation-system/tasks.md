
# 基于多模态重排的学术内容推荐系统 - The Implementation Plan (Decomposed and Prioritized Task List)

## [ ] Task 1: 项目初始化和环境配置
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 使用 uv 初始化 Python 项目
  - 创建项目目录结构
  - 配置 .gitignore 文件
  - 创建 .env.example 文件
  - 初始化 git 仓库
- **Acceptance Criteria Addressed**: AC-9（环境配置基础）
- **Test Requirements**:
  - `programmatic` TR-1.1: 项目目录结构创建成功
  - `programmatic` TR-1.2: uv 环境配置正确
  - `programmatic` TR-1.3: git 仓库初始化成功
- **Notes**: 使用 uv 进行依赖管理，遵循 Python 项目最佳实践

## [ ] Task 2: arXiv 论文爬虫实现
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 实现 arXiv API 客户端
  - 实现论文元数据获取
  - 实现 PDF 文件下载
  - 实现数据存储（元数据保存为 JSON）
  - 实现数据量检查功能
- **Acceptance Criteria Addressed**: AC-1, AC-9
- **Test Requirements**:
  - `programmatic` TR-2.1: 成功从 arXiv 获取至少 50 篇论文元数据
  - `programmatic` TR-2.2: 成功下载 PDF 文件
  - `programmatic` TR-2.3: 数据量检查功能正常工作
  - `programmatic` TR-2.4: 元数据正确保存
- **Notes**: 使用真实的 arXiv API，不虚构数据

## [ ] Task 3: PDF 读取和解析模块
- **Priority**: P0
- **Depends On**: Task 2
- **Description**: 
  - 集成 PDF 处理库（PyMuPDF/fitz）
  - 实现 PDF 文本提取
  - 实现 PDF 页面图像提取（用于多模态）
  - 实现基础的内容清洗
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-3.1: 成功从 PDF 提取文本内容
  - `programmatic` TR-3.2: 成功从 PDF 提取页面图像
  - `programmatic` TR-3.3: 文本内容清洗正常
- **Notes**: 同时支持文本和图像提取，为多模态编码做准备

## [ ] Task 4: 内容切片模块
- **Priority**: P0
- **Depends On**: Task 3
- **Description**: 
  - 实现文本分块策略（按段落/按语义）
  - 实现图像切片（按页面）
  - 实现内容块元数据管理
  - 实现切片数据存储
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-4.1: 文本内容正确切片
  - `programmatic` TR-4.2: 图像内容正确切片
  - `programmatic` TR-4.3: 切片元数据完整
- **Notes**: 切片大小要适合 embedding 模型输入

## [ ] Task 5: 向量数据库集成
- **Priority**: P0
- **Depends On**: Task 4
- **Description**: 
  - 选择并集成向量数据库（ChromaDB）
  - 实现向量存储功能
  - 实现持久化配置
  - 实现集合管理
- **Acceptance Criteria Addressed**: AC-4, AC-10
- **Test Requirements**:
  - `programmatic` TR-5.1: 向量数据库成功初始化
  - `programmatic` TR-5.2: 向量数据成功存储
  - `programmatic` TR-5.3: 持久化功能正常
  - `programmatic` TR-5.4: 重启后数据仍然可用
- **Notes**: 使用 ChromaDB，易于集成且支持持久化

## [ ] Task 6: 多模态 Embedding 编码模块
- **Priority**: P0
- **Depends On**: Task 5
- **Description**: 
  - 集成 OpenAI SDK
  - 配置火山引擎 API（base_url, api_key）
  - 实现文本 embedding 编码
  - 实现图像 embedding 编码（doubao-embedding-vision-250615）
  - 实现编码批量处理
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-6.1: OpenAI 客户端配置正确
  - `programmatic` TR-6.2: 文本 embedding 生成成功
  - `programmatic` TR-6.3: 图像 embedding 生成成功
  - `programmatic` TR-6.4: 批量编码功能正常
- **Notes**: 使用真实 API 调用，测试前确保 API key 配置正确

## [ ] Task 7: 多模态检索模块
- **Priority**: P0
- **Depends On**: Task 6
- **Description**: 
  - 实现查询 embedding 编码
  - 实现向量相似度搜索
  - 实现检索结果过滤
  - 实现检索结果排序（初步）
  - 返回论文原始内容块和信息
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-7.1: 查询编码成功
  - `programmatic` TR-7.2: 相似度搜索返回结果
  - `programmatic` TR-7.3: 检索结果包含完整信息
- **Notes**: 检索结果需要关联论文元数据

## [ ] Task 8: 多模态重排序模块
- **Priority**: P1
- **Depends On**: Task 7
- **Description**: 
  - 使用 doubao-seed-2-0-lite-260215 实现重排序
  - 构建重排序提示词
  - 实现候选论文打分
  - 实现按分数重排序
  - 返回 Top-K 论文
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-8.1: 重排序模块成功调用 LLM
  - `programmatic` TR-8.2: 返回论文有合理的分数
  - `programmatic` TR-8.3: 论文按分数正确排序
- **Notes**: 重排序是提升推荐质量的关键

## [ ] Task 9: 学术综述生成模块
- **Priority**: P1
- **Depends On**: Task 8
- **Description**: 
  - 设计综述生成提示词
  - 集成重排序后的论文内容
  - 实现流式输出（可选）
  - 实现报告格式化（Markdown）
  - 实现报告保存功能
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-9.1: 成功调用 LLM 生成报告
  - `programmatic` TR-9.2: 报告格式正确（Markdown）
  - `human-judgement` TR-9.3: 报告内容质量良好
  - `programmatic` TR-9.4: 报告成功保存
- **Notes**: 综述需要整合多篇论文内容

## [ ] Task 10: 后端 API 服务
- **Priority**: P1
- **Depends On**: Task 9
- **Description**: 
  - 使用 FastAPI 构建后端服务
  - 实现对话接口
  - 实现论文检索接口
  - 实现综述生成接口
  - 实现数据检查接口
  - 添加 CORS 支持
- **Acceptance Criteria Addressed**: AC-5, AC-6, AC-7, AC-9
- **Test Requirements**:
  - `programmatic` TR-10.1: FastAPI 服务成功启动
  - `programmatic` TR-10.2: API 文档可访问
  - `programmatic` TR-10.3: 各接口正常响应
  - `programmatic` TR-10.4: CORS 配置正确
- **Notes**: API 设计要 RESTful

## [ ] Task 11: React 前端项目初始化
- **Priority**: P1
- **Depends On**: Task 10
- **Description**: 
  - 使用 Vite 创建 React 项目
  - 配置 TypeScript（可选）
  - 配置 Tailwind CSS
  - 配置 API 客户端
  - 配置路由（如需要）
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-11.1: React 项目成功初始化
  - `programmatic` TR-11.2: 开发服务器成功启动
  - `programmatic` TR-11.3: Tailwind CSS 配置正确
- **Notes**: 遵循 Vercel React 最佳实践

## [ ] Task 12: 对话界面组件
- **Priority**: P1
- **Depends On**: Task 11
- **Description**: 
  - 实现聊天消息组件
  - 实现输入框组件
  - 实现消息列表
  - 实现加载状态
  - 实现错误处理显示
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-12.1: 界面组件渲染正常
  - `programmatic` TR-12.2: 消息输入和发送正常
  - `human-judgement` TR-12.3: 界面美观合理
- **Notes**: 注重用户体验

## [ ] Task 13: 前端与后端集成
- **Priority**: P1
- **Depends On**: Task 12
- **Description**: 
  - 实现对话 API 调用
  - 实现论文列表显示
  - 实现综述报告显示
  - 实现流式输出显示（如支持）
  - 处理加载和错误状态
- **Acceptance Criteria Addressed**: AC-5, AC-6, AC-7, AC-8
- **Test Requirements**:
  - `programmatic` TR-13.1: API 调用成功
  - `programmatic` TR-13.2: 数据正确显示
  - `programmatic` TR-13.3: 错误处理正常
- **Notes**: 确保前后端数据格式一致

## [ ] Task 14: 启动时自动数据检查和获取
- **Priority**: P1
- **Depends On**: Task 2, Task 10
- **Description**: 
  - 在后端启动时检查论文数据量
  - 数据不足时自动启动爬虫
  - 实现进度显示（可选）
  - 确保有足量论文供测试
- **Acceptance Criteria Addressed**: AC-1, AC-9
- **Test Requirements**:
  - `programmatic` TR-14.1: 启动时自动检查数据
  - `programmatic` TR-14.2: 数据不足时自动获取
  - `programmatic` TR-14.3: 至少获取 50 篇论文
- **Notes**: 这是系统启动的必要步骤

## [ ] Task 15: 集成测试和系统测试
- **Priority**: P2
- **Depends On**: Task 13, Task 14
- **Description**: 
  - 端到端流程测试
  - 性能测试
  - 边界情况测试
  - 错误恢复测试
- **Acceptance Criteria Addressed**: 所有 AC
- **Test Requirements**:
  - `programmatic` TR-15.1: 端到端流程运行成功
  - `programmatic` TR-15.2: 检索响应时间 &lt; 3 秒
  - `human-judgement` TR-15.3: 整体系统运行稳定
- **Notes**: 确保整个系统协同工作

## [ ] Task 16: 删除测试文件并启动项目
- **Priority**: P2
- **Depends On**: Task 15
- **Description**: 
  - 识别临时测试文件
  - 删除测试文件（保留必要的文档）
  - 编写启动脚本
  - 启动完整项目（后端 + 前端）
- **Acceptance Criteria Addressed**: 所有 AC
- **Test Requirements**:
  - `programmatic` TR-16.1: 测试文件清理完成
  - `programmatic` TR-16.2: 启动脚本执行成功
  - `programmatic` TR-16.3: 后端服务正常运行
  - `programmatic` TR-16.4: 前端服务正常运行
- **Notes**: 保留 .env.example 和必要文档
