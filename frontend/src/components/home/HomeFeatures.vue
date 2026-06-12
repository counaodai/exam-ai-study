<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Feature {
  icon: string
  title: string
  desc: string
  detail: string
  color: string
  stagger: string
}

const features: Feature[] = [
  {
    icon: 'mdi:sort-variant',
    title: '题目自动分类',
    desc: '不再翻来翻去找错题',
    detail: 'AI识别题型，自动归入言语、数量、判断等模块，比你自己分类快10倍',
    color: 'var(--primary-color)',
    stagger: '0ms',
  },
  {
    icon: 'mdi:sitemap-outline',
    title: '导图自动生成',
    desc: '零门槛构建知识网络',
    detail: '每次问答后自动更新思维导图，零手工操作，知识脉络一目了然',
    color: 'var(--warning-color)',
    stagger: '80ms',
  },
  {
    icon: 'mdi:lightbulb-on-outline',
    title: '方法自动提取',
    desc: '别人刷1000题的套路，你直接拿',
    detail: '从题目中提炼通用解题方法，举一反三不是梦，1个方法顶10道题',
    color: 'var(--accent-color)',
    stagger: '160ms',
  },
]

const visible = ref(false)

onMounted(() => {
  const observer = new IntersectionObserver(
    ([entry]) => { if (entry.isIntersecting) visible.value = true },
    { threshold: 0.15 }
  )
  const el = document.getElementById('features')
  if (el) observer.observe(el)
})
</script>

<template>
  <section id="features" class="features-section">
    <!-- SVG波浪分割线 -->
    <svg class="wave-divider" viewBox="0 0 1440 60" preserveAspectRatio="none" aria-hidden="true">
      <path d="M0 30c180-20 360 20 540 10s360-25 540-10 270 25 360 15v25H0z" fill="var(--bg-muted)" opacity="0.5"/>
    </svg>

    <div class="features-inner">
      <h2 class="section-title">
        你只管问，剩下的交给我
      </h2>
      <p class="section-subtitle">
        不用再花时间整理笔记，AI边聊边帮你归类、画图、总结
      </p>

      <div class="feature-cards" :class="{ visible }">
        <div
          v-for="feat in features"
          :key="feat.title"
          class="feature-card"
          :style="{ '--stagger': feat.stagger, '--card-color': feat.color }"
        >
          <div class="card-icon">
            <iconify-icon :icon="feat.icon" width="28" :style="{ color: feat.color }" />
          </div>
          <h3 class="card-title">{{ feat.title }}</h3>
          <p class="card-desc">{{ feat.desc }}</p>
          <p class="card-detail">{{ feat.detail }}</p>
          <!-- 手绘装饰线 -->
          <svg class="card-squiggle" viewBox="0 0 120 8" aria-hidden="true">
            <path d="M0 5c10-3 20 3 30 0s20-4 30-1 20 3 30 0 20-3 30 0" fill="none" :stroke="feat.color" stroke-width="1.5" opacity="0.3"/>
          </svg>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.features-section {
  position: relative;
  padding: 80px 32px 100px;
  background: var(--bg-muted);
}

.wave-divider {
  position: absolute;
  top: -30px;
  left: 0;
  width: 100%;
  height: 60px;
}

.features-inner {
  max-width: 1100px;
  margin: 0 auto;
}

.section-title {
  font-family: var(--font-display);
  font-size: clamp(24px, 4vw, 40px);
  color: var(--text-primary);
  margin-bottom: 12px;
}

.section-subtitle {
  font-family: var(--font-body);
  font-size: clamp(14px, 1.6vw, 18px);
  color: var(--text-secondary);
  margin-bottom: 48px;
  line-height: 1.7;
}

.feature-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 28px;
}

.feature-cards:not(.visible) .feature-card {
  opacity: 0;
  transform: translateY(40px);
}

.feature-card {
  background: var(--bg-surface);
  border: 2px solid var(--line-primary);
  border-radius: var(--radius-hand-drawn);
  padding: 32px 28px 28px;
  position: relative;
  transition: all var(--transition-hover-lift);
  animation: cardEnter var(--transition-bounce) var(--stagger) both;
  animation-play-state: var(--card-play, paused);
}

.feature-cards.visible .feature-card {
  --card-play: running;
}

.feature-card:nth-child(2) {
  margin-top: 24px; /* 错位效果 */
}

.feature-card:nth-child(3) {
  margin-top: 8px;
}

.feature-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 8px 24px rgba(90, 79, 63, 0.1);
}

.card-icon {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-bg);
  border-radius: var(--radius-hand-drawn);
  margin-bottom: 20px;
  border: 2px solid var(--border-light);
}

.card-title {
  font-family: var(--font-heading);
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.card-desc {
  font-family: var(--font-display);
  font-size: 15px;
  color: var(--card-color);
  margin-bottom: 12px;
}

.card-detail {
  font-family: var(--font-body);
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.card-squiggle {
  display: block;
  width: 100%;
  height: 8px;
  margin-top: 20px;
}

@keyframes cardEnter {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 900px) {
  .feature-cards {
    grid-template-columns: 1fr;
  }
  .feature-card:nth-child(2),
  .feature-card:nth-child(3) {
    margin-top: 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .feature-card { animation: none !important; opacity: 1; transform: none; }
  .feature-card:hover { transform: none; }
}
</style>
