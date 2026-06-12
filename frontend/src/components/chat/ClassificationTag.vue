<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import type { ClassificationResult, MindMapUpdateResult } from '@/types/chat'
import { updateMessageClassification } from '@/api/chat'

interface Props {
  classification: ClassificationResult
  mindmapUpdate?: MindMapUpdateResult | null
  messageId?: string
}

const props = defineProps<Props>()
const router = useRouter()

const emit = defineEmits<{
  corrected: [data: { classification: ClassificationResult; mindmap_update: MindMapUpdateResult | null }]
}>()

const modulePath = computed(() => {
  if (props.classification.sub_module) {
    return `${props.classification.module} > ${props.classification.sub_module}`
  }
  return props.classification.module
})

const confidenceType = computed(() => {
  if (props.classification.confidence >= 0.8) return 'success'
  if (props.classification.confidence >= 0.6) return 'warning'
  return 'danger'
})

const confidenceText = computed(() => {
  return `${Math.round(props.classification.confidence * 100)}%`
})

const masteryColor = computed(() => {
  if (!props.mindmapUpdate) return ''
  if (props.mindmapUpdate.mastery >= 80) return 'var(--success-color)'
  if (props.mindmapUpdate.mastery >= 60) return 'var(--warning-color)'
  return 'var(--accent-color)'
})

const showCorrection = ref(false)
const correcting = ref(false)
const correctionModule = ref('')
const correctionSubModule = ref('')

const primaryModules = ['言语理解与表达', '数量关系', '判断推理', '资料分析', '常识判断']

const secondaryModuleMap: Record<string, string[]> = {
  '言语理解与表达': ['逻辑填空', '片段阅读', '语句表达'],
  '数量关系': ['数学运算', '数字推理'],
  '判断推理': ['图形推理', '定义判断', '类比推理', '逻辑判断'],
  '资料分析': ['增长量', '增长率', '比重', '倍数', '平均数', '综合分析'],
  '常识判断': ['政治', '法律', '经济', '历史', '地理', '科技', '文学'],
}

const currentSecondaryModules = computed(() => {
  if (!correctionModule.value) return []
  return secondaryModuleMap[correctionModule.value] || []
})

function handleViewMindMap() {
  if (props.mindmapUpdate?.mindmap_id) {
    router.push(`/mindmap/${props.mindmapUpdate.mindmap_id}`)
  }
}

function handleViewMethod() {
  if (props.mindmapUpdate?.method_id) {
    router.push(`/methods/${props.mindmapUpdate.method_id}`)
  }
}

function handleCorrect() {
  correctionModule.value = props.classification.module
  correctionSubModule.value = props.classification.sub_module
  showCorrection.value = true
}

async function confirmCorrection() {
  if (!props.messageId) return
  correcting.value = true
  try {
    const result = await updateMessageClassification(props.messageId, {
      module: correctionModule.value,
      sub_module: correctionSubModule.value || undefined,
    })
    emit('corrected', {
      classification: result.classification,
      mindmap_update: result.mindmap_update,
    })
    showCorrection.value = false
  } catch (e) {
    console.error('分类修正失败', e)
  } finally {
    correcting.value = false
  }
}

watch(() => correctionModule.value, () => {
  correctionSubModule.value = ''
})
</script>

<template>
  <div class="classification-container">
    <div class="classification-tag-row">
      <iconify-icon icon="mdi:tag-outline" width="16" class="tag-icon" />
      <span class="tag-label">已归类：</span>
      <el-tag :type="confidenceType" effect="plain" size="small">
        {{ modulePath }}
      </el-tag>
      <el-tag type="info" effect="plain" size="small" class="confidence-tag">
        置信度 {{ confidenceText }}
      </el-tag>
    </div>

    <div v-if="mindmapUpdate?.updated" class="mindmap-update-info">
      <el-divider content-position="left">
        <span class="divider-text">思维导图已更新</span>
      </el-divider>

      <div class="update-stats">
        <el-statistic title="节点题目数" :value="mindmapUpdate.question_count">
          <template #suffix>
            <span class="stat-suffix">道</span>
          </template>
        </el-statistic>
        <el-statistic title="掌握度" :value="mindmapUpdate.mastery">
          <template #suffix>
            <span class="stat-suffix" :style="{ color: masteryColor }">%</span>
          </template>
        </el-statistic>
      </div>

      <div v-if="mindmapUpdate.should_generate_method && !mindmapUpdate.method_id" class="method-tip">
        <el-alert
          title="该分类已积累足够题目，可以生成方法论总结"
          type="success"
          :closable="false"
          show-icon
        />
      </div>

      <div v-if="mindmapUpdate.method_id" class="method-tip">
        <el-alert
          title="方法论已自动生成"
          type="success"
          :closable="false"
          show-icon
        />
      </div>

      <div class="action-buttons">
        <el-button type="primary" link @click="handleViewMindMap">
          <iconify-icon icon="mdi:sitemap-outline" width="16" />
          查看思维导图
        </el-button>
        <el-button v-if="mindmapUpdate.method_id" type="success" link @click="handleViewMethod">
          <iconify-icon icon="mdi:lightbulb-on-outline" width="16" />
          查看方法论
        </el-button>
        <el-button type="default" link @click="handleCorrect">
          <iconify-icon icon="mdi:pencil-outline" width="16" />
          修正分类
        </el-button>
      </div>
    </div>

    <div v-else class="action-buttons">
      <el-button type="default" link @click="handleCorrect">
        <iconify-icon icon="mdi:pencil-outline" width="16" />
        修正分类
      </el-button>
    </div>
  </div>

  <el-dialog v-model="showCorrection" title="修正题目分类" width="480px">
    <el-form label-width="100px">
      <el-form-item label="一级模块">
        <el-select v-model="correctionModule" placeholder="请选择一级模块" style="width: 100%">
          <el-option
            v-for="mod in primaryModules"
            :key="mod"
            :label="mod"
            :value="mod"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="二级分类">
        <el-select
          v-model="correctionSubModule"
          placeholder="请选择二级分类"
          style="width: 100%"
          :disabled="!correctionModule"
        >
          <el-option
            v-for="sub in currentSecondaryModules"
            :key="sub"
            :label="sub"
            :value="sub"
          />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="showCorrection = false">取消</el-button>
      <el-button type="primary" :loading="correcting" @click="confirmCorrection">
        确认修正
      </el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.classification-container {
  margin-top: 10px;
  padding: 12px 14px;
  background: linear-gradient(135deg, var(--primary-bg) 0%, var(--bg-surface) 100%);
  border-radius: var(--radius-hand-drawn-soft);
  border: 2px solid var(--primary-lighter);
  border-left: 4px solid var(--primary-color);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-fast);
}

.classification-container:hover {
  box-shadow: var(--shadow-md);
}

.classification-tag-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.tag-icon {
  color: var(--primary-color);
  font-size: 16px;
}

.tag-label {
  font-size: 13px;
  color: var(--text-regular);
  font-weight: 500;
  font-family: var(--font-heading);
}

.confidence-tag {
  margin-left: 4px;
}

.mindmap-update-info {
  margin-top: 10px;
}

.divider-text {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
  font-family: var(--font-heading);
}

.update-stats {
  display: flex;
  gap: 28px;
  margin: 10px 0;
}

.stat-suffix {
  font-size: 12px;
}

.method-tip {
  margin: 10px 0;
}

.action-buttons {
  display: flex;
  gap: 14px;
  margin-top: 10px;
}

.action-buttons .el-button {
  font-weight: 500;
  transition: all var(--transition-hover-lift);
}

.action-buttons .el-button:hover {
  transform: translateY(-1px);
}

:deep(.el-divider__text) {
  font-weight: 500;
}
</style>
