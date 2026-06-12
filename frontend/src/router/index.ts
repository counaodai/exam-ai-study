import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页', layout: 'landing' },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '工作台' },
  },
  {
    path: '/upload',
    name: 'Upload',
    component: () => import('@/views/Upload.vue'),
    meta: { title: '文档导入' },
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/Chat.vue'),
    meta: { title: 'AI问答' },
  },
  {
    path: '/mindmap',
    name: 'MindMap',
    component: () => import('@/views/MindMap.vue'),
    meta: { title: '思维导图' },
  },
  {
    path: '/mindmap/:moduleId',
    name: 'MindMapDetail',
    component: () => import('@/views/MindMapDetail.vue'),
    meta: { title: '思维导图详情' },
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: () => import('@/views/Analysis.vue'),
    meta: { title: '统计分析' },
  },
  {
    path: '/methods',
    name: 'MethodList',
    component: () => import('@/views/MethodList.vue'),
    meta: { title: '方法论总结' },
  },
  {
    path: '/methods/:id',
    name: 'MethodDetail',
    component: () => import('@/views/MethodDetail.vue'),
    meta: { title: '方法论详情' },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { title: '设置' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title || '首页'} - 公考AI智能学习系统`
  next()
})

export default router
