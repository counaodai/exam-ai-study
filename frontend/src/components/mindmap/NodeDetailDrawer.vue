<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useMindMapStore } from '@/stores/mindmap'
import type { MindMapNode, NodeQuestionItem } from '@/types/mindmap'

const props = defineProps<{
  visible: boolean
  node: MindMapNode | null
  mapId: string
}>()

const emit = defineEmits<{
  (e: 'update:visible', val: boolean): void
  (e: 'viewMethod', nodeId: string): void
}>()

const router = useRouter()
const mindMapStore = useMindMapStore()

const currentPage = ref(1)
const pageSize = 10

const questions = computed(() => mindMapStore.nodeQuestions?.items ?? [])
const total = computed(() => mindMapStore.nodeQuestions?.total ?? 0)
const loading = computed(() => mindMapStore.nodeQuestionsLoading)

const nodeTypeLabel = computed(() => {
  const map: Record<string, string> = {
    module: '一级模块',
    topic: '主题节点',
    method: '方法论',
    question: '题目节点',
  }
  return props.node ? map[props.node.type] || props.node.type : ''
})

const hasMethod = computed(() => {
  return props.node?.metadata?.method_summary != null
})

async function loadQuestions() {
  if (!props.node) return
  currentPage.value = 1
  await mindMapStore.fetchNodeQuestions(props.mapId, props.node.id, 1, pageSize)
}

function handlePageChange(page: number) {
  currentPage.value = page
  if (props.node) {
    mindMapStore.fetchNodeQuestions(props.mapId, props.node.id, page, pageSize)
  }
}

function handleClose() {
  emit('update:visible', false)
}

function handleViewMethod() {
  if (props.node?.metadata?.method_summary) {
    router.push(`/methods/${props.node.metadata.method_summary}`)
  }
}

function handleViewQuestion(question: NodeQuestionItem) {
  ElMessage.info(`查看题目：${question.content.substring(0, 30)}...`)
}

function getDifficultyStars(difficulty: number | null): string {
  if (!difficulty) return '未知'
  return '★'.repeat(difficulty) + '☆'.repeat(5 - difficulty)
}

watch(() => props.visible, (val) => {
  if (val && props.node) {
    loadQuestions()
  }
})
</script>

<template>
  <el-drawer
    :model-value="visible"
    @update:model-value="handleClose"
    title="节点详情"
    direction="rtl"
    size="420px"
    :before-close="handleClose"
  >
    <div v-if="node" class="node-detail">
      <div class="node-info">
        <div class="info-row">
          <span class="info-label">节点名称</span>
          <span class="info-value">{{ node.label }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">类型</span>
          <el-tag size="small">{{ nodeTypeLabel }}</el-tag>
        </div>
        <div class="info-row">
          <span class="info-label">关联题目</span>
          <span class="info-value">{{ total }} 道</span>
        </div>
        <div class="info-row">
          <span class="info-label">掌握度</span>
          <el-progress
            :percentage="node.mastery"
            :stroke-width="10"
            style="width: 160px"
          />
        </div>
        <div class="info-row">
          <span class="info-label">已生成方法论</span>
          <el-tag :type="hasMethod ? 'success' : 'info'" size="small">
            {{ hasMethod ? '是' : '否' }}
          </el-tag>
        </div>
        <el-button
          v-if="hasMethod"
          type="primary"
          size="small"
          @click="handleViewMethod"
        >
          查看方法论
        </el-button>
      </div>

      <el-divider />

      <div class="questions-section">
        <h4>关联题目列表</h4>

        <div v-if="loading" class="loading-container">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载中...</span>
        </div>

        <div v-else-if="questions.length === 0" class="empty-container">
          <el-empty description="暂无关联题目" :image-size="80" />
        </div>

        <div v-else class="questions-list">
          <el-collapse>
            <el-collapse-item
              v-for="(q, index) in questions"
              :key="q.id"
              :name="q.id"
            >
              <template #title>
                <div class="question-title">
                  <span class="question-index">{{ (currentPage - 1) * pageSize + index + 1 }}.</span>
                  <span class="question-content">{{ q.content.substring(0, 60) }}{{ q.content.length > 60 ? '...' : '' }}</span>
                </div>
              </template>
              <div class="question-detail">
                <div class="question-meta">
                  <span v-if="q.source">来源：{{ q.source }}</span>
                  <span>难度：{{ getDifficultyStars(q.difficulty) }}</span>
                  <span>掌握度：{{ q.mastery }}%</span>
                </div>
                <div v-if="q.answer" class="question-answer">
                  <strong>答案：</strong>{{ q.answer }}
                </div>
                <div v-if="q.explanation" class="question-explanation">
                  <strong>解析：</strong>{{ q.explanation }}
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>

          <div v-if="total > pageSize" class="pagination-container">
            <el-pagination
              :current-page="currentPage"
              :page-size="pageSize"
              :total="total"
              layout="prev, pager, next"
              @current-change="handlePageChange"
            />
          </div>
        </div>
      </div>
    </div>
  </el-drawer>
</template>

<style scoped>
.node-detail {
  padding: 0 4px;
}

.node-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-label {
  font-size: 13px;
  color: #909399;
  min-width: 90px;
}

.info-value {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.questions-section h4 {
  margin: 0 0 12px;
  font-size: 15px;
  color: #303133;
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px 0;
  color: #909399;
}

.empty-container {
  padding: 20px 0;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.question-title {
  display: flex;
  gap: 6px;
  align-items: flex-start;
}

.question-index {
  color: #409eff;
  font-weight: 600;
  flex-shrink: 0;
}

.question-content {
  font-size: 13px;
  color: #303133;
  line-height: 1.5;
}

.question-detail {
  padding: 8px 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.question-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.question-answer {
  font-size: 13px;
  color: #303133;
  line-height: 1.6;
}

.question-explanation {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  background: #f5f7fa;
  padding: 8px 12px;
  border-radius: 4px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding: 16px 0;
}
</style>
