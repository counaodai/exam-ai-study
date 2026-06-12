<script setup lang="ts">
import { ref, onMounted } from 'vue'

const stats = [
  { value: '3万+', label: '公考题目', icon: 'mdi:clipboard-text-outline' },
  { value: '6大', label: '公考模块', icon: 'mdi:view-grid-outline' },
  { value: '秒级', label: '智能分类', icon: 'mdi:lightning-bolt-outline' },
  { value: '1→10', label: '方法举一反三', icon: 'mdi:lightbulb-on-outline' },
]

const visible = ref(false)

onMounted(() => {
  const observer = new IntersectionObserver(
    ([entry]) => { if (entry.isIntersecting) visible.value = true },
    { threshold: 0.2 }
  )
  const el = document.getElementById('stats')
  if (el) observer.observe(el)
})
</script>

<template>
  <section id="stats" class="stats-section">
    <div class="stats-inner" :class="{ visible }">
      <div class="stats-header">
        <h2 class="stats-title">数字会说话</h2>
        <p class="stats-subtitle">不是为了炫耀，是让你心里有底</p>
      </div>

      <div class="stats-grid">
        <div
          v-for="(stat, i) in stats"
          :key="stat.label"
          class="stat-item"
          :style="{ '--i': i }"
        >
          <div class="stat-icon">
            <iconify-icon :icon="stat.icon" width="22" />
          </div>
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>
    </div>

    <!-- 手绘装饰 -->
    <svg class="deco-line" viewBox="0 0 200 20" aria-hidden="true">
      <path d="M5 10c20-6 40 6 60 0s40-8 60-2 40 6 60 0 20-4 20-4" fill="none" stroke="var(--primary-lighter)" stroke-width="1.5" opacity="0.4"/>
    </svg>
  </section>
</template>

<style scoped>
.stats-section {
  position: relative;
  padding: 80px 32px 100px;
  background: var(--bg-color);
  overflow: hidden;
}

.stats-inner {
  max-width: 1000px;
  margin: 0 auto;
}

.stats-header {
  margin-bottom: 48px;
}

.stats-title {
  font-family: var(--font-display);
  font-size: clamp(24px, 4vw, 36px);
  color: var(--text-primary);
  margin-bottom: 8px;
}

.stats-subtitle {
  font-family: var(--font-body);
  font-size: clamp(14px, 1.5vw, 17px);
  color: var(--text-secondary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.stat-item {
  text-align: center;
  padding: 32px 16px;
  background: var(--bg-surface);
  border: 2px solid var(--primary-lighter);
  border-radius: var(--radius-hand-drawn);
  opacity: 0;
  transform: translateY(20px);
}

.stats-inner.visible .stat-item {
  animation: statIn var(--transition-bounce) calc(var(--i) * 80ms) both;
}

.stat-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-bg);
  border-radius: var(--radius-hand-drawn);
  margin: 0 auto 16px;
  color: var(--primary-color);
  border: 1.5px solid var(--primary-lighter);
}

.stat-value {
  font-family: var(--font-display);
  font-size: clamp(28px, 3.5vw, 40px);
  color: var(--text-primary);
  line-height: 1.2;
  margin-bottom: 8px;
}

.stat-label {
  font-family: var(--font-heading);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
}

.deco-line {
  position: absolute;
  bottom: 20px;
  left: 5%;
  width: 200px;
  height: 20px;
}

@keyframes statIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (prefers-reduced-motion: reduce) {
  .stat-item { animation: none !important; opacity: 1; transform: none; }
}
</style>
