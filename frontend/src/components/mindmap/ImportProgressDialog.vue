<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  visible: boolean
  total: number
  completed: number
  results: Array<{
    contentPreview: string
    status: 'pending' | 'success' | 'failed'
    questionId?: string
    error?: string
  }>
}>()

const emit = defineEmits<{
  (e: 'update:visible', v: boolean): void
  (e: 'cancel'): void
}>()

const progress = computed(() => {
  if (props.total === 0) return 0
  return Math.round((props.completed / props.total) * 100)
})

const statusText = computed(() => {
  if (props.completed >= props.total) return '导入完成 🌿'
  return `正在悉心导入... ${props.completed} / ${props.total}`
})

function getStatusIcon(status: string): { name: string; color: string } {
  switch (status) {
    case 'success': return { name: 'mdi:check-circle-outline', color: 'var(--success-color)' }
    case 'failed': return { name: 'mdi:close-circle-outline', color: 'var(--accent-color)' }
    default: return { name: 'mdi:loading', color: 'var(--text-muted)' }
  }
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    title="导入进度"
    width="520px"
    :close-on-click-modal="false"
    :show-close="false"
    :close-on-press-escape="false"
  >
    <div class="progress-container">
      <div class="progress-status">{{ statusText }}</div>

      <el-progress
        :percentage="progress"
        :status="progress === 100 ? 'success' : undefined"
        :stroke-width="20"
        :text-inside="true"
      />

      <div class="progress-list">
        <div
          v-for="(item, idx) in results"
          :key="idx"
          class="progress-item"
          :class="`is-${item.status}`"
        >
          <span class="status-icon" :style="{ color: getStatusIcon(item.status).color }">
            <iconify-icon
              :icon="getStatusIcon(item.status).name"
              width="16"
              :class="{ 'spin': item.status === 'pending' }"
            ></iconify-icon>
          </span>
          <span class="item-preview">{{ item.contentPreview }}</span>
          <span class="item-status">{{ item.status === 'pending' ? '等待中' : item.status === 'success' ? '成功' : item.error || '失败' }}</span>
        </div>
      </div>
    </div>

    <template #footer>
      <el-button
        v-if="progress < 100"
        @click="emit('cancel')"
      >取消导入</el-button>
      <el-button
        v-else
        type="primary"
        @click="emit('update:visible', false)"
      >关闭</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.progress-container {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.progress-status {
  font-size: 16px;
  font-weight: 500;
  font-family: var(--font-heading);
  color: var(--text-primary);
  text-align: center;
}

.progress-container :deep(.el-progress-bar__outer) {
  background: var(--primary-bg);
  border-radius: var(--radius-full);
}

.progress-list {
  max-height: 320px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 4px;
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: var(--bg-surface);
  border: 2px solid var(--border-light);
  border-radius: var(--radius-hand-drawn-soft);
  font-size: 13px;
  transition: all var(--transition-fade);
  animation: fadeInUp var(--transition-fade) forwards;
}

.progress-item.is-success {
  background: var(--primary-bg);
  border-color: var(--primary-lighter);
}

.progress-item.is-failed {
  background: rgba(192, 105, 74, 0.08);
  border-color: rgba(192, 105, 74, 0.25);
}

.status-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.spin {
  animation: spin 1.2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.item-preview {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-primary);
  font-family: var(--font-heading);
}

.item-status {
  flex-shrink: 0;
  font-size: 12px;
  color: var(--text-secondary);
}

.is-failed .item-status {
  color: var(--accent-color);
}

.is-success .item-status {
  color: var(--success-color);
  font-weight: 500;
}
</style>
