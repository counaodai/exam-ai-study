# 公考AI智能学习系统

> **基于 RAG 知识库的公考智能学习助手** — 让备考更高效

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/counaodai/exam-ai-study/actions)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/counaodai/exam-ai-study/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/Vue.js-3.x-41B883?logo=vue.js)](https://vuejs.org/)
[![Star](https://img.shields.io/github/stars/counaodai/exam-ai-study?style=social)](https://github.com/counaodai/exam-ai-study/stargazers)
[![Fork](https://img.shields.io/github/forks/counaodai/exam-ai-study?style=social)](https://github.com/counaodai/exam-ai-study/network/members)

<div align="center">
  <p>
    <a href="#%E5%8A%9F%E8%83%BD%E7%89%B9%E8%89%B2">功能特色</a> •
    <a href="#%E6%8A%80%E6%9C%AF%E6%A0%88">技术栈</a> •
    <a href="#%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B">快速开始</a> •
    <a href="#%E9%A1%B9%E7%9B%AE%E7%BB%93%E6%9E%84">项目结构</a> •
    <a href="#%E8%B4%A1%E7%8C%AE%E6%8C%87%E5%8D%97">贡献指南</a> •
    <a href="#%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98">FAQ</a>
  </p>
  <p>
    <a href="#%E8%8B%B1%E6%96%87%E7%89%88english">English</a>
  </p>
</div>

---

## :scroll: 项目概述

### 核心定位

**公考AI智能学习系统**是一款面向公务员考试考生的智能化学习工具，通过 **RAG（检索增强生成）技术**构建个人知识库，实现资料导入、智能问答、知识体系可视化、解题方法论自动归纳的完整学习闭环。

### :star: 解决的核心痛点

| 痛点 | 解决方案 |
|------|----------|
| 备考资料繁杂，缺乏结构化整理 | AI自动解析文档，按模块组织知识体系 |
| 题目容易遗忘，同类题型反复出错 | 智能分类归集，掌握度可视化追踪 |
| 零散知识点难以系统化为知识体系 | 思维导图自动生成，层层递进 |
| 无法从做题经验中提炼通用解法 | AI自动归纳方法论，举一反三 |

### 适用场景

- :pencil2: 公务员行测/申论备考
- :brain: 事业单位考试复习
- :book: 各类公职类考试学习
- :computer: 企业培训知识管理

---

## :sparkles: 功能特色

### :rocket: 核心功能

| 功能 | 说明 | 优先级 |
|------|------|--------|
| **RAG 知识库问答** | 上传文档后自动建立知识库，AI基于知识精准回答，可溯源 | P0 |
| **思维导图可视化** | 自动构建知识体系导图，支持手动编辑、拖拽、缩放 | P0 |
| **题目智能分类** | 自动识别题目所属公考模块（言语/数量/判断/资料/常识） | P0 |
| **方法论自动归纳** | 积累题目后AI自动生成通用解题方法，提炼套路 | P0 |
| **统计分析仪表盘** | 多维度数据统计：模块分布、掌握度热力图、学习趋势 | P1 |

### :wrench: 技术亮点

- :mag: **智能分块** — 按题目/章节结构分块，非固定字符数
- :robot: **两级分类器** — 关键词规则匹配 + LLM 智能分类，双重保障
- :chart: **动态思维导图** — 基于 vue-flow，自定义节点样式
- :chart_with_upwards_trend: **ECharts 图表** — 丰富可视化展示学习数据

---

## :gear: 技术栈

### 前端技术

| 技术 | 用途 |
|------|------|
| [Vue 3](https://vuejs.org/) | 渐进式 JavaScript 框架 |
| [Element Plus](https://element-plus.org/) | Vue 3 组件库 |
| [Pinia](https://pinia.vuejs.org/) | Vue 状态管理 |
| [Vue Router](https://router.vuejs.org/) | 官方路由管理器 |
| [Axios](https://axios-http.com/) | HTTP 客户端 |
| [vue-flow](https://vueflow.dev/) | 思维导图渲染引擎 |
| [ECharts](https://echarts.apache.org/) | 数据可视化图表 |
| [Vite](https://vite.dev/) | 下一代前端构建工具 |
| [TypeScript](https://www.typescriptlang.org/) | 类型安全的 JavaScript |

### 后端技术

| 技术 | 用途 |
|------|------|
| [FastAPI](https://fastapi.tiangolo.com/) | 高性能 Web 框架 |
| [LangChain](https://python.langchain.com/) | RAG 应用开发框架 |
| [ChromaDB](https://www.trychroma.com/) | 向量数据库 |
| [SQLAlchemy](https://www.sqlalchemy.org/) | Python ORM 工具 |
| [Alembic](https://alembic.sqlalchemy.org/) | 数据库迁移工具 |
| [MySQL](https://www.mysql.com/) | 关系型数据库 |

---

## :rocket: 快速开始

### 环境要求

| 环境 | 版本要求 |
|------|----------|
| Node.js | >= 18.0 |
| pnpm | >= 8.0 |
| Python | >= 3.11 |
| MySQL | >= 8.0 |

### 1. 克隆项目

```bash
git clone https://github.com/counaodai/exam-ai-study.git
cd exam-ai-study
```

### 2. 后端配置与启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（复制模板后修改）
copy .env.template .env      # Windows
# cp .env.template .env      # macOS/Linux

# 初始化数据库
# 确保 MySQL 运行中，并在 config.py 中配置 DATABASE_URL

# 启动后端服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> :wrench: **环境变量说明**

复制 [backend/app/config.py](backend/app/config.py) 中的配置项到 `.env` 文件，修改实际值：

```env
# 数据库连接
DATABASE_URL=mysql+aiomysql://root:your_password@localhost:3306/exam_study

# LLM 配置
LLM_PROVIDER=openai
LLM_MODEL=your_model_name
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://your-api-endpoint/v1

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

### 3. 前端配置与启动

```bash
# 打开新终端，进入前端目录
cd frontend

# 安装依赖（使用 pnpm）
pnpm install

# 启动开发服务器
pnpm dev
```

访问 http://localhost:5173 即可使用系统。

### 4. Docker 一键部署（可选）

```bash
# 使用 Docker Compose 启动 MySQL + ChromaDB
docker-compose up -d

# 然后分别启动前后端
```

---

## :file_folder: 项目结构

```
exam-ai-study/
├── frontend/                          # ===== Vue3 前端 =====
│   ├── src/
│   │   ├── views/                     # 页面视图
│   │   │   ├── Dashboard.vue          # 统计仪表盘
│   │   │   ├── Upload.vue             # 文档导入
│   │   │   ├── Chat.vue               # AI问答
│   │   │   ├── MindMap.vue            # 思维导图
│   │   │   ├── Analysis.vue           # 统计分析
│   │   │   └── Settings.vue           # 系统设置
│   │   ├── components/                # 组件
│   │   │   ├── chat/                  # 聊天组件
│   │   │   ├── mindmap/               # 思维导图组件
│   │   │   ├── upload/                # 上传组件
│   │   │   └── layout/                # 布局组件
│   │   ├── stores/                    # Pinia 状态管理
│   │   ├── api/                       # API 请求封装
│   │   ├── router/                    # Vue Router 配置
│   │   ├── types/                     # TypeScript 类型
│   │   └── utils/                     # 工具函数
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
│
├── backend/                           # ===== Python FastAPI 后端 =====
│   ├── app/
│   │   ├── api/                       # API 路由
│   │   ├── core/
│   │   │   ├── rag/                   # RAG 核心逻辑
│   │   │   ├── ai/                    # AI 核心逻辑
│   │   │   └── mindmap/               # 思维导图逻辑
│   │   ├── models/                    # 数据库模型
│   │   ├── schemas/                   # Pydantic 模型
│   │   ├── prompts/                   # Prompt 模板
│   │   ├── db/                        # 数据库配置
│   │   └── config.py                  # 配置管理
│   ├── alembic/                       # 数据库迁移
│   ├── requirements.txt
│   └── .env                           # 环境变量
│
├── docs/                              # 项目文档
├── .gitignore                         # Git 忽略配置
├── docker-compose.yml                 # Docker Compose 配置
└── README.md                          # 项目说明
```

---

## :books: 使用示例

### 完整学习流程

```
1. 文档导入       → 上传公考教材/真题 PDF
       │
       ▼
2. RAG 知识库     → 系统自动解析、分块、向量化
       │
       ▼
3. AI 智能问答    → 基于知识库提问，获取精准回答
       │
       ▼
4. 自动分类       → 题目自动归入对应模块（言语/数量/判断/资料）
       │
       ▼
5. 思维导图更新   → 知识点自动归入知识体系图
       │
       ▼
6. 方法论生成     → 同类型题目积累后，AI 自动总结解题方法
```

### API 接口概览

| 模块 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 文档管理 | `/api/documents/upload` | POST | 上传文档 |
| | `/api/documents` | GET | 获取文档列表 |
| AI 问答 | `/api/chat` | POST | 发送消息获取回答 |
| | `/api/chat/conversations` | GET | 获取对话历史 |
| 思维导图 | `/api/mindmaps` | GET/POST | 获取/创建导图 |
| | `/api/mindmaps/[id]` | PUT/DELETE | 更新/删除导图 |
| 统计分析 | `/api/analysis/overview` | GET | 获取统计数据 |
| 方法论 | `/api/methods/generate` | POST | 触发方法论生成 |

> :page_facing\_ 详细 API 文档访问 http://localhost:8000/docs 查看

---

## :raised_hands: 贡献指南

欢迎任何形式的贡献！

### 贡献流程

1. **Fork** 本仓库
2. **创建** 特性分支 (`git checkout -b feature/AmazingFeature`)
3. **提交** 更改 (`git commit -m 'Add some AmazingFeature'`)
4. **推送** 到分支 (`git push origin feature/AmazingFeature`)
5. **提交** Pull Request

### 开发规范

- 前端遵循 [Vue 3 组合式 API](https://vuejs.org/api/basic-reactivity.html) 规范
- 后端遵循 [PEP 8](https://peps.python.org/pep-0008/) 规范
- 提交信息使用中文，格式：`类型: 描述`
  - `feat: 新增 RAG 检索功能`
  - `fix: 修复分类器 bug`
  - `docs: 更新 README 文档`

### 问题反馈

- :bug: [提交 Issue](https://github.com/counaodai/exam-ai-study/issues) — 报告 Bug 或提出新功能建议
- :email: 联系方式：wjh20040730@outlook.com

---

## :question: 常见问题 (FAQ)

### Q1: 如何配置 LLM 接口？

编辑 `backend/.env` 文件，配置以下环境变量：

```env
LLM_PROVIDER=openai
LLM_MODEL=your_model_name
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://your-api-endpoint/v1
```

### Q2: 支持哪些文档格式？

- PDF（含扫描版 OCR）
- Word (.docx)
- 纯文本 (.txt)
- Markdown (.md)
- 图片 (.jpg/.png，需 OCR 识别)

### Q3: 如何在本地部署？

参考 [快速开始](#%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B) 部分，按步骤安装依赖并配置环境变量即可。

### Q4: ChromaDB 数据存在哪里？

默认存储在 `backend/chroma_data/` 目录下，该目录已在 `.gitignore` 中排除，不会提交到 Git。

### Q5: 如何重置数据库？

```bash
cd backend
alembic upgrade head    # 执行最新迁移
python -m app.db.init_data  # 初始化预置数据
```

---

## :scroll: 更新日志

详见 [项目需求说明书](项目需求说明书.md)，包含完整的功能迭代计划和开发日志。

---

## :mortar\_board: 致谢

- [Vue.js](https://vuejs.org/) — 渐进式 JavaScript 框架
- [FastAPI](https://fastapi.tiangolo.com/) — 现代 Web 框架
- [LangChain](https://python.langchain.com/) — LLM 应用开发框架
- [ChromaDB](https://www.trychroma.com/) — 嵌入式向量数据库
- [vue-flow](https://vueflow.dev/) — 流程图/思维导图引擎

---

## :balance\_scale: 开源协议

本项目采用 [MIT 许可证](LICENSE) 开源。

---

## 英文版 (English)

### Overview

**Exam AI Study** is an intelligent learning assistant for Chinese civil service exam preparation. It leverages **RAG (Retrieval-Augmented Generation)** technology to build a personal knowledge base, enabling document import, intelligent Q&A, knowledge visualization, and automated methodology extraction.

### Key Features

- :speech\_balloon: **RAG Knowledge Base Q&A** — Upload documents to build a searchable knowledge base
- :chart: **Mind Map Visualization** — Auto-generate interactive knowledge structure diagrams
- :brain: **Smart Question Classification** — Auto-categorize questions by exam module
- :memo: **Methodology Extraction** — AI extracts problem-solving strategies from accumulated questions
- :bar\_chart: **Analytics Dashboard** — Multi-dimensional statistics and learning trend tracking

### Tech Stack

- **Frontend**: Vue 3 + Element Plus + Pinia + TypeScript + vue-flow + ECharts
- **Backend**: Python FastAPI + LangChain + ChromaDB + SQLAlchemy + MySQL

### Quick Start

```bash
# Clone repository
git clone https://github.com/counaodai/exam-ai-study.git
cd exam-ai-study

# Backend setup
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend setup
cd ../frontend
pnpm install
pnpm dev
```

### License

This project is licensed under the [MIT License](LICENSE).

---
💬 联系我
如果大家在使用过程中遇到任何问题，或者有啥想法想聊聊，都可以通过我的 QQ 邮箱找我哈～

📧 2833693854@qq.com

我会尽量及时回复大家，也欢迎一起交流校园项目、技术学习之类的话题，大家一起进步嘛 😊
<div align="center">

**如果这个项目对你有帮助，请 :star: 给一个 Star！**

Made with :heart: by [counaodai](https://github.com/counaodai)

</div>
