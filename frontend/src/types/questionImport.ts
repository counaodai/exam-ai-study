/** 题目导入相关类型定义 */

export interface ParsedQuestion {
  content: string
  options?: Record<string, string>
  answer?: string
  explanation?: string
  suggestedModuleId?: string
  suggestedModulePath?: string
  parseConfidence: number
}

export interface ImportQuestionItem {
  content: string
  options?: Record<string, string>
  answer?: string
  explanation?: string
  moduleId?: string
  secondaryModule?: string
}

export interface ImportProgress {
  taskId: string
  total: number
  completed: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  results: ImportProgressItem[]
}

export interface ImportProgressItem {
  contentPreview: string
  status: 'pending' | 'success' | 'failed'
  questionId?: string
  error?: string
}

export interface ParseQuestionsRequest {
  content: string
  format?: 'plain' | 'markdown'
}

export interface ParseQuestionsResponse {
  questions: ParsedQuestion[]
  parse_errors: Array<{
    index?: number
    error?: string
    message?: string
    content_preview?: string
    confidence?: number
  }>
}

export interface ImportQuestionsRequest {
  questions: ImportQuestionItem[]
  allow_duplicate?: boolean
}

export interface ImportQuestionsResponse {
  imported_count: number
  imported_ids: string[]
  failed: Array<{
    index?: number
    content_preview?: string
    reason?: string
    existing_question_id?: string
  }>
  mindmap_update?: {
    updated_nodes: Array<{
      node_id: string
      node_label: string
      node_level: number
      question_count: number
      mastery: number
    }>
    should_generate_methods: string[]
  } | null
}

export interface QuestionListItem {
  id: string
  content: string
  answer: string | null
  explanation: string | null
  source: string | null
  moduleId?: string
  moduleName?: string
  modulePath?: string
  difficulty: number | null
  mastery: number
  is_valid: boolean
  created_at: string
}

export interface QuestionListResponse {
  items: QuestionListItem[]
  total: number
  page: number
  page_size: number
}

export interface CheckDuplicateRequest {
  content: string
  mindmap_id: string
}

export interface CheckDuplicateResponse {
  is_duplicate: boolean
  existing_question_id: string | null
  existing_question_content: string | null
}
