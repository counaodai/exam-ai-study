export const APP_NAME = '公考AI智能学习系统'

export const MODULE_NAMES = [
  '言语理解与表达',
  '数量关系',
  '判断推理',
  '资料分析',
  '常识判断',
] as const

export type PrimaryModule = (typeof MODULE_NAMES)[number]

export const STATUS_MAP: Record<string, { label: string; type: string }> = {
  pending: { label: '待处理', type: 'info' },
  processing: { label: '解析中', type: 'warning' },
  completed: { label: '已完成', type: 'success' },
  failed: { label: '失败', type: 'danger' },
}

export const MASTERY_COLORS = {
  low: '#f56c6c',
  medium: '#e6a23c',
  high: '#67c23a',
} as const
