/** 题目导入相关 API */
import request from './request'
import type {
  ParseQuestionsRequest,
  ParseQuestionsResponse,
  ImportQuestionsRequest,
  ImportQuestionsResponse,
  QuestionListResponse,
  CheckDuplicateRequest,
  CheckDuplicateResponse,
} from '@/types/questionImport'

// ===== 题目列表 =====

export function getQuestionList(params?: {
  page?: number
  page_size?: number
  module_id?: string
  keyword?: string
  is_valid?: boolean
}) {
  return request.get<any, QuestionListResponse>('/questions', { params })
}

// ===== 题目解析 =====

export function parseQuestions(data: ParseQuestionsRequest) {
  return request.post<any, ParseQuestionsResponse>('/questions/parse', data)
}

// ===== 解析后导入 =====

export function importParsedQuestions(data: ImportQuestionsRequest) {
  return request.post<any, ImportQuestionsResponse>('/questions/import-parsed', data)
}

// ===== 导入到思维导图 =====

export function importQuestionsToMindmap(mapId: string, data: ImportQuestionsRequest) {
  return request.post<any, ImportQuestionsResponse>(`/mindmaps/${mapId}/import-questions`, data)
}

// ===== 去重检查 =====

export function checkDuplicate(data: CheckDuplicateRequest) {
  return request.post<any, CheckDuplicateResponse>('/questions/check-duplicate', data)
}
