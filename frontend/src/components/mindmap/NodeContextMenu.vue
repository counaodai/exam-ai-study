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
        <el-icon><Plus /></el-icon>
        <span>添加子节点</span>
      </div>
      <div class="menu-item" @click="handleAction('edit')">
        <el-icon><Edit /></el-icon>
        <span>编辑节点名称</span>
      </div>
      <div class="menu-item" @click="handleAction('questions')">
        <el-icon><Document /></el-icon>
        <span>查看关联题目</span>
      </div>
      <div class="menu-divider"></div>
      <div
        class="menu-item"
        :class="{ 'menu-item--disabled': nodeType === 'module' }"
        @click="nodeType !== 'module' && handleAction('delete')"
      >
        <el-icon><Delete /></el-icon>
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
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  padding: 6px 0;
  min-width: 160px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  color: #303133;
  transition: background-color 0.2s;
}

.menu-item:hover {
  background-color: #f5f7fa;
}

.menu-item--disabled {
  color: #c0c4cc;
  cursor: not-allowed;
}

.menu-item--disabled:hover {
  background-color: transparent;
}

.menu-divider {
  height: 1px;
  background-color: #ebeef5;
  margin: 4px 0;
}
</style>
