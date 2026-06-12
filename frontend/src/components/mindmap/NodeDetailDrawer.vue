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
    size="440px"
    :before-close="handleClose"
  >
    <div v-if="node" class="node-detail">
      <!-- 节点信息卡片 -->
      <div class="node-info">
        <div class="info-title">
          <iconify-icon icon="mdi:leaf-circle-outline" width="22" class="title-icon" />
          <span>{{ node.label }}</span>
        </div>

        <div class="info-row">
          <span class="info-label">
            <iconify-icon icon="mdi:tag-outline" width="14" />
            类型
          </span>
          <el-tag size="small">{{ nodeTypeLabel }}</el-tag>
        </div>

        <div class="info-row">
          <span class="info-label">
            <iconify-icon icon="mdi:file-document-outline" width="14" />
            关联题目
          </span>
          <span class="info-value-num">{{ total }} 道</span>
        </div>

        <div class="info-row">
          <span class="info-label">
            <iconify-icon icon="mdi:chart-line-variant" width="14" />
            掌握度
          </span>
          <el-progress
            :percentage="node.mastery"
            :stroke-width="10"
            style="width: 170px"
          />
        </div>

        <div class="info-row">
          <span class="info-label">
            <iconify-icon icon="mdi:lightbulb-on-outline" width="14" />
            已生成方法论
          </span>
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
          <iconify-icon icon="mdi:book-open-page-variant-outline" width="14" style="margin-right: 4px" />
          查看方法论
        </el-button>
      </div>

      <el-divider />

      <!-- 关联题目列表 -->
      <div class="questions-section">
        <h4>
          <iconify-icon icon="mdi:format-list-bulleted" width="18" class="section-icon" />
          关联题目列表
        </h4>

        <div v-if="loading" class="loading-container">
          <iconify-icon icon="mdi:loading" width="18" class="spin-icon" />
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
                <div class="question-title" @click="handleViewQuestion(q)">
                  <span class="question-index">{{ (currentPage - 1) * pageSize + index + 1 }}.</span>
                  <span class="question-content">{{ q.content.substring(0, 60) }}{{ q.content.length > 60 ? '...' : '' }}</span>
                </div>
              </template>
              <div class="question-detail">
                <div class="question-meta">
                  <span v-if="q.source">
                    <iconify-icon icon="mdi:source-branch" width="12" />
                    {{ q.source }}
                  </span>
                  <span>
                    <iconify-icon icon="mdi:star-outline" width="12" />
                    {{ getDifficultyStars(q.difficulty) }}
                  </span>
                  <span>
                    <iconify-icon icon="mdi:chart-line-variant" width="12" />
                    掌握度 <span class="meta-num">{{ q.mastery }}%</span>
                  </span>
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
  font-family: var(--font-heading);
  color: var(--text-primary);
}

/* —— 节点信息块 —— */
.node-info {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 16px;
  background: var(--bg-muted);
  border: 2px solid var(--border-color);
  border-radius: var(--radius-hand-drawn-soft);
}

.info-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--text-primary);
  font-weight: 700;
  padding-bottom: 10px;
  border-bottom: 1.5px dashed var(--border-color);
}

.title-icon {
  color: var(--primary-color);
}

.info-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-label {
  font-size: 13px;
  color: var(--text-secondary);
  min-width: 100px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-family: var(--font-heading);
}

.info-value-num {
  font-family: var(--font-display);
  font-size: 16px;
  color: var(--primary-color);
  font-weight: 700;
}

/* —— 题目列表区 —— */
.questions-section h4 {
  margin: 0 0 14px;
  font-size: 16px;
  font-family: var(--font-heading);
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.section-icon {
  color: var(--primary-color);
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px 0;
  color: var(--text-secondary);
}

.spin-icon {
  color: var(--primary-color);
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
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
  font-family: var(--font-heading);
}

.question-index {
  color: var(--primary-color);
  font-family: var(--font-display);
  font-weight: 700;
  flex-shrink: 0;
}

.question-content {
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.5;
}

.question-detail {
  padding: 8px 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.question-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 12px;
  color: var(--text-secondary);
}

.question-meta span {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.meta-num {
  font-family: var(--font-display);
  font-weight: 700;
  color: var(--primary-color);
}

.question-answer {
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.6;
  padding: 8px 12px;
  background: rgba(91, 140, 90, 0.08);
  border: 2px solid rgba(91, 140, 90, 0.18);
  border-radius: var(--radius-hand-drawn-soft);
}

.question-answer strong {
  color: var(--primary-color);
}

.question-explanation {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  background: var(--bg-muted);
  border: 2px solid var(--border-color);
  padding: 8px 12px;
  border-radius: var(--radius-hand-drawn-soft);
}

.question-explanation strong {
  color: var(--accent-color);
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding: 16px 0;
}

/* —— 折叠面板手绘软圆角 —— */
:deep(.el-collapse) {
  border-top: 2px solid var(--border-color);
  border-bottom: 2px solid var(--border-color);
}

:deep(.el-collapse-item__header) {
  font-family: var(--font-heading);
  color: var(--text-primary);
  background: transparent;
  border-bottom: 1.5px dashed var(--border-color);
}

:deep(.el-collapse-item__wrap) {
  background: transparent;
  border-bottom: 1.5px dashed var(--border-color);
}

:deep(.el-collapse-item:last-child .el-collapse-item__header),
:deep(.el-collapse-item:last-child .el-collapse-item__wrap) {
  border-bottom: none;
}

:deep(.el-divider) {
  border-top-color: var(--border-color);
  border-top-style: dashed;
}
</style>
