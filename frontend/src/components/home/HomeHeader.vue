<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isScrolled = ref(false)
const mobileMenuOpen = ref(false)

function handleScroll() {
  isScrolled.value = window.scrollY > 20
}

function navigateTo(path: string) {
  router.push(path)
  mobileMenuOpen.value = false
}

function scrollToFeatures() {
  document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })
}

onMounted(() => window.addEventListener('scroll', handleScroll))
onUnmounted(() => window.removeEventListener('scroll', handleScroll))
</script>

<template>
  <header class="home-header" :class="{ scrolled: isScrolled }">
    <div class="header-inner">
      <div class="logo" @click="navigateTo('/')">
        <iconify-icon icon="mdi:leaf-circle-outline" width="32" class="logo-icon" />
        <span class="logo-text">慢慢学</span>
      </div>

      <nav class="nav-links" :class="{ open: mobileMenuOpen }">
        <a @click.prevent="scrollToFeatures" aria-label="查看功能">功能</a>
        <a @click.prevent="navigateTo('/chat')" aria-label="开始问答">问答</a>
        <a @click.prevent="navigateTo('/mindmap')" aria-label="查看导图">导图</a>
      </nav>

      <button class="cta-btn" @click="navigateTo('/dashboard')" aria-label="进入工作台">
        开始学习
      </button>

      <button class="mobile-toggle" @click="mobileMenuOpen = !mobileMenuOpen" aria-label="菜单">
        <iconify-icon :icon="mobileMenuOpen ? 'mdi:close' : 'mdi:menu'" width="24" />
      </button>
    </div>

    <!-- 手绘波浪底边 -->
    <svg class="header-wave" viewBox="0 0 1440 40" preserveAspectRatio="none" aria-hidden="true">
      <path d="M0 20c120-15 240 15 360 5s240-20 360-5 240 18 360 8 240-15 360-5v17H0z" fill="var(--bg-color)" opacity="0.7" />
    </svg>
  </header>
</template>

<style scoped>
.home-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: var(--bg-color);
  transition: box-shadow var(--transition-fade);
}

.home-header.scrolled {
  box-shadow: 0 4px 20px rgba(74, 63, 47, 0.08);
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 32px;
  display: flex;
  align-items: center;
  gap: 32px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  color: var(--primary-color);
  transition: transform var(--transition-btn-hover);
}

.logo:hover {
  transform: scale(1.03);
}

.logo-icon {
  flex-shrink: 0;
  color: var(--primary-color);
}

.logo-text {
  font-family: var(--font-display);
  font-size: clamp(20px, 2.5vw, 26px);
  color: var(--text-primary);
  letter-spacing: 1px;
}

.nav-links {
  display: flex;
  gap: 28px;
  margin-left: auto;
}

.nav-links a {
  font-family: var(--font-heading);
  font-size: 15px;
  font-weight: 600;
  color: var(--text-secondary);
  cursor: pointer;
  position: relative;
  padding: 4px 0;
  transition: color var(--transition-btn-hover);
}

.nav-links a::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: -4px;
  right: -4px;
  height: 3px;
  background: var(--primary-color);
  border-radius: 2px;
  transform: scaleX(0);
  transform-origin: left;
  transition: transform var(--transition-btn-hover);
}

.nav-links a:hover {
  color: var(--text-primary);
}

.nav-links a:hover::after {
  transform: scaleX(1);
}

.cta-btn {
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: 14px;
  padding: 10px 24px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius-hand-drawn);
  cursor: pointer;
  transition: all var(--transition-btn-hover);
}

.cta-btn:hover {
  background: var(--primary-light);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(91, 140, 90, 0.3);
}

.cta-btn:active {
  transform: scale(0.97);
  transition-duration: 150ms;
}

.cta-btn:focus-visible {
  outline: 3px solid var(--primary-color);
  outline-offset: 2px;
}

.mobile-toggle {
  display: none;
  background: none;
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  padding: 4px;
}

.header-wave {
  display: block;
  width: 100%;
  height: 20px;
}

@media (max-width: 768px) {
  .nav-links { display: none; }
  .nav-links.open {
    display: flex;
    flex-direction: column;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--bg-surface);
    padding: 16px 32px;
    gap: 16px;
    border-bottom: 2px solid var(--primary-lighter);
  }
  .cta-btn { display: none; }
  .mobile-toggle { display: block; }
}

@media (prefers-reduced-motion: reduce) {
  * { transition-duration: 0ms !important; animation-duration: 0ms !important; }
}
</style>
