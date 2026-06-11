<script setup lang="ts">
import { useAppStore } from '@/stores/app'
import { Fold, Expand } from '@element-plus/icons-vue'

const appStore = useAppStore()
</script>

<template>
  <el-header class="app-header">
    <div class="header-left">
      <el-icon class="collapse-btn" @click="appStore.toggleSidebar">
        <Fold v-if="!appStore.isSidebarCollapsed" />
        <Expand v-else />
      </el-icon>
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-if="$route.meta.title && $route.path !== '/'">
          {{ $route.meta.title }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    <div class="header-right">
      <el-dropdown>
        <span class="user-info">
          <el-avatar :size="32" icon="UserFilled" />
          <span class="username">用户</span>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item>个人设置</el-dropdown-item>
            <el-dropdown-item divided>退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </el-header>
</template>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-light);
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 1px 4px rgba(15, 40, 39, 0.04);
  height: var(--header-height);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: var(--text-muted);
  transition: all var(--transition-fast);
  padding: 4px;
  border-radius: var(--radius-sm);
}

.collapse-btn:hover {
  color: var(--primary-color);
  background: var(--primary-bg);
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
  padding: 4px 12px;
  border-radius: var(--radius-full);
  transition: all var(--transition-fast);
}

.user-info:hover {
  background: var(--bg-muted);
}

.username {
  font-size: 14px;
  color: var(--text-regular);
  font-weight: 500;
}

:deep(.el-dropdown-link) {
  cursor: pointer;
}

:deep(.el-avatar) {
  background: var(--primary-gradient);
  border: 2px solid var(--primary-lighter);
}
</style>
