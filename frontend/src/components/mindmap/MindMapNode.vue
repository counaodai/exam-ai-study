<script setup lang="ts">
import { computed, ref, nextTick } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import { Document, TrendCharts, Trophy } from '@element-plus/icons-vue'
import type { NodeType } from '@/types/mindmap'

interface Props {
  id: string
  data: {
    label: string
    type: NodeType
    question_count: number
    mastery: number
    method_id?: string | null
    highlight?: boolean
  }
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'contextmenu', payload: { nodeId: string; event: MouseEvent }): void
  (e: 'labelChange', payload: { nodeId: string; label: string }): void
  (e: 'nodeClick', nodeId: string): void
}>()

const isEditing = ref(false)
const editValue = ref('')
const editInputRef = ref<HTMLInputElement | null>(null)

const typeColors: Record<NodeType, string> = {
  module: '#409EFF',
  topic: '#67C23A',
  method: '#E6A23C',
  question: '#909399',
}

const typeLabels: Record<NodeType, string> = {
  module: '模块',
  topic: '主题',
  method: '方法',
  question: '题目',
}

const nodeColor = computed(() => {
  if (props.data.method_id) return '#E6A23C'
  return typeColors[props.data.type] || '#409EFF'
})

const typeLabel = computed(() => typeLabels[props.data.type] || '未知')

const masteryColor = computed(() => {
  if (props.data.mastery >= 80) return '#67C23A'
  if (props.data.mastery >= 60) return '#E6A23C'
  return '#F56C6C'
})

const hasMethod = computed(() => !!props.data.method_id)

function handleDblClick() {
  editValue.value = props.data.label
  isEditing.value = true
  nextTick(() => {
    editInputRef.value?.focus()
    editInputRef.value?.select()
  })
}

function handleEditConfirm() {
  const trimmed = editValue.value.trim()
  if (trimmed && trimmed !== props.data.label) {
    emit('labelChange', { nodeId: props.id, label: trimmed })
  }
  isEditing.value = false
}

function handleEditCancel() {
  isEditing.value = false
}

function handleContextMenu(event: MouseEvent) {
  event.preventDefault()
  event.stopPropagation()
  emit('contextmenu', { nodeId: props.id, event })
}

function handleClick() {
  emit('nodeClick', props.id)
}
</script>

<template>
  <div
    class="mind-map-node"
    :class="{ 'has-method': hasMethod, 'is-highlighted': data.highlight }"
    :style="{ borderColor: nodeColor }"
    @dblclick.stop="handleDblClick"
    @contextmenu.stop="handleContextMenu"
    @click.stop="handleClick"
  >
    <Handle type="target" :position="Position.Top" :connectable="true" />

    <div class="node-header" :style="{ backgroundColor: nodeColor }">
      <span class="type-tag">{{ typeLabel }}</span>
      <el-icon v-if="hasMethod" class="method-icon"><Trophy /></el-icon>
    </div>

    <div class="node-body">
      <div v-if="!isEditing" class="node-label">{{ data.label }}</div>
      <input
        v-else
        ref="editInputRef"
        v-model="editValue"
        class="label-edit-input"
        @keyup.enter="handleEditConfirm"
        @keyup.escape="handleEditCancel"
        @blur="handleEditConfirm"
      />
      <div v-if="hasMethod" class="method-badge">
        <el-tag type="warning" size="small" effect="dark">
          已生成方法论
        </el-tag>
      </div>
      <div class="node-stats">
        <span class="stat-item">
          <el-icon><Document /></el-icon>
          {{ data.question_count }}题
        </span>
        <span class="stat-item" :style="{ color: masteryColor }">
          <el-icon><TrendCharts /></el-icon>
          {{ data.mastery }}%
        </span>
      </div>
    </div>

    <Handle type="source" :position="Position.Bottom" :connectable="true" />
  </div>
</template>

<style scoped>
.mind-map-node {
  background: #fff;
  border: 2px solid;
  border-radius: 8px;
  min-width: 160px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.2s;
}

.mind-map-node:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.mind-map-node.has-method {
  border-width: 3px;
  box-shadow: 0 2px 12px rgba(230, 162, 60, 0.3);
}

.mind-map-node.has-method:hover {
  box-shadow: 0 4px 20px rgba(230, 162, 60, 0.5);
}

.mind-map-node.is-highlighted {
  animation: highlight-pulse 1.4s ease-in-out infinite;
  box-shadow: 0 0 0 3px rgba(245, 108, 108, 0.4), 0 4px 16px rgba(245, 108, 108, 0.3);
}

@keyframes highlight-pulse {
  0%, 100% {
    box-shadow: 0 0 0 3px rgba(245, 108, 108, 0.4), 0 4px 16px rgba(245, 108, 108, 0.3);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(245, 108, 108, 0.15), 0 4px 20px rgba(245, 108, 108, 0.5);
  }
}

.node-header {
  padding: 6px 10px;
  border-radius: 6px 6px 0 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.type-tag {
  color: #fff;
  font-size: 12px;
  font-weight: 600;
}

.method-icon {
  color: #fff;
  font-size: 14px;
}

.node-body {
  padding: 10px;
}

.node-label {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
  word-break: break-word;
}

.label-edit-input {
  width: 100%;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  border: 1px solid #409eff;
  border-radius: 4px;
  padding: 4px 6px;
  margin-bottom: 8px;
  outline: none;
  box-sizing: border-box;
  background: #f0f7ff;
}

.method-badge {
  margin-bottom: 8px;
}

.node-stats {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
