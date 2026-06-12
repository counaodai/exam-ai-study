<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getOverviewStats } from '@/api/analysis'

const router = useRouter()

const stats = ref({
  documents: 0,
  questions: 0,
  conversations: 0,
  methods: 0,
})

const statsLoading = ref(false)

const quickActions = [
  { title: '导入文档', desc: '上传学习资料', icon: 'mdi:file-upload-outline', path: '/upload', color: 'var(--primary-color)' },
  { title: 'AI问答', desc: '智能解答题目', icon: 'mdi:chat-outline', path: '/chat', color: 'var(--success-color)' },
  { title: '思维导图', desc: '知识脉络一图览', icon: 'mdi:sitemap-outline', path: '/mindmap', color: 'var(--warning-color)' },
  { title: '统计分析', desc: '看看学习进度', icon: 'mdi:chart-line', path: '/analysis', color: 'var(--accent-color)' },
]

function navigateTo(path: string) {
  router.push(path)
}

async function fetchStats() {
  statsLoading.value = true
  try {
    const data = await getOverviewStats()
    stats.value = {
      documents: data.total_documents,
      questions: data.total_questions,
      conversations: data.total_conversations,
      methods: data.total_methods,
    }
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  } finally {
    statsLoading.value = false
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<template>
  <div class="dashboard">
    <div class="welcome">
      <h1>嗨，准备开始学习啦</h1>
      <p>AI陪你一起备考，轻松又高效</p>
    </div>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" v-loading="statsLoading">
          <div class="stat-value">{{ stats.documents }}</div>
          <div class="stat-label">已导入文档</div>
          <svg class="stat-wave" viewBox="0 0 120 8" aria-hidden="true">
            <path d="M0 5c10-4 20 2 30 0s20-5 30-1 20 3 30 0 20-4 30-1" fill="none" stroke="var(--primary-lighter)" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" v-loading="statsLoading">
          <div class="stat-value">{{ stats.questions }}</div>
          <div class="stat-label">累计题目</div>
          <svg class="stat-wave" viewBox="0 0 120 8" aria-hidden="true">
            <path d="M0 4c15-3 25 4 40 1s20-6 35-2 20 4 30 0 15-3 15-3" fill="none" stroke="var(--primary-lighter)" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" v-loading="statsLoading">
          <div class="stat-value">{{ stats.conversations }}</div>
          <div class="stat-label">对话次数</div>
          <svg class="stat-wave" viewBox="0 0 120 8" aria-hidden="true">
            <path d="M0 6c12-5 22 2 35-1s18-4 30 1 22 3 30 0 23-4 25-4" fill="none" stroke="var(--primary-lighter)" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" v-loading="statsLoading">
          <div class="stat-value">{{ stats.methods }}</div>
          <div class="stat-label">方法论</div>
          <svg class="stat-wave" viewBox="0 0 120 8" aria-hidden="true">
            <path d="M0 3c10 3 20-2 30 1s20 3 30-1 20-4 30 0 20 3 30-1" fill="none" stroke="var(--primary-lighter)" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </el-card>
      </el-col>
    </el-row>

    <h2 class="section-title">快速开始</h2>
    <el-row :gutter="20">
      <el-col v-for="action in quickActions" :key="action.path" :span="6">
        <el-card shadow="hover" class="action-card" @click="navigateTo(action.path)">
          <div class="action-icon" :style="{ color: action.color }">
            <iconify-icon :icon="action.icon" width="32" />
          </div>
          <div class="action-title">{{ action.title }}</div>
          <div class="action-desc">{{ action.desc }}</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  animation: fadeIn var(--transition-fade);
}

/* ---- 欢迎区 ---- */
.welcome {
  margin-bottom: 36px;
  padding: 28px 32px;
  background: var(--primary-gradient);
  border-radius: var(--radius-hand-drawn-soft);
  color: #fff;
  position: relative;
  overflow: hidden;
}

.welcome::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(255,255,255,0.12) 0%, transparent 70%);
  border-radius: 50%;
}

.welcome h1 {
  font-size: 26px;
  font-family: var(--font-heading);
  color: #fff;
  margin-bottom: 8px;
  position: relative;
  z-index: 1;
}

.welcome p {
  color: rgba(255, 255, 255, 0.88);
  font-size: 15px;
  font-family: var(--font-heading);
  position: relative;
  z-index: 1;
}

/* ---- 统计卡片 ---- */
.stats-row {
  margin-bottom: 36px;
}

.stat-card {
  text-align: center;
  cursor: default;
  overflow: visible;
  position: relative;
}

.stat-card :deep(.el-card__body) {
  padding-bottom: 20px;
  position: relative;
}

.stat-wave {
  display: block;
  width: 60%;
  margin: 10px auto 0;
  opacity: 0;
  transition: opacity var(--transition-hover-lift);
}

.stat-card:hover .stat-wave {
  opacity: 1;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
  font-family: var(--font-display);
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-top: 10px;
  font-weight: 500;
  font-family: var(--font-heading);
}

/* ---- 区块标题 ---- */
.section-title {
  font-size: 20px;
  font-family: var(--font-heading);
  color: var(--text-primary);
  margin-bottom: 20px;
  position: relative;
  padding-left: 14px;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 20px;
  background: var(--primary-gradient);
  border-radius: 2px;
}

/* ---- 快速操作卡片 ---- */
.action-card {
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-hover-lift);
  overflow: hidden;
  position: relative;
}

.action-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--primary-gradient);
  transform: scaleX(0);
  transition: transform var(--transition-hover-lift);
}

.action-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-lg) !important;
}

.action-card:hover::before {
  transform: scaleX(1);
}

.action-icon {
  width: 68px;
  height: 68px;
  border-radius: var(--radius-hand-drawn-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 18px;
  transition: all var(--transition-hover-lift);
  box-shadow: var(--shadow-sm);
  background: var(--primary-bg);
  border: 1.5px solid var(--primary-lighter);
}

.action-card:hover .action-icon {
  transform: scale(1.08);
  box-shadow: var(--shadow-md);
}

.action-title {
  font-size: 16px;
  font-weight: 600;
  font-family: var(--font-heading);
  color: var(--text-primary);
  margin-bottom: 6px;
}

.action-desc {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
  font-family: var(--font-body);
}
</style>
