<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getQuestionList } from '@/api/questionImport'
import type { QuestionListItem } from '@/types/questionImport'

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  (e: 'update:visible', v: boolean): void
  (e: 'confirm', questions: QuestionListItem[]): void
}>()

const loading = ref(false)
const questions = ref<QuestionListItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const keyword = ref('')
const selectedIds = ref<Set<string>>(new Set())

const isAllSelected = ref(false)
const isIndeterminate = ref(false)

async function fetchQuestions() {
  loading.value = true
  try {
    const result = await getQuestionList({
      page: page.value,
      page_size: pageSize.value,
      keyword: keyword.value || undefined,
      is_valid: true,
    })
    questions.value = result.items
    total.value = result.total
  } catch (err: any) {
    ElMessage.error('获取题目列表失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  fetchQuestions()
}

function handlePageChange(p: number) {
  page.value = p
  fetchQuestions()
}

function toggleSelect(id: string) {
  const newSet = new Set(selectedIds.value)
  if (newSet.has(id)) {
    newSet.delete(id)
  } else {
    newSet.add(id)
  }
  selectedIds.value = newSet
  updateSelectAllState()
}

function toggleSelectAll() {
  if (isAllSelected.value) {
    selectedIds.value = new Set()
  } else {
    selectedIds.value = new Set(questions.value.map((q) => q.id))
  }
  updateSelectAllState()
}

function updateSelectAllState() {
  const allIds = questions.value.map((q) => q.id)
  const selectedCount = allIds.filter((id) => selectedIds.value.has(id)).length
  isAllSelected.value = selectedCount === allIds.length && allIds.length > 0
  isIndeterminate.value = selectedCount > 0 && selectedCount < allIds.length
}

function handleConfirm() {
  const selected = questions.value.filter((q) => selectedIds.value.has(q.id))
  if (selected.length === 0) {
    ElMessage.warning('选一个吧，至少挑一道题')
    return
  }
  emit('confirm', selected)
  selectedIds.value = new Set()
  emit('update:visible', false)
}

watch(() => props.visible, (val) => {
  if (val) {
    selectedIds.value = new Set()
    page.value = 1
    fetchQuestions()
  }
})

onMounted(() => {
  if (props.visible) {
    fetchQuestions()
  }
})
</script>

<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    title="从历史题目选择"
    width="720px"
    :close-on-click-modal="false"
  >
    <div class="selector-toolbar">
      <el-input
        v-model="keyword"
        placeholder="搜索题目..."
        clearable
        style="width: 260px"
        @keyup.enter="handleSearch"
        @clear="handleSearch"
      >
        <template #prefix>
          <iconify-icon icon="mdi:magnify" width="16" style="color: var(--text-muted)"></iconify-icon>
        </template>
      </el-input>
      <span class="selected-count">
        <iconify-icon icon="mdi:check-circle-outline" width="14" style="vertical-align: -2px; margin-right: 4px"></iconify-icon>
        已选 <strong>{{ selectedIds.size }}</strong> 道
      </span>
    </div>

    <el-table
      v-loading="loading"
      :data="questions"
      style="width: 100%"
      max-height="420px"
      @selection-change="() => {}"
    >
      <el-table-column width="50">
        <template #header>
          <el-checkbox
            v-model="isAllSelected"
            :indeterminate="isIndeterminate"
            @change="toggleSelectAll"
          />
        </template>
        <template #default="{ row }">
          <el-checkbox
            :model-value="selectedIds.has(row.id)"
            @change="toggleSelect(row.id)"
          />
        </template>
      </el-table-column>
      <el-table-column label="题目内容" min-width="300">
        <template #default="{ row }">
          <div class="question-content">
            <span class="content-text">{{ row.content }}</span>
            <el-tag v-if="row.modulePath" size="small" type="info" class="module-tag">
              {{ row.modulePath }}
            </el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="来源" width="100">
        <template #default="{ row }">
          <el-tag size="small" :type="row.source === '手动导入' ? 'success' : 'info'">
            {{ row.source || 'AI问答' }}
          </el-tag>
        </template>
      </el-table-column>
      <template #empty>
        <el-empty description="还是空的呢，先去添加一些吧" />
      </template>
    </el-table>

    <div class="selector-pagination">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        small
        @current-change="handlePageChange"
      />
    </div>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :disabled="selectedIds.size === 0" @click="handleConfirm">
        确认选择（{{ selectedIds.size }} 道）
      </el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.selector-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  padding: 10px 14px;
  background: linear-gradient(135deg, var(--primary-bg) 0%, var(--bg-surface) 100%);
  border: 2px dashed var(--primary-lighter);
  border-radius: var(--radius-hand-drawn-soft);
}

.selected-count {
  font-size: 14px;
  font-family: var(--font-heading);
  color: var(--primary-color);
  font-weight: 500;
}

.selected-count strong {
  font-family: var(--font-display);
  font-size: 18px;
  margin: 0 2px;
  color: var(--primary-color);
}

.question-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.content-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 400px;
  color: var(--text-primary);
}

.module-tag {
  align-self: flex-start;
}

.selector-pagination {
  display: flex;
  justify-content: center;
  margin-top: 14px;
}
</style>
