import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { DocumentItem, DocumentChunk, UploadQueueItem, UploadQueueStatus } from '@/types/document'
import * as documentApi from '@/api/document'

const MAX_CONCURRENT = 3
const MAX_RETRY = 2

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substring(2, 8)
}

export const useDocumentStore = defineStore('document', () => {
  const documents = ref<DocumentItem[]>([])
  const uploading = ref(false)
  const previewChunks = ref<DocumentChunk[]>([])
  const previewLoading = ref(false)
  const uploadQueue = ref<UploadQueueItem[]>([])

  const pollingTimers = new Map<string, ReturnType<typeof setInterval>>()

  const queueStats = computed(() => {
    const queue = uploadQueue.value
    return {
      total: queue.length,
      waiting: queue.filter((i) => i.status === 'waiting').length,
      uploading: queue.filter((i) => i.status === 'uploading').length,
      completed: queue.filter((i) => i.status === 'completed').length,
      failed: queue.filter((i) => i.status === 'failed').length,
      cancelled: queue.filter((i) => i.status === 'cancelled').length,
    }
  })

  const isQueueActive = computed(() => {
    return uploadQueue.value.some(
      (i) => i.status === 'waiting' || i.status === 'uploading',
    )
  })

  async function fetchDocuments() {
    documents.value = await documentApi.getDocumentList()
  }

  function addToQueue(files: File[]) {
    const items: UploadQueueItem[] = files.map((file) => ({
      id: generateId(),
      file,
      filename: file.name,
      file_size: file.size,
      status: 'waiting' as UploadQueueStatus,
      progress: 0,
      error: null,
      retryCount: 0,
    }))
    uploadQueue.value.push(...items)
    processQueue()
  }

  async function processQueue() {
    if (uploading.value) return

    const waitingItems = uploadQueue.value.filter((i) => i.status === 'waiting')
    const uploadingItems = uploadQueue.value.filter((i) => i.status === 'uploading')

    if (waitingItems.length === 0) return
    if (uploadingItems.length >= MAX_CONCURRENT) return

    uploading.value = true

    const availableSlots = MAX_CONCURRENT - uploadingItems.length
    const itemsToUpload = waitingItems.slice(0, availableSlots)

    const promises = itemsToUpload.map((item) => uploadSingleItem(item))

    await Promise.allSettled(promises)

    uploading.value = false

    const remaining = uploadQueue.value.filter((i) => i.status === 'waiting')
    if (remaining.length > 0) {
      processQueue()
    }
  }

  async function uploadSingleItem(item: UploadQueueItem) {
    item.status = 'uploading'
    item.progress = 0
    item.error = null

    try {
      const doc = await documentApi.uploadDocument(item.file, undefined, {
        onProgress: (percent) => {
          item.progress = percent
        },
      })

      item.progress = 100
      item.status = 'completed'

      documents.value.unshift(doc)
      startPollingStatus(doc.id)
    } catch (e: any) {
      const currentStatus = item.status as string
      if (currentStatus === 'cancelled') return

      if (item.retryCount < MAX_RETRY) {
        item.retryCount++
        item.status = 'waiting'
        item.error = `上传失败，${MAX_RETRY - item.retryCount + 1} 次重试机会`
        processQueue()
      } else {
        item.status = 'failed'
        item.error = e?.message || '上传失败，请重试'
      }
    }
  }

  function cancelQueueItem(id: string) {
    const item = uploadQueue.value.find((i) => i.id === id)
    if (!item) return

    if (item.status === 'uploading' || item.status === 'waiting') {
      item.status = 'cancelled'
    }
  }

  function retryQueueItem(id: string) {
    const item = uploadQueue.value.find((i) => i.id === id)
    if (!item || item.status !== 'failed') return

    item.status = 'waiting'
    item.progress = 0
    item.error = null
    item.retryCount = 0
    processQueue()
  }

  function cancelAllQueue() {
    uploadQueue.value.forEach((item) => {
      if (item.status === 'waiting' || item.status === 'uploading') {
        item.status = 'cancelled'
      }
    })
  }

  function clearFinishedQueue() {
    uploadQueue.value = uploadQueue.value.filter(
      (i) => i.status === 'waiting' || i.status === 'uploading',
    )
  }

  function clearQueue() {
    uploadQueue.value = []
  }

  async function deleteDocument(id: string) {
    stopPollingStatus(id)
    await documentApi.deleteDocument(id)
    documents.value = documents.value.filter((d) => d.id !== id)
  }

  async function reprocessDocument(id: string) {
    const doc = await documentApi.reprocessDocument(id)
    const index = documents.value.findIndex((d) => d.id === id)
    if (index !== -1) {
      documents.value[index] = doc
    }
    startPollingStatus(id)
    return doc
  }

  function startPollingStatus(docId: string) {
    stopPollingStatus(docId)
    const timer = setInterval(async () => {
      try {
        const status = await documentApi.getDocumentStatus(docId)
        const doc = documents.value.find((d) => d.id === docId)
        if (doc) {
          doc.status = status.status as any
          doc.chunk_count = status.chunk_count
        }
        if (status.status === 'completed' || status.status === 'failed') {
          stopPollingStatus(docId)
        }
      } catch {
        stopPollingStatus(docId)
      }
    }, 2000)
    pollingTimers.set(docId, timer)
  }

  function stopPollingStatus(docId: string) {
    const timer = pollingTimers.get(docId)
    if (timer) {
      clearInterval(timer)
      pollingTimers.delete(docId)
    }
  }

  function startPollingAll() {
    for (const doc of documents.value) {
      if (doc.status === 'pending' || doc.status === 'processing') {
        startPollingStatus(doc.id)
      }
    }
  }

  async function fetchChunks(docId: string) {
    previewLoading.value = true
    try {
      previewChunks.value = await documentApi.getDocumentChunks(docId)
    } finally {
      previewLoading.value = false
    }
  }

  function clearChunks() {
    previewChunks.value = []
  }

  return {
    documents,
    uploading,
    previewChunks,
    previewLoading,
    uploadQueue,
    queueStats,
    isQueueActive,
    fetchDocuments,
    addToQueue,
    cancelQueueItem,
    retryQueueItem,
    cancelAllQueue,
    clearFinishedQueue,
    clearQueue,
    deleteDocument,
    reprocessDocument,
    startPollingStatus,
    stopPollingStatus,
    startPollingAll,
    fetchChunks,
    clearChunks,
  }
})
