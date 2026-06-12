<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useMethodStore } from '@/stores/method'

const route = useRoute()
const router = useRouter()
const methodStore = useMethodStore()

onMounted(() => {
  const id = route.params.id as string
  if (id) {
    methodStore.fetchMethodDetail(id)
  }
})

function handleBack() {
  router.push('/methods')
}

function handleViewQuestions() {
  if (methodStore.currentMethod?.module_id) {
    router.push(`/mindmap/${methodStore.currentMethod.module_id}`)
  }
}
</script>

<template>
  <div class="method-detail-page">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="handleBack">
          <iconify-icon icon="mdi:arrow-left" width="16" style="margin-right: 4px" />
          返回列表
        </el-button>
        <h1 v-if="methodStore.currentMethod">
          <iconify-icon icon="mdi:lightbulb-on-outline" class="title-icon" />
          {{ methodStore.currentMethod.method_name }}
        </h1>
      </div>
      <div class="header-right">
        <el-tag v-if="methodStore.currentMethod?.is_auto_generated" type="success">
          AI 自动生成
        </el-tag>
        <el-tag v-else type="warning">
          手动编辑
        </el-tag>
      </div>
    </div>

    <div v-if="methodStore.loading" class="loading-state">
      <el-skeleton :rows="10" animated />
    </div>

    <div v-else-if="methodStore.currentMethod" class="method-content">
      <el-card class="section-card summary-card">
        <template #header>
          <div class="card-title">
            <iconify-icon icon="mdi:trophy-outline" width="20" />
            <span>方法论总结</span>
          </div>
        </template>
        <p class="summary-text">{{ methodStore.currentMethod.summary }}</p>
        <div class="meta-info">
          <span>关联题目：{{ methodStore.currentMethod.question_count }} 道</span>
          <span>生成时间：{{ new Date(methodStore.currentMethod.created_at).toLocaleDateString() }}</span>
        </div>
      </el-card>

      <el-card v-if="methodStore.currentMethod.recognition" class="section-card">
        <template #header>
          <div class="card-title">
            <iconify-icon icon="mdi:file-document-outline" width="20" />
            <span>识别特征</span>
          </div>
        </template>
        <h4>{{ methodStore.currentMethod.recognition.title }}</h4>
        <p class="recognition-content">{{ methodStore.currentMethod.recognition.content }}</p>
      </el-card>

      <el-card class="section-card">
        <template #header>
          <div class="card-title">
            <iconify-icon icon="mdi:file-document-outline" width="20" />
            <span>解题步骤</span>
          </div>
        </template>
        <el-timeline>
          <el-timeline-item
            v-for="step in methodStore.currentMethod.steps"
            :key="step.step"
            :timestamp="`步骤 ${step.step}`"
            placement="top"
            type="primary"
          >
            <el-card shadow="never">
              <h4>{{ step.title }}</h4>
              <p>{{ step.description }}</p>
              <div v-if="step.example" class="step-example">
                <strong>示例：</strong>{{ step.example }}
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </el-card>

      <el-card v-if="methodStore.currentMethod.traps?.length" class="section-card">
        <template #header>
          <div class="card-title">
            <iconify-icon icon="mdi:alert-circle-outline" width="20" />
            <span>常见陷阱</span>
          </div>
        </template>
        <div class="traps-list">
          <div
            v-for="(trap, index) in methodStore.currentMethod.traps"
            :key="index"
            class="trap-item"
          >
            <div class="trap-header">
              <el-tag type="danger" size="small">陷阱 {{ index + 1 }}</el-tag>
              <span class="trap-text">{{ trap.trap }}</span>
            </div>
            <div class="trap-solution">
              <el-tag type="success" size="small">解决</el-tag>
              <span>{{ trap.solution }}</span>
            </div>
          </div>
        </div>
      </el-card>

      <div class="bottom-cards">
        <el-card v-if="methodStore.currentMethod.quick_tips?.length" class="section-card">
          <template #header>
            <div class="card-title">
              <iconify-icon icon="mdi:white-balance-sunny" width="20" />
              <span>速记技巧</span>
            </div>
          </template>
          <ul class="tips-list">
            <li v-for="(tip, index) in methodStore.currentMethod.quick_tips" :key="index">
              {{ tip }}
            </li>
          </ul>
        </el-card>

        <el-card v-if="methodStore.currentMethod.key_formulas?.length" class="section-card">
          <template #header>
            <div class="card-title">
              <iconify-icon icon="mdi:file-document-outline" width="20" />
              <span>关键公式</span>
            </div>
          </template>
          <ul class="formulas-list">
            <li v-for="(formula, index) in methodStore.currentMethod.key_formulas" :key="index">
              {{ formula }}
            </li>
          </ul>
        </el-card>
      </div>

      <div class="action-bar">
        <el-button type="primary" @click="handleViewQuestions">
          <iconify-icon icon="mdi:file-document-outline" width="16" style="margin-right: 4px" />
          查看关联题目
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.method-detail-page {
  padding: 0 4px;
  animation: fadeIn var(--transition-fade);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h1 {
  margin: 0;
  font-size: 26px;
  font-family: var(--font-display);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-left h1 .title-icon {
  color: var(--primary-color);
  font-size: 28px;
}

.loading-state {
  padding: 20px;
}

.method-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-card {
  width: 100%;
  overflow: hidden;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 17px;
  font-weight: 600;
  font-family: var(--font-heading);
  color: var(--text-primary);
}

.summary-card :deep(.el-card__body) {
  background: linear-gradient(135deg, var(--primary-bg) 0%, var(--bg-surface) 100%);
  border-left: 4px solid var(--primary-color);
}

.summary-text {
  font-size: 16px;
  line-height: 1.9;
  color: var(--text-primary);
  font-family: var(--font-body);
  letter-spacing: 0.02em;
  margin: 0 0 14px 0;
}

.meta-info {
  display: flex;
  gap: 28px;
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 500;
}

.recognition-content {
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-regular);
  margin: 10px 0 0;
  padding: 12px 16px;
  background: var(--bg-muted);
  border-radius: var(--radius-hand-drawn-soft);
  border-left: 3px solid var(--accent-color);
}

:deep(.el-timeline) {
  padding-left: 4px;
}

:deep(.el-timeline-item__timestamp) {
  font-weight: 600;
  font-family: var(--font-display);
  color: var(--primary-color);
  font-size: 14px;
}

:deep(.el-timeline-item__node) {
  border-color: var(--primary-color);
  background: var(--primary-bg);
}

:deep(.el-card[shadow="never"]) {
  transition: var(--transition-hover-lift);
}

:deep(.el-card[shadow="never"]:hover) {
  box-shadow: var(--shadow-sm) !important;
  transform: translateX(4px);
}

:deep(.el-card[shadow="never"] .el-card__body) {
  padding: 14px 16px;
}

.step-example {
  margin-top: 10px;
  padding: 10px 14px;
  background: var(--bg-muted);
  border-radius: var(--radius-hand-drawn-soft);
  font-size: 13px;
  color: var(--text-regular);
  border-left: 3px solid var(--accent-color);
  line-height: 1.6;
}

.traps-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.trap-item {
  padding: 14px 16px;
  background: linear-gradient(90deg, rgba(192, 105, 74, 0.08) 0%, transparent 100%);
  border-radius: var(--radius-hand-drawn-soft);
  border: 2px solid rgba(192, 105, 74, 0.18);
  transition: var(--transition-hover-lift);
}

.trap-item:hover {
  box-shadow: var(--shadow-sm);
  transform: translateX(4px);
}

.trap-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.trap-text {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.trap-solution {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--primary-color);
  font-weight: 500;
}

.bottom-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.tips-list,
.formulas-list {
  margin: 0;
  padding-left: 20px;
}

.tips-list li,
.formulas-list li {
  font-size: 14px;
  line-height: 1.9;
  color: var(--text-regular);
  margin-bottom: 8px;
  padding-left: 8px;
  font-family: var(--font-body);
}

.tips-list li::marker {
  color: var(--primary-color);
  font-family: var(--font-display);
}

.formulas-list li::marker {
  color: var(--accent-color);
  font-family: var(--font-display);
}

.action-bar {
  display: flex;
  gap: 12px;
  padding: 24px 0 8px;
}

@media (max-width: 768px) {
  .bottom-cards {
    grid-template-columns: 1fr;
  }
}
</style>
