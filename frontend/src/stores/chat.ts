import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Conversation, ChatMessage, SourceItem, ClassificationResult, MindMapUpdateResult } from '@/types/chat'
import * as chatApi from '@/api/chat'

export const useChatStore = defineStore('chat', () => {
  const conversations = ref<Conversation[]>([])
  const currentConversation = ref<Conversation | null>(null)
  const messages = ref<ChatMessage[]>([])
  const sending = ref(false)
  const streamingContent = ref('')
  const streamingSources = ref<SourceItem[]>([])
  const abortController = ref<AbortController | null>(null)

  const isStreaming = computed(() => sending.value && streamingContent.value.length > 0)

  async function fetchConversations() {
    conversations.value = await chatApi.getConversations()
  }

  async function fetchMessages(conversationId: string) {
    const res = await chatApi.getConversationDetail(conversationId)
    currentConversation.value = res.conversation
    messages.value = res.messages
  }

  function cancelStream() {
    if (abortController.value) {
      abortController.value.abort()
      abortController.value = null
    }
  }

  async function sendMessage(content: string) {
    if (sending.value) return

    sending.value = true
    streamingContent.value = ''
    streamingSources.value = []

    const userMsg: ChatMessage = {
      id: 'temp-user-' + Date.now(),
      conversation_id: currentConversation.value?.id || '',
      role: 'user',
      content,
      question_id: null,
      module_id: null,
      classification: null,
      sources: null,
      mindmap_update: null,
      created_at: new Date().toISOString(),
    }
    messages.value.push(userMsg)

    const aiPlaceholder: ChatMessage = {
      id: 'temp-ai-' + Date.now(),
      conversation_id: currentConversation.value?.id || '',
      role: 'assistant',
      content: '',
      question_id: null,
      module_id: null,
      classification: null,
      sources: null,
      mindmap_update: null,
      created_at: new Date().toISOString(),
    }
    messages.value.push(aiPlaceholder)
    const aiIndex = messages.value.length - 1

    const controller = new AbortController()
    abortController.value = controller

    try {
      await chatApi.sendMessageStream(
        {
          content,
          conversation_id: currentConversation.value?.id,
        },
        {
          onMetadata(data) {
            messages.value[aiIndex].conversation_id = data.conversation_id
            messages.value[aiIndex].sources = data.sources.length > 0 ? data.sources : null
            streamingSources.value = data.sources
          },
          onContent(chunk) {
            streamingContent.value += chunk
            messages.value[aiIndex].content = streamingContent.value
          },
          onDone() {
            messages.value[aiIndex].content = streamingContent.value
          },
          onError(error) {
            if (!streamingContent.value) {
              messages.value[aiIndex].content = `⚠️ ${error}`
            } else {
              messages.value[aiIndex].content = streamingContent.value
            }
          },
        },
        controller.signal,
      )

      if (!currentConversation.value) {
        await fetchConversations()
        const aiMsg = messages.value[aiIndex]
        if (aiMsg.conversation_id) {
          const detail = await chatApi.getConversationDetail(aiMsg.conversation_id)
          currentConversation.value = detail.conversation
          const realAiMsg = detail.messages.find(
            (m) => m.role === 'assistant' && m.content === aiMsg.content,
          )
          if (realAiMsg) {
            messages.value[aiIndex] = realAiMsg
          }
        }
      }
    } catch (e: any) {
      if (!messages.value[aiIndex].content) {
        messages.value[aiIndex].content = '⚠️ 发送失败，请检查网络后重试'
      }
    } finally {
      sending.value = false
      streamingContent.value = ''
      streamingSources.value = []
      abortController.value = null
    }
  }

  async function deleteConversation(id: string) {
    await chatApi.deleteConversation(id)
    conversations.value = conversations.value.filter((c) => c.id !== id)
    if (currentConversation.value?.id === id) {
      currentConversation.value = null
      messages.value = []
    }
  }

  function startNewConversation() {
    currentConversation.value = null
    messages.value = []
  }

  function updateMessageClassification(
    msgId: string,
    classification: ClassificationResult,
    mindmapUpdate: MindMapUpdateResult | null,
  ) {
    const msg = messages.value.find((m) => m.id === msgId)
    if (msg) {
      msg.classification = classification
      if (mindmapUpdate) {
        msg.mindmap_update = mindmapUpdate
      }
    }
  }

  return {
    conversations,
    currentConversation,
    messages,
    sending,
    streamingContent,
    isStreaming,
    fetchConversations,
    fetchMessages,
    sendMessage,
    cancelStream,
    deleteConversation,
    startNewConversation,
    updateMessageClassification,
  }
})
