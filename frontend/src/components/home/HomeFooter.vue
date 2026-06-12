<script setup lang="ts">
const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="home-footer">
    <!-- 手绘波浪顶部 -->
    <svg class="footer-wave" viewBox="0 0 1440 50" preserveAspectRatio="none" aria-hidden="true">
      <path d="M0 25c180 15 360-15 540-5s360 20 540 5 270-18 360-8v33H0z" fill="var(--bg-muted)"/>
    </svg>

    <div class="footer-inner">
      <div class="footer-top">
        <div class="footer-brand">
          <span class="brand-name">慢慢学</span>
          <p class="brand-desc">备考路上，有个AI陪你慢慢来</p>
        </div>

        <nav class="footer-nav" aria-label="页脚导航">
          <a href="#features">功能</a>
          <a href="#stats">数据</a>
          <router-link to="/chat">问答</router-link>
          <router-link to="/dashboard">工作台</router-link>
        </nav>
      </div>

      <!-- 手绘分割线 -->
      <svg class="footer-divider" viewBox="0 0 400 8" aria-hidden="true">
        <path d="M0 4c30-3 60 3 90 0s60-4 90 0 60 3 90 0 60-3 90 0" fill="none" stroke="var(--primary-lighter)" stroke-width="1.5"/>
      </svg>

      <div class="footer-bottom">
        <span>{{ currentYear }} 慢慢学 — 公考AI智能学习系统</span>
        <span class="footer-hint">慢慢来，比较快</span>
      </div>
    </div>

    <!-- 装饰手绘元素 -->
    <svg class="footer-deco" viewBox="0 0 60 60" aria-hidden="true">
      <circle cx="30" cy="30" r="3" fill="var(--accent-light)" opacity="0.4"/>
      <path d="M20 40c5-8 15-8 20 0" fill="none" stroke="var(--warning-color)" stroke-width="1.5" opacity="0.3"/>
    </svg>
  </footer>
</template>

<style scoped>
.home-footer {
  position: relative;
  background: var(--bg-muted);
  padding-top: 50px;
}

.footer-wave {
  position: absolute;
  top: -25px;
  left: 0;
  width: 100%;
  height: 50px;
}

.footer-inner {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 32px 32px;
}

.footer-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.brand-name {
  font-family: var(--font-display);
  font-size: 22px;
  color: var(--text-primary);
  display: block;
  margin-bottom: 8px;
}

.brand-desc {
  font-family: var(--font-body);
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.footer-nav {
  display: flex;
  gap: 24px;
}

.footer-nav a {
  font-family: var(--font-heading);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  text-decoration: none;
  cursor: pointer;
  transition: color var(--transition-btn-hover);
}

.footer-nav a:hover {
  color: var(--primary-color);
}

.footer-divider {
  display: block;
  width: 100%;
  height: 8px;
  margin-bottom: 24px;
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-family: var(--font-body);
  font-size: 13px;
  color: var(--text-muted);
}

.footer-hint {
  font-family: var(--font-display);
  color: var(--primary-color);
}

.footer-deco {
  position: absolute;
  bottom: 30px;
  right: 8%;
  width: 60px;
  height: 60px;
}

@media (max-width: 600px) {
  .footer-top {
    flex-direction: column;
    gap: 24px;
  }
  .footer-bottom {
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }
}
</style>
