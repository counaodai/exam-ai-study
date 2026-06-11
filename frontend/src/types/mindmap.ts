export type NodeType = 'module' | 'topic' | 'method' | 'question'

export interface MindMapNode {
  id: string
  label: string
  type: NodeType
  parent_id: string | null
  level: number
  question_count: number
  mastery: number
  content: string | null
  metadata: NodeMetadata
  position: NodePosition
}

export interface NodeMetadata {
  is_auto_generated: boolean
  source_questions: string[]
  method_summary: string | null
}

export interface NodePosition {
  x: number
  y: number
}

export interface MindMap {
  id: string
  title: string
  root_module: string
  nodes: MindMapNode[]
  edges: MindMapEdge[]
  created_at: string
  updated_at: string
}

export type EdgeType = 'default' | 'straight' | 'step' | 'smoothstep'

export interface MindMapEdge {
  id: string
  source: string
  target: string
  edge_type?: EdgeType
  color?: string
  stroke_width?: number
  has_arrow?: boolean
  animated?: boolean
  label?: string | null
  is_derived?: boolean
}

export interface CreateEdgeRequest {
  source: string
  target: string
  edge_type?: EdgeType
  color?: string
  stroke_width?: number
  has_arrow?: boolean
  animated?: boolean
  label?: string | null
}

export interface UpdateEdgeRequest {
  source?: string
  target?: string
  edge_type?: EdgeType
  color?: string
  stroke_width?: number
  has_arrow?: boolean
  animated?: boolean
  label?: string | null
}

export interface CreateNodeRequest {
  label: string
  type?: NodeType
  parent_id?: string | null
  content?: string
}

export interface UpdateNodeRequest {
  label?: string
  content?: string
  position_x?: number
  position_y?: number
  parent_id?: string | null
}

export interface NodeQuestionItem {
  id: string
  content: string
  answer: string | null
  explanation: string | null
  source: string | null
  difficulty: number | null
  mastery: number
  created_at: string
}

export interface NodeQuestionsResponse {
  total: number
  page: number
  page_size: number
  items: NodeQuestionItem[]
}
