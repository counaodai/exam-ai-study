<script setup lang="ts">
import { useAppStore } from '@/stores/app'
import { useRouter } from 'vue-router'

const appStore = useAppStore()
const router = useRouter()

function goToSettings() {
  router.push('/settings')
}
</script>

<template>
  <el-header class="app-header">
    <div class="header-left">
      <button
        class="collapse-btn"
        :aria-label="appStore.isSidebarCollapsed ? '展开侧边栏' : '收起侧边栏'"
        @click="appStore.toggleSidebar"
      >
        <iconify-icon :icon="appStore.isSidebarCollapsed ? 'mdi:menu-open' : 'mdi:menu'" width="22" />
      </button>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/dashboard' }">工作台</el-breadcrumb-item>
        <el-breadcrumb-item v-if="$route.meta.title">
          {{ $route.meta.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    <div class="header-right">
      <el-dropdown>
        <span class="user-info">
          <el-avatar :size="32" icon="UserFilled" />
          <span class="username">同学</span>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="goToSettings">个人设置</el-dropdown-item>
            <el-dropdown-item divided>退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
    <!-- 手绘波浪底边 -->
    <svg class="header-wave" viewBox="0 0 1200 12" preserveAspectRatio="none" aria-hidden="true">
      <path
        d="M0,8 C100,2 200,12 300,6 C400,0 500,10 600,5 C700,0 800,10 900,4 C1000,0 1100,8 1200,6 L1200,12 L0,12 Z"
        fill="var(--bg-color)"
      />
    </svg>
  </el-header>
</template>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  height: var(--header-height);
  position: relative;
  padding: 0 20px;
  border-bottom: none;
}

.header-wave {
  position: absolute;
  bottom: -11px;
  left: 0;
  width: 100%;
  height: 12px;
  z-index: 2;
}

.collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 2px solid var(--border-light);
  border-radius: var(--radius-hand-drawn-soft);
  background: var(--bg-surface);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-hover-lift);
}

.collapse-btn:hover {
  color: var(--primary-color);
  border-color: var(--primary-lighter);
  background: var(--primary-bg);
  transform: translateY(-1px);
}

.collapse-btn:active {
  transform: scale(0.95);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 14px;
  border-radius: var(--radius-hand-drawn-soft);
  border: 2px solid var(--border-light);
  transition: all var(--transition-hover-lift);
  background: var(--bg-surface);
}

.user-info:hover {
  background: var(--primary-bg);
  border-color: var(--primary-lighter);
  transform: translateY(-1px);
}

.username {
  font-size: 14px;
  color: var(--text-regular);
  font-weight: 600;
  font-family: var(--font-heading);
}

:deep(.el-avatar) {
  background: var(--primary-gradient);
  border: 2px solid var(--primary-lighter);
}

:deep(.el-breadcrumb__inner) {
  font-family: var(--font-heading);
  font-weight: 500;
}
</style>
