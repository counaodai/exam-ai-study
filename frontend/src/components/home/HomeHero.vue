<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function goToDashboard() {
  router.push('/dashboard')
}
</script>

<template>
  <section class="hero">
    <!-- 装饰手绘元素 -->
    <svg class="deco deco-tl" viewBox="0 0 80 80" aria-hidden="true">
      <path d="M10 40c5-20 15-30 30-25s10 20-5 25-25 5-25 0z" fill="none" stroke="var(--primary-lighter)" stroke-width="1.5" opacity="0.4"/>
      <circle cx="55" cy="20" r="3" fill="var(--accent-light)" opacity="0.5"/>
    </svg>

    <svg class="deco deco-br" viewBox="0 0 80 80" aria-hidden="true">
      <path d="M20 60c10-15 25-10 30 0s-5 15-15 10" fill="none" stroke="var(--warning-color)" stroke-width="1.5" opacity="0.3"/>
      <circle cx="30" cy="55" r="2" fill="var(--primary-lighter)" opacity="0.4"/>
    </svg>

    <div class="hero-inner">
      <!-- 左侧 60%: 标题 + CTA -->
      <div class="hero-content">
        <h1 class="hero-title">
          慢慢来，<br/>比较快
        </h1>
        <p class="hero-subtitle">
          AI帮你把厚书读薄，<br/>每天只专注搞懂几道题
        </p>
        <div class="hero-actions">
          <button class="hero-cta" @click="goToDashboard" aria-label="开始学习">
            开始学习
            <iconify-icon icon="mdi:arrow-right" width="18" style="margin-left:6px" />
          </button>
          <span class="hero-hint">免费使用，无需注册</span>
        </div>
      </div>

      <!-- 右侧 40%: 产品预览卡片 -->
      <div class="hero-preview">
        <div class="preview-card">
          <div class="preview-header">
            <span class="preview-dot" style="background:var(--accent-color)"></span>
            <span class="preview-dot" style="background:var(--warning-color)"></span>
            <span class="preview-dot" style="background:var(--primary-color)"></span>
          </div>
          <div class="preview-body">
            <div class="preview-chat">
              <div class="preview-msg user">这道言语理解怎么做？</div>
              <div class="preview-msg ai">
                <span class="msg-label">AI</span>
                这道题考的是主旨概括，关键词是"因此"...
              </div>
            </div>
            <div class="preview-tag">
              <span class="tag-item">言语理解</span>
              <span class="tag-item">主旨概括</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero {
  position: relative;
  min-height: 88vh;
  display: flex;
  align-items: center;
  padding: 60px 32px 80px;
  background: var(--bg-color);
  overflow: hidden;
}

.deco {
  position: absolute;
  width: 120px;
  height: 120px;
  pointer-events: none;
}

.deco-tl { top: 10%; left: 3%; }
.deco-br { bottom: 8%; right: 5%; }

.hero-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 60px;
  width: 100%;
}

.hero-content {
  flex: 6;
  min-width: 0;
}

.hero-title {
  font-family: var(--font-display);
  font-size: clamp(36px, 6vw, 72px);
  line-height: 1.2;
  color: var(--text-primary);
  margin-bottom: 24px;
  animation: heroIn var(--transition-bounce) both;
}

.hero-subtitle {
  font-family: var(--font-body);
  font-size: clamp(16px, 2vw, 22px);
  line-height: 1.7;
  color: var(--text-secondary);
  margin-bottom: 36px;
  animation: heroIn var(--transition-bounce) 100ms both;
}

.hero-actions {
  display: flex;
  align-items: center;
  gap: 20px;
  animation: heroIn var(--transition-bounce) 200ms both;
}

.hero-cta {
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: 16px;
  padding: 14px 32px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius-hand-drawn);
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  transition: all var(--transition-btn-hover);
}

.hero-cta:hover {
  background: var(--primary-light);
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(91, 140, 90, 0.3);
}

.hero-cta:active {
  transform: scale(0.97);
  transition-duration: 150ms;
}

.hero-cta:focus-visible {
  outline: 3px solid var(--primary-color);
  outline-offset: 3px;
}

.hero-hint {
  font-family: var(--font-body);
  font-size: 14px;
  color: var(--text-muted);
}

.hero-preview {
  flex: 4;
  min-width: 0;
  animation: heroIn var(--transition-bounce) 300ms both;
}

.preview-card {
  background: var(--bg-surface);
  border: 2px solid var(--line-secondary);
  border-radius: var(--radius-hand-drawn);
  padding: 0;
  overflow: hidden;
  box-shadow: 6px 8px 0 rgba(123, 160, 122, 0.15);
  transform: rotate(1.5deg);
}

.preview-header {
  display: flex;
  gap: 6px;
  padding: 12px 16px;
  background: var(--bg-muted);
  border-bottom: 1.5px dashed var(--primary-lighter);
}

.preview-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  opacity: 0.8;
}

.preview-body {
  padding: 20px 18px;
}

.preview-chat {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.preview-msg {
  font-family: var(--font-body);
  font-size: 13px;
  line-height: 1.5;
  padding: 10px 14px;
  border-radius: var(--radius-hand-drawn);
  max-width: 85%;
}

.preview-msg.user {
  background: var(--primary-bg);
  color: var(--text-primary);
  align-self: flex-end;
}

.preview-msg.ai {
  background: var(--bg-muted);
  color: var(--text-primary);
  align-self: flex-start;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.msg-label {
  font-size: 10px;
  font-weight: 700;
  background: var(--primary-color);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  flex-shrink: 0;
  margin-top: 1px;
}

.preview-tag {
  display: flex;
  gap: 8px;
}

.tag-item {
  font-family: var(--font-heading);
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  background: var(--accent-light);
  color: var(--accent-color);
  border-radius: var(--radius-hand-drawn);
}

@keyframes heroIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 900px) {
  .hero-inner {
    flex-direction: column;
    gap: 40px;
  }
  .hero-content, .hero-preview { flex: none; width: 100%; }
}

@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0ms !important; transition-duration: 0ms !important; }
}
</style>
