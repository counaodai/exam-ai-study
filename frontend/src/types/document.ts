export type DocumentStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface DocumentItem {
  id: string
  filename: string
  file_type: string
  file_size: number
  file_path: string
  module: string | null
  status: DocumentStatus
  chunk_count: number
  created_at: string
  updated_at: string
}

export interface DocumentChunk {
  id: string
  content: string
  source: string
  module: string | null
  chunk_type: 'question' | 'knowledge' | 'method'
  metadata: ChunkMetadata
}

export interface ChunkMetadata {
  page: number | null
  chapter: string | null
  question_number: number | null
  year: string | null
  tags: string[]
}

export type UploadQueueStatus = 'waiting' | 'uploading' | 'completed' | 'failed' | 'cancelled'

export interface UploadQueueItem {
  id: string
  file: File
  filename: string
  file_size: number
  status: UploadQueueStatus
  progress: number
  error: string | null
  retryCount: number
}
