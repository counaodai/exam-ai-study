import request from './request'
import type { Conversation, ChatMessage, SourceItem, ClassificationResult, MindMapUpdateResult } from '@/types/chat'

export interface SendMessageRequest {
  content: string
  conversation_id?: string
}

interface UpdateClassificationResponse {
  message: string
  classification: ClassificationResult
  mindmap_update: MindMapUpdateResult | null
}

export interface StreamCallbacks {
  onMetadata: (data: { conversation_id: string; sources: SourceItem[] }) => void
  onContent: (chunk: string) => void
  onDone: () => void
  onError: (error: string) => void
}

export function sendMessage(data: SendMessageRequest) {
  return request.post<any, ChatMessage>('/chat', data, {
    timeout: 120000,
  })
}

export async function sendMessageStream(
  data: SendMessageRequest,
  callbacks: StreamCallbacks,
  abortSignal?: AbortSignal,
): Promise<void> {
  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/api'
  const url = `${backendUrl}/chat/stream`

  let response: Response
  try {
    response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
      signal: abortSignal,
    })
  } catch (err: any) {
    if (err.name === 'AbortError') {
      callbacks.onError('请求已取消')
    } else {
      callbacks.onError('网络连接失败，请检查网络后重试')
    }
    return
  }

  if (!response.ok) {
    let errorMsg = `请求失败 (${response.status})`
    try {
      const errBody = await response.json()
      errorMsg = errBody.detail || errorMsg
    } catch {}
    callbacks.onError(errorMsg)
    return
  }

  const reader = response.body?.getReader()
  if (!reader) {
    callbacks.onError('无法读取响应流')
    return
  }

  const decoder = new TextDecoder()
  let buffer = ''

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed || !trimmed.startsWith('data: ')) continue

        const jsonStr = trimmed.slice(6)
        if (!jsonStr) continue

        try {
          const event = JSON.parse(jsonStr)

          if (event.type === 'metadata') {
            callbacks.onMetadata({
              conversation_id: event.conversation_id,
              sources: event.sources || [],
            })
          } else if (event.type === 'content') {
            callbacks.onContent(event.content)
          } else if (event.type === 'done') {
            callbacks.onDone()
          }
        } catch {
          // 忽略无法解析的行
        }
      }
    }

    if (buffer.trim()) {
      const trimmed = buffer.trim()
      if (trimmed.startsWith('data: ')) {
        try {
          const event = JSON.parse(trimmed.slice(6))
          if (event.type === 'content') callbacks.onContent(event.content)
          else if (event.type === 'done') callbacks.onDone()
        } catch {}
      }
    }
  } catch (err: any) {
    if (err.name === 'AbortError') {
      callbacks.onError('请求已取消')
    } else {
      callbacks.onError('流式读取中断，请重试')
    }
  }
}

export function getConversations() {
  return request.get<any, Conversation[]>('/chat/conversations')
}

export function getConversationDetail(id: string) {
  return request.get<any, { conversation: Conversation; messages: ChatMessage[] }>(
    `/chat/conversations/${id}`
  )
}

export function deleteConversation(id: string) {
  return request.delete(`/chat/conversations/${id}`)
}

export function updateMessageClassification(
  messageId: string,
  data: { module: string; sub_module?: string },
) {
  return request.put<any, UpdateClassificationResponse>(
    `/chat/messages/${messageId}/classification`,
    data,
  )
}
