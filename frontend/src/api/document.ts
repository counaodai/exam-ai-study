import request from './request'
import type { DocumentItem, DocumentChunk } from '@/types/document'

export interface UploadProgressCallback {
  onProgress?: (percent: number) => void
}

export function uploadDocument(
  file: File,
  module?: string,
  callbacks?: UploadProgressCallback,
) {
  const formData = new FormData()
  formData.append('file', file)
  if (module) {
    formData.append('module', module)
  }
  return request.post<any, DocumentItem>('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000,
    onUploadProgress: (progressEvent) => {
      if (callbacks?.onProgress && progressEvent.total) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        callbacks.onProgress(percent)
      }
    },
  })
}

export function getDocumentList() {
  return request.get<any, DocumentItem[]>('/documents')
}

export function deleteDocument(id: string) {
  return request.delete(`/documents/${id}`)
}

export function getDocumentChunks(id: string) {
  return request.get<any, DocumentChunk[]>(`/documents/${id}/chunks`, {
    timeout: 60000,
  })
}

export function getDocumentStatus(id: string) {
  return request.get<any, { id: string; status: string; chunk_count: number }>(
    `/documents/${id}/status`
  )
}

export function reprocessDocument(id: string) {
  return request.post<any, DocumentItem>(`/documents/${id}/reprocess`)
}
