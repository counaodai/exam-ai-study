<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadFile } from 'element-plus'
import {
  Upload as UploadIcon,
  FolderOpened,
  Close,
  RefreshRight,
} from '@element-plus/icons-vue'
import { formatFileSize } from '@/utils/format'
import { STATUS_MAP } from '@/utils/constants'
import { useDocumentStore } from '@/stores/document'
import { MODULE_NAMES } from '@/utils/constants'
import ChunkPreview from '@/components/upload/ChunkPreview.vue'

const documentStore = useDocumentStore()
const selectedModule = ref('')
const previewDialogVisible = ref(false)
const previewDocName = ref('')
const folderInputRef = ref<HTMLInputElement | null>(null)

const ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.doc', '.txt', '.md']

onMounted(() => {
  documentStore.fetchDocuments().then(() => {
    documentStore.startPollingAll()
  })
})

onBeforeUnmount(() => {
  for (const doc of documentStore.documents) {
    documentStore.stopPollingStatus(doc.id)
  }
})

function isAllowedFile(filename: string): boolean {
  const ext = '.' + filename.split('.').pop()?.toLowerCase()
  return ALLOWED_EXTENSIONS.includes(ext)
}

function handleFilesSelected(uploadFile: UploadFile) {
  if (!uploadFile.raw) return
  const files = [uploadFile.raw]
  documentStore.addToQueue(files, selectedModule.value)
}

function triggerFolderUpload() {
  if (!folderInputRef.value) {
    const input = document.createElement('input')
    input.type = 'file'
    input.setAttribute('webkitdirectory', '')
    input.setAttribute('directory', '')
    input.multiple = true
    input.accept = ALLOWED_EXTENSIONS.join(',')
    input.style.display = 'none'
    input.addEventListener('change', handleFolderSelected)
    document.body.appendChild(input)
    folderInputRef.value = input
  }
  folderInputRef.value.click()
}

function handleFolderSelected(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files) return

  const files: File[] = []
  for (let i = 0; i < input.files.length; i++) {
    const file = input.files[i]
    if (isAllowedFile(file.name)) {
      files.push(file)
    }
  }

  if (files.length === 0) {
    ElMessage.warning('所选文件夹中没有支持的文件格式')
    return
  }

  const skipped = input.files.length - files.length
  if (skipped > 0) {
    ElMessage.info(`已过滤 ${skipped} 个不支持的文件`)
  }

  documentStore.addToQueue(files, selectedModule.value)
  ElMessage.success(`已添加 ${files.length} 个文件到上传队列`)
  input.value = ''
}

function handleDelete(id: string) {
  documentStore.deleteDocument(id)
  ElMessage.success('删除成功')
}

function handleReprocess(id: string) {
  documentStore.reprocessDocument(id)
  ElMessage.success('已重新触发处理，请稍候...')
}

async function handlePreviewChunks(id: string, filename: string) {
  previewDocName.value = filename
  previewDialogVisible.value = true
  await documentStore.fetchChunks(id)
}

function handlePreviewClose() {
  previewDialogVisible.value = false
  documentStore.clearChunks()
}

function getStatusType(status: string): string {
  const map: Record<string, string> = {
    waiting: 'info',
    uploading: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info',
  }
  return map[status] || 'info'
}

function getStatusLabel(status: string): string {
  const map: Record<string, string> = {
    waiting: '等待中',
    uploading: '上传中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消',
  }
  return map[status] || status
}
</script>

<template>
  <div class="upload-page">
    <h1>
      <iconify-icon icon="mdi:sprout-outline" width="28" class="title-icon" />
      文档导入
    </h1>

    <el-card class="upload-card">
      <div class="upload-actions">
        <el-upload
          multiple
          :auto-upload="false"
          :on-change="handleFilesSelected"
          accept=".pdf,.docx,.doc,.txt,.md"
          :show-file-list="false"
        >
          <el-button type="primary" :icon="UploadIcon" :disabled="documentStore.isQueueActive">
            选择文件（支持多选）
          </el-button>
        </el-upload>
        <el-button
          :icon="FolderOpened"
          @click="triggerFolderUpload"
          :disabled="documentStore.isQueueActive"
        >
          上传文件夹
        </el-button>
      </div>

      <el-upload
        drag
        multiple
        :auto-upload="false"
        :on-change="handleFilesSelected"
        accept=".pdf,.docx,.doc,.txt,.md"
        :disabled="documentStore.isQueueActive"
        class="drag-upload"
      >
        <iconify-icon icon="mdi:leaf-circle-outline" width="48" class="drag-leaf-icon" />
        <div class="el-upload__text">
          拖拽文件到这里，一次上传一堆
        </div>
        <template #tip>
          <div class="el-upload__tip">支持 PDF / Word / TXT / Markdown，单文件最大 50MB</div>
        </template>
      </el-upload>

      <div class="module-select">
        <span>归属模块（可选）：</span>
        <el-select v-model="selectedModule" placeholder="请选择模块" clearable style="width: 200px">
          <el-option v-for="m in MODULE_NAMES" :key="m" :label="m" :value="m" />
        </el-select>
      </div>
    </el-card>

    <el-card v-if="documentStore.uploadQueue.length > 0" class="queue-card">
      <template #header>
        <div class="queue-header">
          <span>上传队列</span>
          <div class="queue-stats">
            <el-tag size="small" type="info">
              共 {{ documentStore.queueStats.total }} 个
            </el-tag>
            <el-tag v-if="documentStore.queueStats.uploading > 0" size="small" type="warning">
              上传中 {{ documentStore.queueStats.uploading }}
            </el-tag>
            <el-tag v-if="documentStore.queueStats.completed > 0" size="small" type="success">
              完成 {{ documentStore.queueStats.completed }}
            </el-tag>
            <el-tag v-if="documentStore.queueStats.failed > 0" size="small" type="danger">
              失败 {{ documentStore.queueStats.failed }}
            </el-tag>
          </div>
          <div class="queue-actions">
            <el-button
              v-if="documentStore.isQueueActive"
              type="danger"
              size="small"
              :icon="Close"
              @click="documentStore.cancelAllQueue()"
            >
              全部取消
            </el-button>
            <el-button
              v-if="!documentStore.isQueueActive && documentStore.queueStats.completed > 0"
              size="small"
              @click="documentStore.clearFinishedQueue()"
            >
              清除已完成
            </el-button>
          </div>
        </div>
      </template>

      <div class="queue-list">
        <div
          v-for="item in documentStore.uploadQueue"
          :key="item.id"
          class="queue-item"
          :class="item.status"
        >
          <div class="queue-item-info">
            <span class="queue-item-name">{{ item.filename }}</span>
            <span class="queue-item-size">{{ formatFileSize(item.file_size) }}</span>
          </div>
          <div class="queue-item-progress">
            <el-progress
              v-if="item.status === 'uploading'"
              :percentage="Math.min(Math.round(item.progress), 100)"
              :stroke-width="6"
              :status="item.progress >= 100 ? 'success' : undefined"
            />
            <el-tag
              v-else
              :type="getStatusType(item.status) as any"
              size="small"
            >
              {{ getStatusLabel(item.status) }}
            </el-tag>
          </div>
          <div v-if="item.error" class="queue-item-error">
            {{ item.error }}
          </div>
          <div class="queue-item-actions">
            <el-button
              v-if="item.status === 'failed'"
              type="primary"
              size="small"
              link
              :icon="RefreshRight"
              @click="documentStore.retryQueueItem(item.id)"
            >
              重试
            </el-button>
            <el-button
              v-if="item.status === 'waiting' || item.status === 'uploading'"
              type="danger"
              size="small"
              link
              :icon="Close"
              @click="documentStore.cancelQueueItem(item.id)"
            >
              取消
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <el-card class="list-card">
      <template #header>
        <span>已导入文档</span>
      </template>
      <el-table :data="documentStore.documents" style="width: 100%">
        <el-table-column prop="filename" label="文件名" min-width="200" />
        <el-table-column label="大小" width="100">
          <template #default="{ row }">{{ formatFileSize(row.file_size) }}</template>
        </el-table-column>
        <el-table-column prop="module" label="模块" width="140">
          <template #default="{ row }">{{ row.module || '-' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <div class="status-cell">
              <el-tag :type="STATUS_MAP[row.status]?.type as any">
                {{ STATUS_MAP[row.status]?.label }}
              </el-tag>
              <el-progress
                v-if="row.status === 'processing'"
                :percentage="100"
                :indeterminate="true"
                :show-text="false"
                :stroke-width="3"
                style="width: 80px"
              />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="chunk_count" label="分块数" width="80" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'completed'"
              type="primary"
              link
              @click="handlePreviewChunks(row.id, row.filename)"
            >
              预览
            </el-button>
            <el-button
              v-if="row.status === 'pending' || row.status === 'failed'"
              type="warning"
              link
              @click="handleReprocess(row.id)"
            >
              重新处理
            </el-button>
            <el-button type="danger" link @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="previewDialogVisible"
      :title="`分块预览 - ${previewDocName}`"
      width="800px"
      @close="handlePreviewClose"
    >
      <ChunkPreview
        :chunks="documentStore.previewChunks"
        :loading="documentStore.previewLoading"
      />
    </el-dialog>
  </div>
</template>

<style scoped>
.upload-page {
  animation: fadeIn var(--transition-fade);
}

.upload-page h1 {
  margin-bottom: 24px;
  font-family: var(--font-display);
  font-size: 28px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--text-primary);
}

.title-icon {
  color: var(--primary-color);
  background: var(--primary-bg);
  padding: 6px;
  border-radius: var(--radius-hand-drawn-soft);
  box-sizing: content-box;
}

.upload-card {
  margin-bottom: 20px;
  overflow: hidden;
  border-radius: var(--radius-hand-drawn) !important;
}

.upload-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.drag-upload {
  width: 100%;
}

.drag-upload :deep(.el-upload) {
  width: 100%;
}

.drag-upload :deep(.el-upload-dragger) {
  width: 100%;
  padding: 48px 0;
  border: 2px dashed var(--primary-lighter);
  border-radius: var(--radius-hand-drawn);
  transition: all var(--transition-fade);
  background: linear-gradient(135deg, var(--primary-bg) 0%, var(--bg-surface) 100%);
}

.drag-upload :deep(.el-upload-dragger:hover) {
  border-color: var(--primary-color);
  background: linear-gradient(135deg, var(--primary-bg) 0%, var(--bg-surface) 100%);
  box-shadow: 0 0 0 4px rgba(91, 140, 90, 0.12);
  transition: all var(--transition-hover-lift);
}

.drag-leaf-icon {
  color: var(--primary-color);
  margin-bottom: 16px;
  opacity: 0.85;
  display: block;
  margin-left: auto;
  margin-right: auto;
}

.drag-upload :deep(.el-upload__text) {
  font-size: 15px;
  font-family: var(--font-heading);
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.drag-upload :deep(.el-upload__tip) {
  font-size: 13px;
  color: var(--text-muted);
}

.module-select {
  margin-top: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding-top: 16px;
  border-top: 1px solid var(--border-light);
  font-family: var(--font-heading);
}

.queue-card {
  margin-bottom: 20px;
  overflow: hidden;
  border-radius: var(--radius-hand-drawn) !important;
}

.queue-header {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  font-family: var(--font-heading);
}

.queue-stats {
  display: flex;
  gap: 6px;
  flex: 1;
}

.queue-actions {
  display: flex;
  gap: 8px;
}

.queue-list {
  max-height: 320px;
  overflow-y: auto;
}

.queue-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 14px;
  border-bottom: 1px solid var(--border-light);
  flex-wrap: wrap;
  transition: all var(--transition-fade);
  border-radius: var(--radius-hand-drawn-soft);
  margin-bottom: 4px;
}

.queue-item:last-child {
  border-bottom: none;
}

.queue-item:hover {
  background: var(--bg-muted);
  transition: all var(--transition-hover-lift);
}

.queue-item.completed {
  background: linear-gradient(90deg, rgba(91, 140, 90, 0.10) 0%, transparent 100%);
}

.queue-item.failed {
  background: linear-gradient(90deg, rgba(192, 105, 74, 0.10) 0%, transparent 100%);
}

.queue-item.cancelled {
  background: var(--bg-muted);
  opacity: 0.7;
}

.queue-item-info {
  flex: 1;
  min-width: 150px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.queue-item-name {
  font-size: 14px;
  font-family: var(--font-heading);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 320px;
  color: var(--text-primary);
  font-weight: 500;
}

.queue-item-size {
  font-size: 12px;
  color: var(--text-muted);
  flex-shrink: 0;
  background: var(--bg-muted);
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.queue-item-progress {
  width: 140px;
  flex-shrink: 0;
}

.queue-item-error {
  width: 100%;
  font-size: 12px;
  color: var(--el-color-danger);
  padding-left: 0;
  background: rgba(192, 105, 74, 0.08);
  padding: 6px 10px;
  border-radius: var(--radius-hand-drawn-soft);
  margin-top: 4px;
}

.queue-item-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.list-card {
  margin-top: 20px;
  overflow: hidden;
  border-radius: var(--radius-hand-drawn) !important;
}

.status-cell {
  display: flex;
  flex-direction: column;
  gap: 6px;
  align-items: flex-start;
}

:deep(.el-table) {
  border-radius: var(--radius-hand-drawn);
  overflow: hidden;
}

:deep(.el-table th.el-table__cell) {
  background: var(--bg-muted) !important;
  font-weight: 600;
  font-family: var(--font-heading);
}

:deep(.el-table .cell) {
  font-family: var(--font-heading);
}

:deep(.el-table td.el-table__cell) {
  transition: background-color var(--transition-fade);
}

:deep(.el-table body tr:hover > td) {
  background-color: rgba(91, 140, 90, 0.08) !important;
}
</style>
