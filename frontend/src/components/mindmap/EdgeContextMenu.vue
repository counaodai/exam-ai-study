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

// 预设颜色（自然治愈风：苔藓绿/自然绿/暖沙/陶土橙/暖灰/雾紫）
const colorList = ['#5B8C5A', '#7BA07A', '#C4A35A', '#C0694A', '#8A7E6A', '#8B5CF6']

const typeOptions: { label: string; value: EdgeType; icon: string }[] = [
  { label: '贝塞尔曲线', value: 'default', icon: 'mdi:vector-curve' },
  { label: '直线', value: 'straight', icon: 'mdi:vector-line' },
  { label: '折线', value: 'step', icon: 'mdi:vector-polyline' },
  { label: '圆角折线', value: 'smoothstep', icon: 'mdi:vector-radius' },
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
        <iconify-icon :icon="opt.icon" width="18" class="menu-icon" />
        <span>{{ opt.label }}</span>
        <iconify-icon v-if="currentType === opt.value" icon="mdi:check" width="16" class="menu-check" />
      </div>

      <div class="menu-divider"></div>

      <div class="menu-section-title">
        <iconify-icon icon="mdi:palette-outline" width="14" class="section-icon" />
        <span>颜色</span>
      </div>
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
        <iconify-icon icon="mdi:arrow-right" width="18" class="menu-icon" />
        <span>{{ hasArrow ? '隐藏箭头' : '显示箭头' }}</span>
      </div>
      <div class="menu-item" @click="handle('toggleAnimated')">
        <iconify-icon icon="mdi:motion-play-outline" width="18" class="menu-icon" />
        <span>{{ animated ? '关闭动画' : '开启动画' }}</span>
      </div>
      <div class="menu-item" @click="handle('reverse')">
        <iconify-icon icon="mdi:swap-horizontal" width="18" class="menu-icon" />
        <span>翻转方向</span>
      </div>

      <div class="menu-divider"></div>

      <div class="menu-item danger" @click="handle('delete')">
        <iconify-icon icon="mdi:trash-can-outline" width="18" class="menu-icon" />
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
  background: var(--bg-surface);
  border: 2px solid var(--border-light);
  border-radius: var(--radius-hand-drawn-soft);
  box-shadow: var(--shadow-md), var(--shadow-hand-drawn);
  padding: 8px 6px;
  min-width: 196px;
  font-family: var(--font-heading);
  animation: cardEnter var(--transition-bounce) both;
}

.menu-section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px 4px;
  font-size: 12px;
  color: #8A7E6A;
  font-family: var(--font-heading);
  letter-spacing: 0.3px;
}

.section-icon {
  color: var(--primary-color);
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

.menu-check {
  color: var(--primary-color);
  margin-left: auto;
}

.menu-item > span {
  flex: 1;
}

.menu-item:hover {
  background-color: var(--primary-bg);
  color: var(--primary-color);
  transform: translateX(2px);
}

.menu-item.active {
  color: var(--primary-color);
  font-weight: 600;
  background-color: var(--primary-bg);
}

.menu-item.danger {
  color: var(--accent-color);
}

.menu-item.danger:hover {
  background-color: rgba(192, 105, 74, 0.12);
  color: var(--accent-color);
}

.menu-divider {
  height: 1px;
  background-color: var(--border-light);
  margin: 6px 4px;
  opacity: 0.7;
}

.color-row {
  display: flex;
  gap: 8px;
  padding: 4px 12px 8px;
  flex-wrap: wrap;
}

.color-dot {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
  box-shadow: var(--shadow-hand-drawn);
}

.color-dot:hover {
  transform: scale(1.18) rotate(-4deg);
}

.color-dot.active {
  border-color: var(--text-primary, #4A3F2F);
  box-shadow: 0 0 0 2px var(--bg-surface), var(--shadow-hand-drawn);
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
