<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Upload as UploadIcon, ChatDotRound, Share, DataAnalysis } from '@element-plus/icons-vue'
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
  { title: '导入文档', desc: '上传公考学习资料', icon: UploadIcon, path: '/upload', color: '#409eff' },
  { title: 'AI问答', desc: '智能解答公考题目', icon: ChatDotRound, path: '/chat', color: '#67c23a' },
  { title: '思维导图', desc: '可视化知识体系', icon: Share, path: '/mindmap', color: '#e6a23c' },
  { title: '统计分析', desc: '查看学习数据', icon: DataAnalysis, path: '/analysis', color: '#f56c6c' },
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
      <h1>欢迎使用公考AI智能学习系统</h1>
      <p>基于 RAG 知识库的智能学习助手，助你高效备考</p>
    </div>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" v-loading="statsLoading">
          <div class="stat-value">{{ stats.documents }}</div>
          <div class="stat-label">已导入文档</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" v-loading="statsLoading">
          <div class="stat-value">{{ stats.questions }}</div>
          <div class="stat-label">累计题目</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" v-loading="statsLoading">
          <div class="stat-value">{{ stats.conversations }}</div>
          <div class="stat-label">对话次数</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" v-loading="statsLoading">
          <div class="stat-value">{{ stats.methods }}</div>
          <div class="stat-label">方法论</div>
        </el-card>
      </el-col>
    </el-row>

    <h2 class="section-title">快速开始</h2>
    <el-row :gutter="20">
      <el-col v-for="action in quickActions" :key="action.path" :span="6">
        <el-card shadow="hover" class="action-card" @click="navigateTo(action.path)">
          <div class="action-icon" :style="{ backgroundColor: action.color + '15', color: action.color }">
            <el-icon :size="32"><component :is="action.icon" /></el-icon>
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
  animation: fadeIn 0.5s ease-out;
}

.welcome {
  margin-bottom: 36px;
  padding: 28px 32px;
  background: var(--primary-gradient);
  border-radius: var(--radius-lg);
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
  position: relative;
  z-index: 1;
}

.stats-row {
  margin-bottom: 36px;
}

.stat-card {
  text-align: center;
  cursor: default;
  overflow: hidden;
  position: relative;
}

.stat-card::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 3px;
  background: var(--primary-gradient);
  border-radius: 2px;
  transition: width var(--transition-normal);
}

.stat-card:hover::after {
  width: 60%;
}

.stat-value {
  font-size: 36px;
  font-weight: 700;
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
}

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

.action-card {
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-normal);
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
  transition: transform var(--transition-normal);
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
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 18px;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
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
}
</style>
