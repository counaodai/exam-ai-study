export interface ApiResponse<T = unknown> {
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export type ModuleLevel = 1 | 2 | 3

export interface ModuleItem {
  id: string
  name: string
  parent_id: string | null
  level: ModuleLevel
  description: string | null
  sort_order: number
  is_preset: boolean
  children?: ModuleItem[]
}
