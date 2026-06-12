<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const menuItems = [
  { path: '/dashboard', icon: 'mdi:view-dashboard-outline', title: '工作台' },
  { path: '/upload', icon: 'mdi:file-upload-outline', title: '文档导入' },
  { path: '/chat', icon: 'mdi:chat-outline', title: 'AI问答' },
  { path: '/mindmap', icon: 'mdi:sitemap-outline', title: '思维导图' },
  { path: '/analysis', icon: 'mdi:chart-line', title: '统计分析' },
  { path: '/methods', icon: 'mdi:lightbulb-outline', title: '方法论' },
  { path: '/settings', icon: 'mdi:cog-outline', title: '设置' },
]

function handleMenuClick(path: string) {
  router.push(path)
}
</script>

<template>
  <el-aside :width="appStore.isSidebarCollapsed ? '64px' : '220px'" class="sidebar">
    <!-- Logo区 -->
    <div class="sidebar-logo">
      <div class="logo-icon">
        <iconify-icon icon="mdi:leaf" width="28" />
      </div>
      <transition name="fade">
        <span v-if="!appStore.isSidebarCollapsed" class="logo-text">公考AI助手</span>
      </transition>
    </div>

    <!-- 手绘分割线 -->
    <svg class="sidebar-divider" viewBox="0 0 200 4" preserveAspectRatio="none" aria-hidden="true">
      <path
        d="M0,2 C30,0 60,4 100,2 C140,0 170,4 200,2"
        stroke="rgba(91, 140, 90, 0.3)"
        stroke-width="1.5"
        fill="none"
        stroke-linecap="round"
      />
    </svg>

    <!-- 导航菜单 -->
    <el-menu
      :default-active="route.path"
      :collapse="appStore.isSidebarCollapsed"
      class="sidebar-menu"
      @select="handleMenuClick"
    >
      <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
        <iconify-icon :icon="item.icon" width="20" class="menu-icon" />
        <template #title>{{ item.title }}</template>
      </el-menu-item>
    </el-menu>

    <!-- 底部装饰 -->
    <div class="sidebar-decor" aria-hidden="true">
      <svg viewBox="0 0 120 60" fill="none">
        <path d="M10,50 Q30,10 60,30 Q90,50 110,20" stroke="rgba(91, 140, 90, 0.15)" stroke-width="2" fill="none" stroke-linecap="round" />
        <circle cx="20" cy="45" r="3" fill="rgba(91, 140, 90, 0.1)" />
        <circle cx="95" cy="25" r="2" fill="rgba(192, 105, 74, 0.12)" />
      </svg>
    </div>
  </el-aside>
</template>

<style scoped>
.sidebar {
  background: var(--sidebar-bg-gradient);
  transition: width var(--transition-slow);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-shadow: 3px 0 12px rgba(74, 63, 47, 0.12);
  position: relative;
}

.sidebar-logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 0 16px;
  position: relative;
}

.logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: var(--radius-hand-drawn-soft);
  background: rgba(91, 140, 90, 0.15);
  color: var(--primary-lighter);
  flex-shrink: 0;
  border: 1.5px solid rgba(91, 140, 90, 0.2);
}

.logo-text {
  font-family: var(--font-display);
  font-size: 18px;
  font-weight: 700;
  color: var(--sidebar-text-active);
  letter-spacing: 0.5px;
  white-space: nowrap;
  overflow: hidden;
}

.sidebar-divider {
  width: 80%;
  height: 4px;
  margin: 0 auto 4px;
}

.sidebar-menu {
  border-right: none;
  background-color: transparent;
  padding: 8px 10px;
  flex: 1;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 200px;
}

:deep(.el-menu-item) {
  color: var(--sidebar-text);
  border-radius: var(--radius-hand-drawn-soft);
  margin-bottom: 4px;
  height: 44px;
  line-height: 44px;
  transition: all var(--transition-hover-lift);
  position: relative;
  overflow: hidden;
  font-family: var(--font-heading);
  font-weight: 500;
  font-size: 14px;
}

:deep(.el-menu-item) .menu-icon {
  transition: transform var(--transition-hover-lift);
}

:deep(.el-menu-item:hover) {
  background-color: var(--sidebar-hover);
  color: var(--sidebar-text-active);
  transform: translateX(3px);
}

:deep(.el-menu-item:hover) .menu-icon {
  transform: scale(1.15);
}

:deep(.el-menu-item.is-active) {
  background: var(--sidebar-active);
  color: var(--sidebar-text-active);
  font-weight: 700;
  box-shadow: inset 0 0 12px rgba(91, 140, 90, 0.12);
}

:deep(.el-menu-item.is-active)::after {
  content: '';
  position: absolute;
  left: 0;
  top: 25%;
  height: 50%;
  width: 3px;
  background: var(--sidebar-text-active);
  border-radius: 0 2px 2px 0;
}

.sidebar-decor {
  padding: 12px 16px;
  opacity: 0.6;
  transition: opacity var(--transition-normal);
}

.sidebar-decor:hover {
  opacity: 1;
}

/* 折叠菜单下的图标居中 */
:deep(.el-menu--collapse .el-menu-item) {
  padding: 0 !important;
  justify-content: center;
}

:deep(.el-menu--collapse .menu-icon) {
  margin-right: 0;
}

/* 折叠动画 */
.fade-enter-active {
  transition: opacity var(--transition-fade);
}

.fade-leave-active {
  transition: opacity 150ms ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
