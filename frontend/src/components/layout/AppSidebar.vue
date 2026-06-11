<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import {
  ChatDotRound,
  Upload,
  Share,
  DataAnalysis,
  Setting,
  HomeFilled,
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()

const menuItems = [
  { path: '/', icon: HomeFilled, title: '首页' },
  { path: '/upload', icon: Upload, title: '文档导入' },
  { path: '/chat', icon: ChatDotRound, title: 'AI问答' },
  { path: '/mindmap', icon: Share, title: '思维导图' },
  { path: '/analysis', icon: DataAnalysis, title: '统计分析' },
  { path: '/settings', icon: Setting, title: '设置' },
]

function handleMenuClick(path: string) {
  router.push(path)
}
</script>

<template>
  <el-aside :width="appStore.isSidebarCollapsed ? '64px' : '200px'" class="sidebar">
    <div class="logo">
      <span v-if="!appStore.isSidebarCollapsed">公考AI助手</span>
      <span v-else>AI</span>
    </div>
    <el-menu
      :default-active="route.path"
      :collapse="appStore.isSidebarCollapsed"
      class="sidebar-menu"
      @select="handleMenuClick"
    >
      <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
        <el-icon><component :is="item.icon" /></el-icon>
        <template #title>{{ item.title }}</template>
      </el-menu-item>
    </el-menu>
  </el-aside>
</template>

<style scoped>
.sidebar {
  background: var(--sidebar-bg-gradient);
  transition: width var(--transition-slow);
  overflow: hidden;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-light);
  font-family: var(--font-heading);
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 1px;
  border-bottom: 1px solid rgba(45, 212, 191, 0.1);
  background: linear-gradient(180deg, rgba(13, 148, 136, 0.1) 0%, transparent 100%);
  position: relative;
}

.logo::before {
  content: '';
  position: absolute;
  left: 50%;
  top: -1px;
  transform: translateX(-50%);
  width: 40px;
  height: 2px;
  background: var(--primary-gradient);
  border-radius: 1px;
}

.sidebar-menu {
  border-right: none;
  background-color: transparent;
  padding: 12px 8px;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 240px;
}

:deep(.el-menu-item) {
  color: var(--sidebar-text);
  border-radius: var(--radius-sm);
  margin-bottom: 4px;
  height: 46px;
  line-height: 46px;
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

:deep(.el-menu-item)::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 0;
  background: var(--primary-gradient);
  border-radius: 0 2px 2px 0;
  transition: height var(--transition-normal);
}

:deep(.el-menu-item:hover) {
  background-color: var(--sidebar-hover);
  color: var(--sidebar-text-active);
  transform: translateX(2px);
}

:deep(.el-menu-item:hover::before) {
  height: 60%;
}

:deep(.el-menu-item.is-active) {
  background: var(--sidebar-active);
  color: var(--sidebar-text-active);
  font-weight: 600;
  box-shadow: inset 0 0 12px rgba(13, 148, 136, 0.15);
}

:deep(.el-menu-item.is-active::before) {
  height: 70%;
}

:deep(.el-menu-item .el-icon) {
  font-size: 18px;
  transition: transform var(--transition-fast);
}

:deep(.el-menu-item:hover .el-icon) {
  transform: scale(1.1);
}
</style>
