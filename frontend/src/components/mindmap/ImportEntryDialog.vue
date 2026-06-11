<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { importQuestionsToMindmap } from '@/api/questionImport'
import PasteImportDialog from './PasteImportDialog.vue'
import QuestionSelector from './QuestionSelector.vue'
import ImportProgressDialog from './ImportProgressDialog.vue'
import type { QuestionListItem, ImportQuestionItem } from '@/types/questionImport'

const props = defineProps<{
  visible: boolean
  mindmapId: string
}>()

const emit = defineEmits<{
  (e: 'update:visible', v: boolean): void
  (e: 'imported', result: { importedCount: number; importedIds: string[]; updatedNodes: any[] }): void
}>()

// 子对话框状态
const pasteDialogVisible = ref(false)
const selectorDialogVisible = ref(false)
const progressDialogVisible = ref(false)

// 进度状态
const progressTotal = ref(0)
const progressCompleted = ref(0)
const progressResults = ref<any[]>([])

function handleSelectHistory() {
  emit('update:visible', false)
  selectorDialogVisible.value = true
}

function handleSelectPaste() {
  emit('update:visible', false)
  pasteDialogVisible.value = true
}

async function handleQuestionSelectorConfirm(selectedQuestions: QuestionListItem[]) {
  selectorDialogVisible.value = false

  // 转换为导入格式
  const importItems: ImportQuestionItem[] = selectedQuestions.map((q) => ({
    content: q.content,
    options: undefined,
    answer: q.answer || undefined,
    explanation: q.explanation || undefined,
    moduleId: q.moduleId || q.module_id,
    secondaryModule: q.modulePath || q.module_name,
  }))

  // 初始化进度
  progressTotal.value = importItems.length
  progressCompleted.value = 0
  progressResults.value = importItems.map((item) => ({
    contentPreview: item.content.substring(0, 50),
    status: 'pending' as const,
  }))
  progressDialogVisible.value = true

  // 开始导入
  try {
    const result = await importQuestionsToMindmap(props.mindmapId, {
      questions: importItems,
      allow_duplicate: false,
    })

    // 更新进度
    progressCompleted.value = result.imported_count + result.failed.length
    progressResults.value = progressResults.value.map((r, i) => {
      if (result.imported_ids[i]) {
        return { ...r, status: 'success' as const, questionId: result.imported_ids[i] }
      }
      const failedItem = result.failed.find((f: any) => f.index === i)
      if (failedItem) {
        return { ...r, status: 'failed' as const, error: failedItem.reason }
      }
      return r
    })

    emit('imported', {
      importedCount: result.imported_count,
      importedIds: result.imported_ids,
      updatedNodes: result.mindmap_update?.updated_nodes || [],
    })

    if (result.failed.length > 0) {
      ElMessage.warning(`导入完成：成功 ${result.imported_count} 道，失败 ${result.failed.length} 道`)
    }
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '导入失败')
    progressDialogVisible.value = false
  }
}

function handlePasteImported(result: { importedCount: number; importedIds: string[] }) {
  pasteDialogVisible.value = false
  emit('imported', { importedCount: result.importedCount, importedIds: result.importedIds, updatedNodes: [] })
}

function handleProgressCancel() {
  progressDialogVisible.value = false
  ElMessage.info('导入已取消')
}
</script>

<template>
  <!-- 导入方式选择 -->
  <el-dialog
    :model-value="visible"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    title="导入题目"
    width="420px"
    :close-on-click-modal="false"
  >
    <div class="import-options">
      <div class="import-option-card" @click="handleSelectHistory">
        <div class="option-icon">📋</div>
        <div class="option-info">
          <div class="option-title">从历史题目选择</div>
          <div class="option-desc">从AI问答记录中选择已有题目批量导入</div>
        </div>
      </div>

      <div class="import-option-card" @click="handleSelectPaste">
        <div class="option-icon">📝</div>
        <div class="option-info">
          <div class="option-title">粘贴题目内容</div>
          <div class="option-desc">粘贴纯文本或Markdown格式的题目，自动识别并导入</div>
        </div>
      </div>
    </div>

    <template #footer>
      <el-button @click="emit('update:visible', false)">取消</el-button>
    </template>
  </el-dialog>

  <!-- 子对话框 -->
  <PasteImportDialog
    v-model:visible="pasteDialogVisible"
    :mindmap-id="mindmapId"
    @imported="handlePasteImported"
  />

  <QuestionSelector
    v-model:visible="selectorDialogVisible"
    @confirm="handleQuestionSelectorConfirm"
  />

  <ImportProgressDialog
    v-model:visible="progressDialogVisible"
    :total="progressTotal"
    :completed="progressCompleted"
    :results="progressResults"
    @cancel="handleProgressCancel"
  />
</template>

<style scoped>
.import-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.import-option-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.import-option-card:hover {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.option-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.option-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.option-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.option-desc {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
</style>
