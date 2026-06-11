# 项目开发规范 — 公考AI智能学习系统

你正在参与开发一个"公考AI智能学习系统"项目。你必须严格按照项目需求说明书来编写代码，不得擅自修改架构、技术栈或功能设计。

## 一、技术栈（不可更改）

### 前端
- 框架：Vue 3（Composition API + `<script setup>` 语法）
- UI库：Element Plus（必须使用，不要引入其他UI库）
- 状态管理：Pinia
- HTTP客户端：Axios
- 思维导图：vue-flow
- 图表：ECharts（vue-echarts）
- 路由：Vue Router 4
- 构建工具：Vite + TypeScript
- 包管理器：pnpm

### 后端
- 框架：Python FastAPI
- RAG框架：LangChain（Python版）
- 向量数据库：ChromaDB
- 关系数据库：MySQL
- ORM：SQLAlchemy + Alembic（数据库迁移）
- LLM：mimo 大模型（兼容 Anthropic 接口协议，通过 langchain-anthropic 调用）

### 禁止使用
- ❌ 不要使用 React / Next.js / Tailwind CSS
- ❌ 不要使用 Prisma / TypeORM
- ❌ 不要使用 shadcn/ui / Ant Design
- ❌ 不要引入需求说明书中未提及的框架或库

## 二、项目结构（必须遵守）

前端目录：exam-ai-study/frontend/
后端目录：exam-ai-study/backend/

前端文件必须放在 frontend/src/ 下，按以下结构组织：
- views/ — 页面视图（.vue文件）
- components/ — 组件（按功能分子目录：chat/ mindmap/ upload/ analysis/ layout/）
- stores/ — Pinia状态管理
- api/ — Axios请求封装
- router/ — Vue Router配置
- types/ — TypeScript类型定义
- utils/ — 工具函数

后端文件必须放在 backend/app/ 下，按以下结构组织：
- api/ — FastAPI路由（每个功能模块一个文件）
- core/rag/ — RAG相关（parser, chunker, embedder, vector_store, retriever）
- core/ai/ — AI相关（llm, classifier, answer_gen, method_extract）
- core/mindmap/ — 思维导图（builder, updater）
- models/ — SQLAlchemy数据库模型
- schemas/ — Pydantic请求/响应模型
- db/ — 数据库配置和初始化
- prompts/ — Prompt模板（每个功能一个文件）
- config.py — 配置管理
- main.py — FastAPI入口

## 三、编码规范

### Vue3 规范
- 必须使用 `<script setup lang="ts">` 语法
- 必须使用 Composition API（ref, reactive, computed, watch）
- 不要使用 Options API
- 组件命名使用 PascalCase（如 ChatMessage.vue）
- 页面命名使用 PascalCase（如 Dashboard.vue）
- Element Plus 组件直接使用（不需要全局注册，在需要的文件中 import）
- 样式使用 `<style scoped>`，可以用 Element Plus 的 CSS 变量

### Python 规范
- 遵循 PEP 8 规范
- 使用 type hints（类型注解）
- 使用 async/await 异步语法
- Pydantic v2 语法（用 model_validator 而非 validator）
- SQLAlchemy 2.0 语法（用 async_sessionmaker）
- 所有 API 路由必须有完整的请求/响应 Schema

### API 规范
- 前端 API 请求统一封装在 frontend/src/api/ 目录下
- 使用 Axios 实例，配置 baseURL 从环境变量读取
- 后端 API 统一前缀 /api
- 错误响应格式统一：{"detail": "错误描述"}
- 成功响应格式：直接返回数据对象，或 {"data": ..., "message": "..."}

## 四、数据库规范

- 使用 SQLAlchemy 2.0 的 Declarative Base
- 所有表必须有 id（UUID主键）、created_at、updated_at 字段
- 使用 Alembic 管理数据库迁移
- 预置公考模块数据在 backend/app/db/init_data.py 中定义

## 五、RAG 规范

- 文档分块必须按题目结构分块（识别题号），不要按固定字符数分块
- 向量化使用 ChromaDB，通过 langchain_chroma 集成
- RAG 检索链使用 LangChain 的 RetrievalQA 或自定义 chain
- Prompt 模板单独存放在 backend/app/prompts/ 目录下

## 六、开发顺序（必须按此顺序）

### Phase 1 — 核心基础
1. 前后端项目初始化
2. 数据库建表（SQLAlchemy Models + Alembic）
3. 文档上传 + 解析 + 分块 + 向量化
4. RAG 检索 + AI 问答页面

### Phase 2 — 分类与思维导图
5. 公考模块分类体系（预置数据）
6. 两级分类器（规则 + LLM）
7. 思维导图渲染（vue-flow）
8. 问答后自动分类 + 导图更新

### Phase 3 — 方法论与分析
9. 方法论自动生成
10. 统计分析仪表盘

## 七、关键约束

1. 每次只实现当前 Phase 的功能，不要跳到后续 Phase
2. 生成代码前，先确认当前文件的目录结构和已有代码
3. 不要删除或覆盖已有功能，只做增量添加
4. 遇到不确定的需求，优先参考需求说明书，而不是自行假设
5. 生成的代码必须是可运行的，不要写半成品
6. 环境变量中的 API Key 使用占位符，不要写真实值
7. 代码注释使用中文
8. 每个文件的代码不要超过 300 行，超过则拆分

## 八、需求说明书位置

完整的需求说明书位于：exam-ai-study/项目需求说明书.md
开发前请先阅读该文档，理解完整的功能需求、数据模型和API设计。
