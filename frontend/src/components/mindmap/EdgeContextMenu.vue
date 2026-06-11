<script setup lang="ts">
import type { EdgeType } from '@/types/mindmap'

defineProps<{
  visible: boolean
  position: { x: number; y: number }
  edgeId: string
  hasArrow: boolean
  animated: boolean
  currentType: EdgeType
  currentColor: string
}>()

const emit = defineEmits<{
  (e: 'update:visible', val: boolean): void
  (e: 'action', payload: { type: string; value?: any }): void
}>()

// 预设颜色（与系统色调一致）
const colorList = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#8B5CF6']

const typeOptions: { label: string; value: EdgeType }[] = [
  { label: '贝塞尔曲线', value: 'default' },
  { label: '直线', value: 'straight' },
  { label: '折线', value: 'step' },
  { label: '圆角折线', value: 'smoothstep' },
]

function handle(action: string, value?: any) {
  emit('action', { type: action, value })
  emit('update:visible', false)
}

function close() {
  emit('update:visible', false)
}
</script>

<template>
  <div v-if="visible" class="edge-menu-overlay" @click="close" @contextmenu.prevent="close">
    <div
      class="edge-menu"
      :style="{ left: `${position.x}px`, top: `${position.y}px` }"
      @click.stop
    >
      <div class="menu-section-title">连线样式</div>
      <div
        v-for="opt in typeOptions"
        :key="opt.value"
        class="menu-item"
        :class="{ active: currentType === opt.value }"
        @click="handle('changeType', opt.value)"
      >
        <span>{{ opt.label }}</span>
        <el-icon v-if="currentType === opt.value"><Check /></el-icon>
      </div>

      <div class="menu-divider"></div>

      <div class="menu-section-title">颜色</div>
      <div class="color-row">
        <div
          v-for="c in colorList"
          :key="c"
          class="color-dot"
          :class="{ active: currentColor === c }"
          :style="{ background: c }"
          @click="handle('changeColor', c)"
        ></div>
      </div>

      <div class="menu-divider"></div>

      <div class="menu-item" @click="handle('toggleArrow')">
        <el-icon><Right /></el-icon>
        <span>{{ hasArrow ? '隐藏箭头' : '显示箭头' }}</span>
      </div>
      <div class="menu-item" @click="handle('toggleAnimated')">
        <el-icon><VideoPlay /></el-icon>
        <span>{{ animated ? '关闭动画' : '开启动画' }}</span>
      </div>
      <div class="menu-item" @click="handle('reverse')">
        <el-icon><Switch /></el-icon>
        <span>翻转方向</span>
      </div>

      <div class="menu-divider"></div>

      <div class="menu-item danger" @click="handle('delete')">
        <el-icon><Delete /></el-icon>
        <span>删除连线</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.edge-menu-overlay {
  position: fixed;
  inset: 0;
  z-index: 9998;
}

.edge-menu {
  position: fixed;
  z-index: 9999;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  padding: 6px 0;
  min-width: 180px;
}

.menu-section-title {
  padding: 6px 16px 4px;
  font-size: 12px;
  color: #909399;
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  color: #303133;
  transition: background-color 0.15s;
}

.menu-item > span {
  flex: 1;
}

.menu-item:hover {
  background-color: #f5f7fa;
}

.menu-item.active {
  color: #409eff;
  font-weight: 600;
}

.menu-item.danger {
  color: #f56c6c;
}

.menu-item.danger:hover {
  background-color: #fef0f0;
}

.menu-divider {
  height: 1px;
  background-color: #ebeef5;
  margin: 4px 0;
}

.color-row {
  display: flex;
  gap: 8px;
  padding: 4px 16px 8px;
}

.color-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
  transition: transform 0.15s, border-color 0.15s;
}

.color-dot:hover {
  transform: scale(1.15);
}

.color-dot.active {
  border-color: #303133;
  box-shadow: 0 0 0 2px #fff;
}
</style>
