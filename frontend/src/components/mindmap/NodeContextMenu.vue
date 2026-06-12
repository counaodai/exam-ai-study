<script setup lang="ts">
import type { NodeType } from '@/types/mindmap'

const props = defineProps<{
  visible: boolean
  position: { x: number; y: number }
  nodeType: NodeType
}>()

const emit = defineEmits<{
  (e: 'action', action: string): void
  (e: 'update:visible', val: boolean): void
}>()

const menuStyle = {
  position: 'fixed' as const,
  zIndex: 9999,
}

function handleAction(action: string) {
  emit('action', action)
  emit('update:visible', false)
}

function handleClickOutside() {
  emit('update:visible', false)
}
</script>

<template>
  <div v-if="visible" class="context-menu-overlay" @click="handleClickOutside" @contextmenu.prevent="handleClickOutside">
    <div
      class="context-menu"
      :style="{ ...menuStyle, left: `${position.x}px`, top: `${position.y}px` }"
      @click.stop
    >
      <div class="menu-item" @click="handleAction('add')">
        <iconify-icon icon="mdi:plus" width="18" class="menu-icon" />
        <span>添加子节点</span>
      </div>
      <div class="menu-item" @click="handleAction('edit')">
        <iconify-icon icon="mdi:pencil-outline" width="18" class="menu-icon" />
        <span>编辑节点名称</span>
      </div>
      <div class="menu-item" @click="handleAction('questions')">
        <iconify-icon icon="mdi:file-document-outline" width="18" class="menu-icon" />
        <span>查看关联题目</span>
      </div>
      <div class="menu-divider"></div>
      <div
        class="menu-item menu-item--danger"
        :class="{ 'menu-item--disabled': nodeType === 'module' }"
        @click="nodeType !== 'module' && handleAction('delete')"
      >
        <iconify-icon icon="mdi:trash-can-outline" width="18" class="menu-icon" />
        <span>删除节点</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.context-menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9998;
}

.context-menu {
  background: var(--bg-surface);
  border: 2px solid var(--border-light);
  border-radius: var(--radius-hand-drawn-soft);
  box-shadow: var(--shadow-md), var(--shadow-hand-drawn);
  padding: 8px 6px;
  min-width: 172px;
  font-family: var(--font-heading);
  animation: cardEnter var(--transition-bounce) both;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-primary, #4A3F2F);
  border-radius: var(--radius-hand-drawn-soft);
  transition: background-color 0.2s ease, color 0.2s ease, transform 0.2s ease;
  font-family: var(--font-heading);
}

.menu-icon {
  flex-shrink: 0;
  color: currentColor;
}

.menu-item:hover {
  background-color: var(--primary-bg);
  color: var(--primary-color);
  transform: translateX(2px);
}

.menu-item--danger {
  color: var(--accent-color);
}

.menu-item--danger:hover {
  background-color: rgba(192, 105, 74, 0.12);
  color: var(--accent-color);
}

.menu-item--disabled,
.menu-item--disabled:hover {
  color: #c0c4cc;
  cursor: not-allowed;
  background-color: transparent;
  transform: none;
}

.menu-divider {
  height: 1px;
  background-color: var(--border-light);
  margin: 6px 4px;
  opacity: 0.7;
}

@keyframes cardEnter {
  from {
    opacity: 0;
    transform: translateY(8px) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style>
