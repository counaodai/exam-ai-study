# AI 问答流式输出优化 — 开发文档

> **版本**: v1.0  
> **日期**: 2026-05-28  
> **对应需求**: 优化需求文档 → 二、需求一：AI 问答流式输出优化

---

## 一、问题分析

### 1.1 原有实现的问题

| 问题 | 根因 |
|------|------|
| 用户等待 10-30 秒无反馈 | 后端使用 LangChain `ainvoke()` 等待 LLM 完整生成后才返回 |
| 一次性渲染全部内容 | 前端通过 Axios POST 请求等待完整 JSON 响应 |
| 用户误以为系统卡顿 | 等待期间仅显示静态 "思考中..." 动画，无进度感知 |

### 1.2 原有数据流

```
用户发送 → Axios POST /api/chat → rag_query() → ainvoke() [阻塞10-30s] → 完整JSON响应 → 前端一次性渲染
```

---

## 二、技术方案

### 2.1 整体架构

采用 **SSE（Server-Sent Events）** 实现流式输出：

```
用户发送 → fetch POST /api/chat/stream → RAG检索 → astream() [逐块生成] → SSE事件流 → 前端实时拼接渲染
```

### 2.2 技术选型对比

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| SSE (Server-Sent Events) | 实现简单、HTTP原生、自动重连 | 单向通信、仅支持文本 | ✅ 采用 |
| WebSocket | 双向通信、全功能 | 实现复杂、需要额外协议升级 | ❌ 过度设计 |
| 轮询 | 实现最简 | 延迟高、资源浪费 | ❌ 不适用 |

### 2.3 为什么用 fetch 而非 EventSource

- `EventSource` 仅支持 GET 请求，而对话接口需要 POST（携带 `content` 和 `conversation_id`）
- `fetch` + `ReadableStream` 支持 POST 请求的流式读取
- 兼容性良好，支持 Chrome、Edge、Firefox 最新版本

---

## 三、接口变更

### 3.1 新增接口

**`POST /api/chat/stream`**

与原有 `POST /api/chat` 功能一致，但返回 SSE 流。

#### 请求体

```json
{
  "content": "什么是行程问题？",
  "conversation_id": "可选，已有对话的ID"
}
```

#### 响应格式

`Content-Type: text/event-stream`

事件流格式：

```
data: {"type":"metadata","conversation_id":"uuid","sources":[...]}

data: {"type":"content","content":"行"}

data: {"type":"content","content":"程"}

data: {"type":"content","content":"问题"}

data: {"type":"done"}
```

#### 事件类型说明

| 事件类型 | 说明 | 数据结构 |
|----------|------|----------|
| `metadata` | 首个事件，包含对话ID和参考来源 | `{type, conversation_id, sources[]}` |
| `content` | 文本块，可能是一个字、一个词或一个句子片段 | `{type, content}` |
| `done` | 流结束信号 | `{type}` |

#### 错误处理

- 网络中断：前端 `fetch` 抛出 `AbortError`，已输出内容保留
- LLM 生成异常：流中追加错误提示文本，仍发送 `done` 事件
- 客户端主动取消：通过 `AbortController.abort()` 断开连接

### 3.2 原有接口保持不变

`POST /api/chat` 保留，作为回退方案。可通过配置切换。

---

## 四、核心实现逻辑

### 4.1 后端

#### 文件: `backend/app/core/rag/retriever.py`

新增 `rag_query_stream()` 异步生成器：

```python
async def rag_query_stream(question: str, sources: list) -> AsyncGenerator[str, None]:
    if sources:
        chain = prompt | llm | StrOutputParser()
        async for chunk in chain.astream({"context": context, "question": question}):
            yield chunk
    else:
        chain = prompt | llm | StrOutputParser()
        async for chunk in chain.astream({"question": question}):
            yield chunk
```

关键点：
- 使用 LangChain 的 `chain.astream()` 替代 `chain.ainvoke()`
- `StrOutputParser` 将 LLM 的 `AIMessageChunk` 转为纯文本字符串
- 每个 chunk 可能是一个字、一个词或一个短句

#### 文件: `backend/app/api/chat.py`

新增 `POST /chat/stream` 端点：

1. **创建对话和用户消息**（同步完成，立即提交数据库）
2. **执行 RAG 检索**（获取参考资料）
3. **启动流式响应**（`StreamingResponse` + SSE）
4. **后台保存完整回答**（`BackgroundTasks`，流结束后触发）

数据流：

```
stream_message()
├── 创建 Conversation + Message (user)
├── commit 到数据库
├── _search_with_timeout() → sources
└── StreamingResponse(generate())
    ├── yield metadata event (conversation_id + sources)
    ├── yield content events (逐块)
    └── yield done event
        └── BackgroundTask: _save_stream_result()
            ├── 保存 Message (assistant) 到数据库
            └── 触发 _post_process_classification()
```

### 4.2 前端

#### 文件: `frontend/src/api/chat.ts`

新增 `sendMessageStream()` 函数：

- 使用 `fetch` 发起 POST 请求
- 通过 `ReadableStream` 逐块读取响应
- 解析 SSE `data:` 行，分发到对应回调
- 支持 `AbortSignal` 取消

#### 文件: `frontend/src/stores/chat.ts`

改造 `sendMessage()` 方法：

1. 先插入用户消息占位和 AI 空消息占位
2. 调用 `sendMessageStream()`，通过回调实时更新 AI 消息内容
3. 流结束后刷新对话列表（获取真实数据库记录）

新增状态：
- `streamingContent` — 当前正在流式接收的内容
- `isStreaming` — 是否正在流式输出
- `abortController` — 用于取消请求

#### 文件: `frontend/src/views/Chat.vue`

流式展示逻辑：

- **等待阶段**：显示 "思考中..." 动画（`dot-loading`）
- **流式阶段**：实时 Markdown 渲染 + 闪烁光标（`streaming-cursor`）
- **完成阶段**：光标消失，内容定型
- **滚动控制**：监听 `streamingContent` 变化自动滚动到底部
- **停止按钮**：流式输出期间替换发送按钮为"停止"按钮

---

## 五、异常处理机制

| 场景 | 处理方式 |
|------|----------|
| 网络断开 | fetch 抛出 AbortError，前端显示 "网络连接失败" 提示，已输出内容保留 |
| LLM 生成超时/异常 | 后端捕获异常，追加错误提示文本到流中，正常发送 done 事件 |
| 用户点击"停止" | 前端调用 `AbortController.abort()`，后端收到 `CancelledError`，已生成内容保存到数据库 |
| HTTP 非 200 响应 | 前端读取错误详情，显示对应错误消息 |
| SSE 解析失败 | 忽略无法解析的行，继续处理后续事件 |
| 新建对话但流中断 | metadata 事件已发送 conversation_id，后台任务仍会保存完整回答 |

---

## 六、验收标准对应

| 编号 | 验收项 | 实现方式 |
|------|--------|----------|
| AC-1 | 流式输出基础能力 | 使用 `chain.astream()` + SSE 逐块推送，前端实时拼接显示 |
| AC-2 | Markdown 实时渲染 | `marked.parse()` 在每次 `streamingContent` 更新时重新渲染 |
| AC-3 | 异常处理 | 后端 try/except 捕获异常；前端 AbortController + 错误回调 |
| AC-4 | 状态管理 | `sending` 状态控制按钮 loading，输入框禁用 |
| AC-5 | 结束标识 | `done` 事件触发状态恢复，按钮恢复可用，自动滚动到底部 |
| AC-6 | 对话存储 | `_save_stream_result()` 后台任务在流结束后保存完整回答到数据库 |

---

## 七、测试方案

### 7.1 功能测试

| 测试项 | 操作 | 预期结果 |
|--------|------|----------|
| 基本流式输出 | 发送 "什么是行程问题？" | 文字逐字/逐词出现，Markdown 正确渲染 |
| 新建对话 | 不选择对话直接发送 | 创建新对话，流式输出正常，对话列表更新 |
| 续接对话 | 在已有对话中发送问题 | 在同一对话中流式输出 |
| 停止生成 | 流式输出中点击"停止" | 输出停止，已生成内容保留 |
| 参考来源 | 发送有知识库匹配的问题 | 流结束后显示参考来源卡片 |
| 无知识库匹配 | 发送知识库外的问题 | 正常流式输出，标注"非来自知识库" |

### 7.2 异常测试

| 测试项 | 操作 | 预期结果 |
|--------|------|----------|
| 网络断开 | 流式输出中断开网络 | 已输出内容保留，显示错误提示 |
| 后端未启动 | 发送问题 | 显示 "网络连接失败" 提示 |
| 快速连续发送 | 连续点击发送 | sending 状态阻止重复提交 |

### 7.3 兼容性测试

| 浏览器 | 版本 | 测试结果 |
|--------|------|----------|
| Chrome | 最新 | 待测试 |
| Edge | 最新 | 待测试 |
| Firefox | 最新 | 待测试 |

---

## 八、变更文件清单

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `backend/app/core/rag/retriever.py` | 修改 | 新增 `rag_query_stream()` 异步生成器 |
| `backend/app/api/chat.py` | 修改 | 新增 `POST /chat/stream` 端点、`_save_stream_result()` 后台任务、`_format_sources_for_stream()` |
| `frontend/src/api/chat.ts` | 修改 | 新增 `sendMessageStream()` 流式请求函数、`StreamCallbacks` 接口 |
| `frontend/src/stores/chat.ts` | 修改 | 改造 `sendMessage()` 支持流式、新增流式状态管理 |
| `frontend/src/views/Chat.vue` | 修改 | 流式内容渲染、光标动画、停止按钮、自动滚动 |

---

## 九、向后兼容

- 原有 `POST /api/chat` 接口保留不变
- 原有 `GET /api/chat/conversations`、`GET /api/chat/conversations/{id}`、`DELETE /api/chat/conversations/{id}` 接口不变
- 前端默认使用流式接口，如需回退，只需将 `sendMessage()` 中的 `sendMessageStream` 调用替换回原 `chatApi.sendMessage()` 即可
