export interface Conversation {
  id: string
  title: string | null
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id: string
  conversation_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  question_id: string | null
  module_id: string | null
  classification: ClassificationResult | null
  sources: SourceItem[] | null
  mindmap_update: MindMapUpdateResult | null
  created_at: string
}

export interface ClassificationResult {
  module: string
  sub_module: string
  confidence: number
  reason: string
}

export interface MindMapUpdateResult {
  updated: boolean
  mindmap_id: string | null
  node_label: string | null
  question_count: number
  mastery: number
  should_generate_method: boolean
  method_id: string | null
}

export interface SourceItem {
  content: string
  source: string
  page: number | null
  score: number
}
