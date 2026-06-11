<script setup lang="ts">
import { ref, computed } from 'vue'

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
  if (props.completed >= props.total) return '导入完成'
  return `正在导入... ${props.completed}/${props.total}`
})

function getStatusIcon(status: string) {
  switch (status) {
    case 'success': return '✅'
    case 'failed': return '❌'
    default: return '⏳'
  }
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    title="导入进度"
    width="500px"
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
        >
          <span class="status-icon">{{ getStatusIcon(item.status) }}</span>
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
  gap: 16px;
}

.progress-status {
  font-size: 16px;
  font-weight: 500;
  text-align: center;
}

.progress-list {
  max-height: 300px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  background: var(--el-bg-color-page);
  border-radius: 6px;
  font-size: 13px;
}

.status-icon {
  flex-shrink: 0;
}

.item-preview {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--el-text-color-primary);
}

.item-status {
  flex-shrink: 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
</style>
