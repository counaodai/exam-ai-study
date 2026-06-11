import request from './request'
import type { MethodSummary } from '@/types/method'

export function getMethodList(moduleId?: string) {
  const params = moduleId ? { module_id: moduleId } : undefined
  return request.get<any, MethodSummary[]>('/methods', { params })
}

export function getMethodDetail(id: string) {
  return request.get<any, MethodSummary>(`/methods/${id}`)
}

export function generateMethod(moduleId: string) {
  return request.post<any, MethodSummary>('/methods/generate', { module_id: moduleId })
}

export function updateMethod(id: string, data: Partial<MethodSummary>) {
  return request.put<any, MethodSummary>(`/methods/${id}`, data)
}
