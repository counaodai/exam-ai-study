<script setup lang="ts">
import { ref, nextTick, onMounted, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Promotion, Document, VideoPause } from '@element-plus/icons-vue'
import { marked } from 'marked'
import ClassificationTag from '@/components/chat/ClassificationTag.vue'
import type { ChatMessage, ClassificationResult, MindMapUpdateResult } from '@/types/chat'

const chatStore = useChatStore()
const inputMessage = ref('')
const messageListRef = ref<HTMLElement | null>(null)

marked.setOptions({
  breaks: true,
  gfm: true,
})

function renderMarkdown(content: string): string {
  if (!content) return ''
  return marked.parse(content) as string
}

onMounted(() => {
  chatStore.fetchConversations()
})

function scrollToBottom() {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

watch(
  () => chatStore.streamingContent,
  () => {
    scrollToBottom()
  },
)

async function handleSend() {
  const content = inputMessage.value.trim()
  if (!content) return
  if (chatStore.sending) return

  inputMessage.value = ''
  scrollToBottom()
  await chatStore.sendMessage(content)
  scrollToBottom()
}

async function handleSelectConversation(id: string) {
  await chatStore.fetchMessages(id)
  scrollToBottom()
}

function handleNewConversation() {
  chatStore.startNewConversation()
}

async function handleDeleteConversation(id: string) {
  try {
    await ElMessageBox.confirm('确定删除该对话？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await chatStore.deleteConversation(id)
    ElMessage.success('对话已删除')
  } catch (e) {
    // 用户取消
  }
}

function handleStopStream() {
  chatStore.cancelStream()
}

function handleKeydown(e: Event) {
  const evt = e as KeyboardEvent
  if (evt.key === 'Enter' && !evt.shiftKey) {
    evt.preventDefault()
    handleSend()
  }
}

function isStreamingMessage(msg: ChatMessage): boolean {
  return msg.id.startsWith('temp-ai-') && chatStore.sending
}

function handleClassificationCorrected(
  msgId: string,
  data: { classification: ClassificationResult; mindmap_update: MindMapUpdateResult | null },
) {
  chatStore.updateMessageClassification(msgId, data.classification, data.mindmap_update)
  ElMessage.success('分类已修正，思维导图已更新')
}
</script>

<template>
  <div class="chat-page">
    <div class="chat-sidebar">
      <div class="sidebar-header">
        <el-button type="primary" @click="handleNewConversation" :icon="Plus" style="width: 100%">
          新建对话
        </el-button>
      </div>
      <div class="conversation-list">
        <div
          v-for="conv in chatStore.conversations"
          :key="conv.id"
          class="conversation-item"
          :class="{ active: chatStore.currentConversation?.id === conv.id }"
          @click="handleSelectConversation(conv.id)"
        >
          <span class="conv-title">{{ conv.title || '新对话' }}</span>
          <el-icon class="delete-btn" @click.stop="handleDeleteConversation(conv.id)">
            <Delete />
          </el-icon>
        </div>
        <div v-if="chatStore.conversations.length === 0" class="empty-conv">
          <span>暂无对话</span>
        </div>
      </div>
    </div>

    <div class="chat-main">
      <div ref="messageListRef" class="message-list">
        <div v-if="chatStore.messages.length === 0" class="empty-hint">
          <iconify-icon icon="mdi:leaf" width="56" class="empty-icon"></iconify-icon>
          <h2>公考AI助手</h2>
          <p>基于知识库的智能问答，帮你解答公考难题</p>
          <div class="hint-tips">
            <el-tag
              v-for="tip in ['国考行测真题解析', '数量关系解题技巧', '言语理解答题方法']"
              :key="tip"
              class="tip-tag"
              @click="inputMessage = tip; handleSend()"
            >
              {{ tip }}
            </el-tag>
          </div>
        </div>
        <div
          v-for="msg in chatStore.messages"
          :key="msg.id"
          class="message-item"
          :class="msg.role"
        >
          <div class="message-avatar">
            <el-avatar :size="36" :style="{ background: msg.role === 'user' ? 'var(--accent-color)' : 'var(--primary-color)' }">
              {{ msg.role === 'user' ? '我' : 'AI' }}
            </el-avatar>
          </div>
          <div class="message-body">
            <div v-if="msg.role === 'user'" class="message-text user-text">
              {{ msg.content }}
            </div>
            <div v-else class="message-text ai-text">
              <template v-if="isStreamingMessage(msg) && !msg.content">
                <span class="dot-loading">思考中</span>
              </template>
              <template v-else-if="isStreamingMessage(msg)">
                <div class="streaming-content" v-html="renderMarkdown(msg.content)"></div>
                <span class="streaming-cursor"></span>
              </template>
              <template v-else>
                <div v-html="renderMarkdown(msg.content)"></div>
              </template>
            </div>
            <div v-if="msg.sources && msg.sources.length > 0" class="message-sources">
              <el-divider content-position="left">
                <el-icon><Document /></el-icon>
                <span style="margin-left: 4px">参考来源</span>
              </el-divider>
              <div class="source-list">
                <el-card
                  v-for="(src, i) in msg.sources"
                  :key="i"
                  shadow="hover"
                  class="source-card"
                >
                  <div class="source-header">
                    <el-tag size="small" type="info">{{ src.source }}</el-tag>
                    <el-tag v-if="src.page" size="small">P{{ src.page }}</el-tag>
                    <el-tag size="small" type="success">相似度 {{ (src.score * 100).toFixed(0) }}%</el-tag>
                  </div>
                  <div class="source-content">{{ src.content }}</div>
                </el-card>
              </div>
            </div>
            <ClassificationTag
              v-if="msg.classification && !isStreamingMessage(msg)"
              :classification="msg.classification"
              :mindmap-update="msg.mindmap_update"
              :message-id="msg.id"
              @corrected="handleClassificationCorrected(msg.id, $event)"
            />
          </div>
        </div>
      </div>

      <div class="input-area">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="2"
          placeholder="请输入公考相关问题... (Enter 发送，Shift+Enter 换行)"
          @keydown="handleKeydown"
          :disabled="chatStore.sending"
          resize="none"
        />
        <el-button
          v-if="!chatStore.sending"
          type="primary"
          :icon="Promotion"
          @click="handleSend"
          :disabled="!inputMessage.trim()"
        >
          发送
        </el-button>
        <el-button
          v-else
          type="danger"
          :icon="VideoPause"
          @click="handleStopStream"
        >
          停止
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-page {
  display: flex;
  height: calc(100vh - 120px);
  gap: 16px;
  animation: fadeIn var(--transition-fade);
}

.chat-sidebar {
  width: 260px;
  background: var(--bg-surface);
  border-radius: var(--radius-hand-drawn-soft);
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-md);
  border: 2px solid var(--border-light);
  overflow: hidden;
}

.sidebar-header {
  padding: 14px;
  border-bottom: 2px dashed var(--border-color);
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.conversation-item {
  padding: 12px 14px;
  border-radius: var(--radius-hand-drawn-soft);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
  transition: all var(--transition-fast);
  position: relative;
  font-family: var(--font-heading);
}

.conversation-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%) rotate(-2deg);
  width: 3px;
  height: 0;
  background: var(--primary-gradient);
  border-radius: 0 3px 3px 0;
  transition: height var(--transition-bounce);
}

.conversation-item:hover,
.conversation-item.active {
  background-color: var(--primary-bg);
}

.conversation-item.active {
  font-weight: 600;
}

.conversation-item:hover::before,
.conversation-item.active::before {
  height: 60%;
}

.conv-title {
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  color: var(--text-regular);
}

.conversation-item.active .conv-title {
  color: var(--primary-color);
  font-weight: 600;
}

.delete-btn {
  opacity: 0;
  color: var(--text-muted);
  flex-shrink: 0;
  transition: all var(--transition-fast);
  font-size: 16px;
}

.conversation-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  color: var(--danger-color) !important;
}

.empty-conv {
  text-align: center;
  padding: 30px 20px;
  color: var(--text-muted);
  font-size: 14px;
  font-family: var(--font-display);
}

.chat-main {
  flex: 1;
  background: var(--bg-surface);
  border-radius: var(--radius-hand-drawn-soft);
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-md);
  border: 2px solid var(--border-light);
  overflow: hidden;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.empty-hint {
  text-align: center;
  padding-top: 80px;
  color: var(--text-muted);
  animation: fadeIn var(--transition-fade);
}

.empty-icon {
  display: block;
  margin-bottom: 20px;
  opacity: 0.85;
  color: var(--primary-color);
}

.empty-hint h2 {
  color: var(--text-primary);
  margin-bottom: 10px;
  font-size: 26px;
  font-family: var(--font-heading);
}

.empty-hint p {
  margin-bottom: 24px;
  color: var(--text-secondary);
  font-size: 15px;
  font-family: var(--font-display);
}

.hint-tips {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.tip-tag {
  cursor: pointer;
  transition: all var(--transition-hover-lift);
  border: 1px solid var(--border-color);
  font-family: var(--font-heading);
}

.tip-tag:hover {
  background: var(--primary-gradient);
  color: #fff;
  border-color: transparent;
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.message-item {
  display: flex;
  gap: 14px;
  margin-bottom: 28px;
  animation: fadeIn var(--transition-fade);
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.message-body {
  max-width: 75%;
  min-width: 100px;
}

.message-item.user .message-body {
  text-align: right;
}

.message-text {
  padding: 14px 18px;
  border-radius: var(--radius-hand-drawn-soft);
  line-height: 1.7;
  position: relative;
}

.user-text {
  background: var(--primary-gradient);
  color: #fff;
  white-space: pre-wrap;
  border-bottom-right-radius: 4px;
  box-shadow: 0 2px 8px rgba(91, 140, 90, 0.25);
}

.ai-text {
  background: var(--bg-muted);
  color: var(--text-primary);
  border-bottom-left-radius: 4px;
  border: 2px solid var(--border-light);
}

.ai-text :deep(p) {
  margin: 0 0 12px 0;
}

.ai-text :deep(p:last-child) {
  margin-bottom: 0;
}

.ai-text :deep(ul),
.ai-text :deep(ol) {
  padding-left: 20px;
  margin: 8px 0;
}

.ai-text :deep(code) {
  background: rgba(91, 140, 90, 0.08);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--primary-color);
}

.ai-text :deep(pre) {
  background: #3A3228;
  color: #E8E0CC;
  padding: 16px;
  border-radius: var(--radius-hand-drawn-soft);
  overflow-x: auto;
  margin: 12px 0;
  box-shadow: var(--shadow-inner);
}

.ai-text :deep(pre code) {
  background: transparent;
  color: inherit;
  padding: 0;
}

.ai-text :deep(strong) {
  color: var(--text-primary);
  font-weight: 600;
}

.ai-text :deep(blockquote) {
  border-left: 4px solid var(--primary-color);
  padding-left: 14px;
  margin: 10px 0;
  color: var(--text-secondary);
  background: rgba(91, 140, 90, 0.04);
  padding: 10px 14px;
  border-radius: 0 var(--radius-hand-drawn-soft) var(--radius-hand-drawn-soft) 0;
}

.loading-text {
  display: flex;
  align-items: center;
}

.dot-loading::after {
  content: '';
  animation: dots 1.5s infinite;
}

@keyframes dots {
  0% { content: ''; }
  25% { content: '.'; }
  50% { content: '..'; }
  75% { content: '...'; }
}

.streaming-cursor {
  display: inline-block;
  width: 2px;
  height: 18px;
  background: var(--primary-color);
  margin-left: 2px;
  vertical-align: text-bottom;
  animation: cursor-blink 0.8s infinite;
  border-radius: 1px;
}

@keyframes cursor-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

.streaming-content {
  display: inline;
}

.message-sources {
  margin-top: 14px;
}

.message-sources :deep(.el-divider__text) {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
  font-family: var(--font-heading);
}

.source-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.source-card {
  text-align: left;
  transition: all var(--transition-hover-lift);
}

.source-card:hover {
  transform: translateX(4px);
  box-shadow: var(--shadow-md) !important;
}

.source-card :deep(.el-card__body) {
  padding: 12px 14px;
}

.source-header {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.source-content {
  font-size: 13px;
  color: var(--text-regular);
  line-height: 1.6;
  max-height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.input-area {
  padding: 18px 20px;
  border-top: 2px dashed var(--border-color);
  display: flex;
  gap: 12px;
  align-items: flex-end;
  background: var(--bg-surface);
}

.input-area :deep(.el-textarea__inner) {
  border-radius: var(--radius-hand-drawn-soft);
  border: 2px solid var(--border-color);
  transition: all var(--transition-fast);
  resize: none;
  font-family: var(--font-body);
}

.input-area :deep(.el-textarea__inner:focus) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(91, 140, 90, 0.12);
}

.input-area :deep(.el-textarea__inner:hover) {
  border-color: var(--primary-light);
}

:deep(.el-button--primary) {
  border-radius: var(--radius-hand-drawn-soft);
  padding: 12px 24px;
  height: auto;
  align-self: flex-end;
  font-family: var(--font-heading);
}

:deep(.el-button--danger) {
  border-radius: var(--radius-hand-drawn-soft);
  padding: 12px 24px;
  height: auto;
  align-self: flex-end;
  font-family: var(--font-heading);
}

@media (max-width: 768px) {
  .chat-page {
    flex-direction: column;
    height: auto;
  }

  .chat-sidebar {
    width: 100%;
    max-height: 200px;
  }

  .message-body {
    max-width: 90%;
  }
}
</style>
