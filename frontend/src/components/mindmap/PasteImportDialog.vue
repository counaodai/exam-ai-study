<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { parseQuestions, importQuestionsToMindmap } from '@/api/questionImport'
import type { ParsedQuestion, ImportQuestionItem } from '@/types/questionImport'

const props = defineProps<{
  visible: boolean
  mindmapId: string
}>()

const emit = defineEmits<{
  (e: 'update:visible', v: boolean): void
  (e: 'imported', result: { importedCount: number; importedIds: string[] }): void
}>()

// 步骤控制：1=粘贴，2=预览编辑，3=结果
const step = ref(1)
const pasteContent = ref('')
const parsing = ref(false)
const parsedQuestions = ref<ParsedQuestion[]>([])
const parseErrors = ref<any[]>([])
const importing = ref(false)
const importResult = ref<{ importedCount: number; importedIds: string[]; failed: any[] } | null>(null)

// 编辑状态：每个题目的可编辑字段
const editedQuestions = ref<ImportQuestionItem[]>([])

const canParse = computed(() => pasteContent.value.trim().length > 0)

function initEditedQuestions() {
  editedQuestions.value = parsedQuestions.value.map((q) => ({
    content: q.content,
    options: q.options ? { ...q.options } : undefined,
    answer: q.answer || undefined,
    explanation: q.explanation || undefined,
    moduleId: q.suggestedModuleId,
    secondaryModule: q.suggestedModulePath || undefined,
  }))
}

async function handleParse() {
  if (!canParse.value) {
    ElMessage.warning('请输入题目内容后再识别')
    return
  }
  parsing.value = true
  try {
    const result = await parseQuestions({ content: pasteContent.value, format: 'plain' })
    parsedQuestions.value = result.questions
    parseErrors.value = result.parse_errors
    if (result.questions.length === 0) {
      ElMessage.warning('未识别出有效的题目结构，请检查格式是否正确')
    } else {
      initEditedQuestions()
      step.value = 2
      if (result.parse_errors.length > 0) {
        ElMessage.warning(`识别 ${result.questions.length} 道题目，${result.parse_errors.length} 条解析错误`)
      }
    }
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '解析失败，请重试')
  } finally {
    parsing.value = false
  }
}

async function handleConfirmImport() {
  importing.value = true
  try {
    const result = await importQuestionsToMindmap(props.mindmapId, {
      questions: editedQuestions.value,
    })
    importResult.value = {
      importedCount: result.imported_count,
      importedIds: result.imported_ids,
      failed: result.failed,
    }
    step.value = 3
    emit('imported', { importedCount: result.imported_count, importedIds: result.imported_ids })
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '导入失败，请重试')
  } finally {
    importing.value = false
  }
}

function handleClose() {
  step.value = 1
  pasteContent.value = ''
  parsedQuestions.value = []
  parseErrors.value = []
  importResult.value = null
  emit('update:visible', false)
}

function handleContinueImport() {
  step.value = 1
  pasteContent.value = ''
  parsedQuestions.value = []
  parseErrors.value = []
  importResult.value = null
}

function addOption(questionIndex: number) {
  const q = editedQuestions.value[questionIndex]
  if (!q.options) q.options = {}
  const keys = Object.keys(q.options)
  const nextKey = keys.length > 0
    ? String.fromCharCode(keys[keys.length - 1].charCodeAt(0) + 1)
    : 'A'
  if (nextKey <= 'J') {
    q.options[nextKey] = ''
  }
}

function removeOption(questionIndex: number, key: string) {
  const q = editedQuestions.value[questionIndex]
  if (q.options) {
    delete q.options[key]
  }
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="(v: boolean) => emit('update:visible', v)"
    :title="step === 1 ? '粘贴题目内容' : step === 2 ? '识别预览' : '导入结果'"
    width="720px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <!-- Step 1: 粘贴题目 -->
    <div v-if="step === 1" class="paste-step">
      <el-input
        v-model="pasteContent"
        type="textarea"
        :rows="12"
        placeholder="请粘贴题目内容，支持纯文本和 Markdown 格式&#10;&#10;示例&#10;1. 某公司计划组织员工...&#10;A. 方案一  B. 方案二&#10;C. 方案三  D. 方案四&#10;答案：B&#10;解析：本题考察的是..."
        :class="{ 'is-error': pasteContent.length > 10000 }"
      />
      <div class="paste-hint">
        <span>
          <iconify-icon icon="mdi:information-outline" width="14" style="vertical-align: -2px; margin-right: 4px"></iconify-icon>
          支持纯文本Markdown格式，题目用分隔
        </span>
        <span v-if="pasteContent.length > 10000" class="error-text">内容过长，请分批粘贴</span>
      </div>
    </div>

    <!-- Step 2: 预览编辑 -->
    <div v-if="step === 2" class="preview-step">
      <div class="preview-header">
        <span>识别 <strong>{{ parsedQuestions.length }}</strong> 道题目</span>
        <span v-if="parseErrors.length > 0" class="warning-text">
          共 {{ parseErrors.length }} 条解析错误
        </span>
      </div>

      <div class="question-list">
        <div
          v-for="(q, qi) in editedQuestions"
          :key="qi"
          class="question-edit-card"
        >
          <div class="card-header">题目 {{ qi + 1 }}</div>

          <el-form label-width="60px" size="small">
            <el-form-item label="题目">
              <el-input v-model="q.content" type="textarea" :rows="2" />
            </el-form-item>

            <el-form-item label="选项">
              <div class="options-editor">
                <div
                  v-for="(val, key) in q.options"
                  :key="key"
                  class="option-row"
                >
                  <span class="option-key">{{ key }}.</span>
                  <el-input v-model="q.options![key]" size="small" />
                  <el-button
                    type="danger"
                    circle
                    size="small"
                    @click="removeOption(qi, key)"
                  >
                    <iconify-icon icon="mdi:trash-can-outline" width="14"></iconify-icon>
                  </el-button>
                </div>
                <el-button size="small" @click="addOption(qi)">
                  <iconify-icon icon="mdi:plus" width="14" style="margin-right: 2px"></iconify-icon>
                  添加选项
                </el-button>
              </div>
            </el-form-item>

            <el-form-item label="答案">
              <el-input v-model="q.answer" placeholder="例如：B" style="width: 120px" />
            </el-form-item>

            <el-form-item label="解析">
              <el-input v-model="q.explanation" type="textarea" :rows="2" />
            </el-form-item>

            <el-form-item label="分类">
              <el-input
                v-model="q.secondaryModule"
                placeholder="判断推理 > 逻辑判断"
              />
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>

    <!-- Step 3: 导入结果 -->
    <div v-if="step === 3 && importResult" class="result-step">
      <div class="result-icon">
        <iconify-icon icon="mdi:check-circle-outline" width="64"></iconify-icon>
      </div>
      <div class="result-text">
        导入成功，共导入 <strong>{{ importResult.importedCount }}</strong> 道题目
      </div>
      <div v-if="importResult.failed.length > 0" class="result-failed">
        <p>导入失败的题目：</p>
        <div v-for="(f, fi) in importResult.failed" :key="fi" class="failed-item">
          <iconify-icon icon="mdi:close-circle-outline" width="14" style="vertical-align: -2px; margin-right: 4px; color: var(--accent-color)"></iconify-icon>
          {{ f.content_preview }} 因 {{ f.reason }}
        </div>
      </div>
    </div>

    <template #footer>
      <div v-if="step === 1">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="parsing" :disabled="!canParse" @click="handleParse">
          识别题目
        </el-button>
      </div>
      <div v-if="step === 2">
        <el-button @click="step = 1">返回修改</el-button>
        <el-button type="primary" :loading="importing" @click="handleConfirmImport">
          确认导入（{{ editedQuestions.length }}道题）
        </el-button>
      </div>
      <div v-if="step === 3">
        <el-button @click="handleClose">关闭</el-button>
        <el-button type="primary" @click="handleContinueImport">继续导入</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.paste-step {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.paste-step :deep(.el-textarea__inner) {
  border-radius: var(--radius-hand-drawn-soft);
  border: 2px solid var(--border-light);
  font-family: var(--font-heading);
  transition: all var(--transition-fade);
}

.paste-step :deep(.el-textarea__inner:hover) {
  border-color: var(--primary-lighter);
}

.paste-step :deep(.el-textarea__inner:focus) {
  border-color: var(--primary-color);
}

.paste-step :deep(.el-textarea__inner.is-error) {
  border-color: var(--accent-color);
}

.paste-hint {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-secondary);
}

.error-text {
  color: var(--accent-color);
  font-weight: 500;
}

.preview-step {
  max-height: 60vh;
  overflow-y: auto;
}

.preview-header {
  margin-bottom: 16px;
  font-size: 14px;
  color: var(--text-primary);
  font-family: var(--font-heading);
}

.preview-header strong {
  font-family: var(--font-display);
  color: var(--primary-color);
  font-size: 18px;
  margin: 0 2px;
}

.warning-text {
  color: var(--warning-color);
  margin-left: 8px;
}

.question-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  animation: fadeInUp var(--transition-fade) forwards;
}

.question-edit-card {
  border: 2px solid var(--border-light);
  border-radius: var(--radius-hand-drawn-soft);
  padding: 14px;
  background: linear-gradient(135deg, var(--primary-bg) 0%, var(--bg-surface) 100%);
  transition: all var(--transition-fade);
}

.question-edit-card:hover {
  border-color: var(--primary-lighter);
}

.card-header {
  font-weight: 600;
  font-family: var(--font-heading);
  margin-bottom: 10px;
  color: var(--primary-color);
}

.options-editor {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.option-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.option-key {
  font-weight: 600;
  font-family: var(--font-display);
  color: var(--primary-color);
  min-width: 24px;
}

.result-step {
  text-align: center;
  padding: 24px 0;
  animation: cardEnter var(--transition-fade) forwards;
}

.result-icon {
  color: var(--success-color);
  margin-bottom: 16px;
  display: flex;
  justify-content: center;
}

.result-text {
  font-size: 16px;
  font-family: var(--font-heading);
  color: var(--text-primary);
  margin-bottom: 16px;
}

.result-text strong {
  font-family: var(--font-display);
  font-size: 22px;
  color: var(--primary-color);
  margin: 0 3px;
}

.result-failed {
  text-align: left;
  background: rgba(192, 105, 74, 0.08);
  border: 2px dashed var(--primary-lighter);
  border-radius: var(--radius-hand-drawn-soft);
  padding: 14px;
  margin-top: 12px;
}

.result-failed p {
  margin: 0 0 8px;
  color: var(--accent-color);
  font-weight: 500;
  font-family: var(--font-heading);
}

.failed-item {
  font-size: 13px;
  color: var(--text-secondary);
  padding: 6px 0;
  border-bottom: 1px dashed var(--border-light);
}

.failed-item:last-child {
  border-bottom: none;
}
</style>
