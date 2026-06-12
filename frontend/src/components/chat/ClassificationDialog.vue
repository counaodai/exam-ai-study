<script setup lang="ts">
import { ref, watch } from 'vue'
import type { ClassificationResult } from '@/types/chat'

interface ModuleOption {
  name: string
  children?: { name: string }[]
}

const props = defineProps<{
  visible: boolean
  classification: ClassificationResult | null
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  confirm: [result: { module: string; sub_module: string }]
}>()

const selectedModule = ref('')
const selectedSubModule = ref('')

const moduleOptions: ModuleOption[] = [
  {
    name: '言语理解与表达',
    children: [
      { name: '逻辑填空' },
      { name: '片段阅读' },
      { name: '语句表达' },
    ],
  },
  {
    name: '数量关系',
    children: [
      { name: '数学运算' },
      { name: '数字推理' },
    ],
  },
  {
    name: '判断推理',
    children: [
      { name: '图形推理' },
      { name: '定义判断' },
      { name: '类比推理' },
      { name: '逻辑判断' },
    ],
  },
  {
    name: '资料分析',
    children: [
      { name: '增长率' },
      { name: '增长量' },
      { name: '比重' },
      { name: '倍数' },
      { name: '平均数' },
      { name: '综合分析' },
    ],
  },
  {
    name: '常识判断',
    children: [
      { name: '政治' },
      { name: '法律' },
      { name: '经济' },
      { name: '历史' },
      { name: '地理' },
      { name: '科技' },
      { name: '文学' },
    ],
  },
]

const currentSubModules = ref<{ name: string }[]>([])

watch(
  () => props.visible,
  (val) => {
    if (val && props.classification) {
      selectedModule.value = props.classification.module
      selectedSubModule.value = props.classification.sub_module
      updateSubModules(selectedModule.value)
    }
  },
)

watch(selectedModule, (val) => {
  updateSubModules(val)
  if (!currentSubModules.value.find((m) => m.name === selectedSubModule.value)) {
    selectedSubModule.value = ''
  }
})

function updateSubModules(moduleName: string) {
  const found = moduleOptions.find((m) => m.name === moduleName)
  currentSubModules.value = found?.children || []
}

function handleClose() {
  emit('update:visible', false)
}

function handleConfirm() {
  if (!selectedModule.value) return
  emit('confirm', {
    module: selectedModule.value,
    sub_module: selectedSubModule.value,
  })
  handleClose()
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    title="修正分类结果"
    width="480px"
    @close="handleClose"
  >
    <div v-if="classification" class="dialog-content">
      <div class="current-classification">
        <span class="label">当前分类：</span>
        <el-tag type="info">{{ classification.module }}</el-tag>
        <el-tag v-if="classification.sub_module" type="info">
          {{ classification.sub_module }}
        </el-tag>
        <el-tag type="warning" effect="plain">
          置信度: {{ Math.round(classification.confidence * 100) }}%
        </el-tag>
      </div>

      <el-divider />

      <el-form label-width="80px">
        <el-form-item label="一级模块">
          <el-select v-model="selectedModule" placeholder="请选择一级模块" style="width: 100%">
            <el-option
              v-for="item in moduleOptions"
              :key="item.name"
              :label="item.name"
              :value="item.name"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="二级分类">
          <el-select
            v-model="selectedSubModule"
            placeholder="请选择二级分类"
            style="width: 100%"
            :disabled="currentSubModules.length === 0"
          >
            <el-option
              v-for="item in currentSubModules"
              :key="item.name"
              :label="item.name"
              :value="item.name"
            />
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" @click="handleConfirm">确认修正</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.dialog-content {
  padding: 4px 8px;
}

.current-classification {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  padding: 12px 16px;
  background: var(--bg-muted);
  border-radius: var(--radius-hand-drawn-soft);
  margin-bottom: 4px;
}

.label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
  font-family: var(--font-heading);
}

:deep(.el-divider) {
  margin: 16px 0;
}
</style>
