<script setup lang="ts">
import { computed, ref, nextTick } from 'vue'
import { Handle, Position } from '@vue-flow/core'
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

// 节点类型颜色（自然治愈风：苔藓绿/暖沙/陶土橙/暖灰棕）
const typeColors: Record<NodeType, string> = {
  module: 'var(--primary-color)',
  topic: 'var(--warning-color)',
  method: 'var(--accent-color)',
  question: 'var(--text-secondary)',
}

const typeLabels: Record<NodeType, string> = {
  module: '模块',
  topic: '主题',
  method: '方法',
  question: '题目',
}

// 类型对应的 Iconify 图标
const typeIcons: Record<NodeType, string> = {
  module: 'mdi:view-grid-outline',
  topic: 'mdi:leaf-circle-outline',
  method: 'mdi:lightbulb-on-outline',
  question: 'mdi:help-circle-outline',
}

const nodeColor = computed(() => {
  if (props.data.method_id) return 'var(--accent-color)'
  return typeColors[props.data.type] || 'var(--primary-color)'
})

const typeLabel = computed(() => typeLabels[props.data.type] || '未知')
const typeIcon = computed(() => typeIcons[props.data.type] || 'mdi:circle-outline')

const masteryColor = computed(() => {
  if (props.data.mastery >= 80) return 'var(--success-color)'
  if (props.data.mastery >= 60) return 'var(--warning-color)'
  return 'var(--accent-color)'
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
    <Handle type="target" :position="Position.Top" :connectable="true" class="hand-drawn-handle" />

    <div class="node-header" :style="{ backgroundColor: nodeColor }">
      <span class="type-tag">
        <iconify-icon :icon="typeIcon" width="14" class="type-icon" />
        {{ typeLabel }}
      </span>
      <iconify-icon
        v-if="hasMethod"
        icon="mdi:trophy-outline"
        width="16"
        class="method-icon"
      />
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
          <iconify-icon icon="mdi:file-document-outline" width="14" />
          <span class="stat-num">{{ data.question_count }}</span>
          <span class="stat-unit">题</span>
        </span>
        <span class="stat-item" :style="{ color: masteryColor }">
          <iconify-icon icon="mdi:chart-line-variant" width="14" />
          <span class="stat-num">{{ data.mastery }}</span>
          <span class="stat-unit">%</span>
        </span>
      </div>
    </div>

    <Handle type="source" :position="Position.Bottom" :connectable="true" class="hand-drawn-handle" />
  </div>
</template>

<style scoped>
/* —— 节点容器：手绘描边 + 暖米白底 —— */
.mind-map-node {
  background: var(--bg-surface, #fff);
  border: 2px solid var(--primary-color);
  border-radius: var(--radius-hand-drawn-soft);
  min-width: 168px;
  box-shadow: 0 2px 8px rgba(74, 63, 47, 0.08);
  transition: all var(--transition-hover-lift);
  overflow: hidden;
  font-family: var(--font-heading);
  color: var(--text-primary);
}

.mind-map-node:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(74, 63, 47, 0.18);
}

.mind-map-node.has-method {
  border-width: 2px;
  border-color: var(--accent-color);
  box-shadow: 0 2px 12px rgba(192, 105, 74, 0.22);
}

.mind-map-node.has-method:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 22px rgba(192, 105, 74, 0.35);
}

/* —— 高亮态：苔藓绿光晕 + 轻微脉动 —— */
.mind-map-node.is-highlighted {
  animation: highlight-pulse 1.6s ease-in-out infinite;
  box-shadow:
    0 0 0 3px rgba(91, 140, 90, 0.3),
    0 4px 16px rgba(91, 140, 90, 0.25);
}

@keyframes highlight-pulse {
  0%, 100% {
    box-shadow:
      0 0 0 3px rgba(91, 140, 90, 0.3),
      0 4px 16px rgba(91, 140, 90, 0.25);
  }
  50% {
    box-shadow:
      0 0 0 7px rgba(91, 140, 90, 0.12),
      0 6px 20px rgba(91, 140, 90, 0.4);
  }
}

/* —— 节点头部 —— */
.node-header {
  padding: 6px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1.5px dashed rgba(255, 255, 255, 0.35);
}

.type-tag {
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  font-family: var(--font-heading);
  letter-spacing: 0.3px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.type-icon {
  vertical-align: middle;
}

.method-icon {
  color: #fff;
}

/* —— 节点主体 —— */
.node-body {
  padding: 10px 12px 12px;
  background: var(--bg-surface, #fff);
}

.node-label {
  font-size: 14px;
  font-weight: 600;
  font-family: var(--font-heading);
  color: var(--text-primary);
  margin-bottom: 8px;
  word-break: break-word;
  line-height: 1.4;
}

/* —— 标签编辑输入框 —— */
.label-edit-input {
  width: 100%;
  font-size: 14px;
  font-weight: 600;
  font-family: var(--font-heading);
  color: var(--text-primary);
  border: 2px solid var(--primary-color);
  border-radius: var(--radius-hand-drawn-soft);
  padding: 5px 8px;
  margin-bottom: 8px;
  outline: none;
  box-sizing: border-box;
  background: var(--bg-muted);
}

.method-badge {
  margin-bottom: 8px;
}

/* —— 统计区 —— */
.node-stats {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-secondary);
  padding-top: 6px;
  border-top: 1.5px dashed var(--border-color);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 3px;
  font-family: var(--font-heading);
}

.stat-num {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  line-height: 1;
}

.stat-unit {
  font-size: 11px;
  opacity: 0.8;
}

/* —— Vue-Flow 连接句柄手绘化 —— */
:deep(.vue-flow__handle),
.hand-drawn-handle {
  width: 10px;
  height: 10px;
  background: var(--primary-color);
  border: 2px solid var(--bg-surface, #fff);
  box-shadow: 0 1px 3px rgba(74, 63, 47, 0.2);
  transition: transform var(--transition-hover-lift);
}

:deep(.vue-flow__handle):hover,
.hand-drawn-handle:hover {
  transform: scale(1.5);
  background: var(--accent-color);
}
</style>
