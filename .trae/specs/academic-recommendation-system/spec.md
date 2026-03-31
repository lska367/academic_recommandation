
# 基于多模态重排的学术内容推荐系统 - Product Requirement Document

## Overview
- **Summary**: 构建一个基于多模态重排的学术内容推荐系统，通过对话式前端界面向学术用户提供论文推荐，并自动生成学术综述报告。系统包括 arXiv 论文爬虫、PDF 处理、多模态嵌入编码、向量索引、多模态重排序、LLM 对话和报告生成等完整功能模块。
- **Purpose**: 解决学术研究者高效发现和整理相关论文的痛点，利用多模态技术和 LLM 提供智能的论文推荐和综述服务。
- **Target Users**: 学术研究者、研究生、科研人员。

## Goals
- 从 arXiv 获取足量论文数据供系统测试和使用
- 实现 PDF 论文的读取、切片和多模态编码存储
- 构建向量索引实现快速的多模态检索
- 实现多模态重排序模块，提升推荐质量
- 通过 LLM 生成高质量的学术综述报告
- 提供美观的 React 对话式前端界面
- 系统启动时自动检查和获取数据
- 使用 uv 进行环境和依赖管理
- 实现持久化存储

## Non-Goals (Out of Scope)
- 不实现用户账户系统
- 不实现论文付费获取功能
- 不实现社交分享功能
- 不实现移动端原生应用（仅 Web 应用）

## Background & Context
- 项目基于东北林业大学毕业设计任务书和开题报告
- 使用火山引擎豆包模型作为 LLM 后端
- 使用 OpenAI 兼容接口进行 API 调用
- 使用多模态 embedding 模型处理论文内容
- 使用 uv 进行 Python 项目管理

## Functional Requirements
- **FR-1**: 从 arXiv 爬取论文元数据和 PDF 文件
- **FR-2**: 读取和解析 PDF 论文内容
- **FR-3**: 将论文内容切片并进行多模态编码
- **FR-4**: 使用向量数据库存储和索引嵌入向量
- **FR-5**: 实现多模态检索功能
- **FR-6**: 实现多模态重排序模块
- **FR-7**: 通过 LLM 生成学术综述报告
- **FR-8**: 提供 React 对话式前端界面
- **FR-9**: 系统启动时自动执行数据检查和获取
- **FR-10**: 支持向量库持久化存储

## Non-Functional Requirements
- **NFR-1**: 论文检索响应时间 &lt; 3 秒
- **NFR-2**: 前端界面加载时间 &lt; 2 秒
- **NFR-3**: 系统支持至少 1000 篇论文的存储和检索
- **NFR-4**: 代码结构清晰，易于维护和扩展

## Constraints
- **Technical**:
  - 后端使用 Python
  - 前端使用 React
  - 使用 uv 进行环境管理
  - 使用 OpenAI 兼容 API
  - Embedding 模型: doubao-embedding-vision-250615
  - 主模型: doubao-seed-2-0-lite-260215
  - API Base URL: https://ark.cn-beijing.volces.com/api/v3
- **Business**:
  - 毕业设计项目，需在指定时间内完成
- **Dependencies**:
  - arXiv API
  - 火山引擎豆包 API
  - PDF 处理库
  - 向量数据库

## Assumptions
- 用户已配置好火山引擎 API 密钥
- 网络连接稳定，可访问 arXiv 和火山引擎 API
- 有足够的磁盘空间存储 PDF 文件和向量数据
- 使用真实的 API 调用，不虚构数据

## Acceptance Criteria

### AC-1: arXiv 论文爬虫
- **Given**: 系统已配置好环境
- **When**: 启动论文爬虫
- **Then**: 成功从 arXiv 获取至少 50 篇论文的元数据和 PDF 文件
- **Verification**: `programmatic`
- **Notes**: 确保获取到足量论文供测试使用

### AC-2: PDF 读取和解析
- **Given**: 已获取 PDF 论文文件
- **When**: 执行 PDF 解析程序
- **Then**: 成功提取论文文本内容
- **Verification**: `programmatic`

### AC-3: 内容切片和多模态编码
- **Given**: 已解析的论文内容
- **When**: 执行编码程序
- **Then**: 内容被正确切片并生成多模态嵌入向量
- **Verification**: `programmatic`

### AC-4: 向量索引构建
- **Given**: 已生成的嵌入向量
- **When**: 执行索引构建程序
- **Then**: 向量被正确存储到向量数据库并建立索引
- **Verification**: `programmatic`

### AC-5: 多模态检索功能
- **Given**: 已构建的向量索引
- **When**: 用户输入查询
- **Then**: 系统返回相关的论文内容块
- **Verification**: `programmatic`

### AC-6: 多模态重排序
- **Given**: 检索返回的候选论文
- **When**: 执行重排序模块
- **Then**: 论文按相关性重新排序，质量提升
- **Verification**: `programmatic`

### AC-7: 学术综述生成
- **Given**: 重排序后的论文列表
- **When**: 触发生成综述
- **Then**: LLM 生成完整的学术综述报告
- **Verification**: `human-judgment`

### AC-8: React 前端界面
- **Given**: 后端服务已启动
- **When**: 用户访问前端页面
- **Then**: 显示美观的对话界面，用户可进行对话交互
- **Verification**: `human-judgment`

### AC-9: 启动时自动数据检查
- **Given**: 系统首次启动或数据不足时
- **When**: 启动系统
- **Then**: 自动检查数据量，不足时自动获取论文数据
- **Verification**: `programmatic`

### AC-10: 向量库持久化
- **Given**: 系统已存储向量数据
- **When**: 重启系统
- **Then**: 向量数据仍然可用，无需重新编码
- **Verification**: `programmatic`

## Open Questions
- [ ] 具体需要爬取 arXiv 哪个领域的论文？
- [ ] 向量数据库使用哪个具体产品（ChromaDB, FAISS, Qdrant 等）？
- [ ] React 前端是否需要使用 Next.js？
