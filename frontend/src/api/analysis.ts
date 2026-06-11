import request from './request'

export interface OverviewStats {
  total_documents: number
  total_questions: number
  total_conversations: number
  total_methods: number
  method_coverage: number
}

export interface ModuleStats {
  module_name: string
  question_count: number
  avg_mastery: number
}

export interface SubModuleStats {
  module_name: string
  sub_module_name: string
  question_count: number
  avg_mastery: number
}

export interface TrendData {
  date: string
  count: number
}

export interface WeakPointStats {
  module_name: string
  sub_module_name: string
  question_count: number
  avg_mastery: number
}

export interface MethodCoverageStats {
  total_sub_modules: number
  covered_sub_modules: number
  coverage_rate: number
}

export function getOverviewStats() {
  return request.get<any, OverviewStats>('/analysis/overview')
}

export function getModuleStats() {
  return request.get<any, ModuleStats[]>('/analysis/modules')
}

export function getSubModuleStats(moduleName?: string) {
  const params = moduleName ? { module_name: moduleName } : undefined
  return request.get<any, SubModuleStats[]>('/analysis/sub-modules', { params })
}

export function getTrends(days?: number) {
  const params = days ? { days } : undefined
  return request.get<any, TrendData[]>('/analysis/trends', { params })
}

export function getWeakPoints(limit?: number) {
  const params = limit ? { limit } : undefined
  return request.get<any, WeakPointStats[]>('/analysis/weak-points', { params })
}

export function getMethodCoverage() {
  return request.get<any, MethodCoverageStats>('/analysis/method-coverage')
}