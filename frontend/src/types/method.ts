export interface MethodSummary {
  id: string
  module_id: string
  method_name: string
  recognition: MethodRecognition
  steps: MethodStep[]
  traps: MethodTrap[]
  quick_tips: string[]
  key_formulas: string[]
  summary: string
  question_count: number
  source_question_ids: string[]
  is_auto_generated: boolean
  created_at: string
  updated_at: string
}

export interface MethodRecognition {
  title: string
  content: string
}

export interface MethodStep {
  step: number
  title: string
  description: string
  example: string
}

export interface MethodTrap {
  trap: string
  solution: string
}
