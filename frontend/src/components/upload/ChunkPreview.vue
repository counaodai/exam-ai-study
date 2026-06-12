<script setup lang="ts">
import { computed } from 'vue'
import type { DocumentChunk } from '@/types/document'

const props = defineProps<{
  chunks: DocumentChunk[]
  loading: boolean
}>()

const chunkTypeMap: Record<string, { label: string; type: string }> = {
  question: { label: '题目', type: 'danger' },
  knowledge: { label: '知识点', type: 'primary' },
  method: { label: '方法', type: 'success' },
}

const stats = computed(() => {
  const total = props.chunks.length
  const questions = props.chunks.filter((c) => c.chunk_type === 'question').length
  const knowledge = props.chunks.filter((c) => c.chunk_type === 'knowledge').length
  const methods = props.chunks.filter((c) => c.chunk_type === 'method').length
  return { total, questions, knowledge, methods }
})
</script>

<template>
  <div class="chunk-preview">
    <el-skeleton v-if="loading" :rows="5" animated />

    <template v-else-if="chunks.length > 0">
      <div class="chunk-stats">
        <div class="stat-pill stat-total">
          <span class="stat-num">{{ stats.total }}</span>
          <span class="stat-label">个分块</span>
        </div>
        <div v-if="stats.questions" class="stat-pill stat-question">
          <span class="stat-num">{{ stats.questions }}</span>
          <span class="stat-label">题目</span>
        </div>
        <div v-if="stats.knowledge" class="stat-pill stat-knowledge">
          <span class="stat-num">{{ stats.knowledge }}</span>
          <span class="stat-label">知识点</span>
        </div>
        <div v-if="stats.methods" class="stat-pill stat-method">
          <span class="stat-num">{{ stats.methods }}</span>
          <span class="stat-label">方法</span>
        </div>
      </div>

      <el-scrollbar max-height="500px">
        <div v-for="(chunk, index) in chunks" :key="chunk.id" class="chunk-item">
          <div class="chunk-header">
            <span class="chunk-index">#{{ index + 1 }}</span>
            <el-tag
              :type="(chunkTypeMap[chunk.chunk_type]?.type as any) || 'info'"
              size="small"
            >
              {{ chunkTypeMap[chunk.chunk_type]?.label || chunk.chunk_type }}
            </el-tag>
            <el-tag
              v-if="chunk.metadata.question_number"
              size="small"
              type="warning"
            >
              第{{ chunk.metadata.question_number }}题
            </el-tag>
            <el-tag v-if="chunk.metadata.chapter" size="small" type="info">
              {{ chunk.metadata.chapter }}
            </el-tag>
            <span class="chunk-length">{{ chunk.content.length }} 字</span>
          </div>
          <div class="chunk-content">
            {{ chunk.content }}
          </div>
        </div>
      </el-scrollbar>
    </template>

    <el-empty v-else description="还是空的呢，先去添加一些吧" />
  </div>
</template>

<style scoped>
.chunk-stats {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stat-pill {
  display: flex;
  align-items: baseline;
  gap: 6px;
  padding: 8px 16px;
  border: 2px solid var(--border-light);
  border-radius: var(--radius-hand-drawn-soft);
  background: var(--bg-surface);
  transition: all var(--transition-hover-lift);
  animation: fadeInUp var(--transition-fade) forwards;
}

.stat-pill:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.stat-num {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 700;
  line-height: 1;
}

.stat-label {
  font-family: var(--font-heading);
  font-size: 13px;
  color: var(--text-secondary);
}

.stat-total {
  background: linear-gradient(135deg, var(--primary-bg) 0%, var(--bg-surface) 100%);
  border-color: var(--primary-lighter);
}
.stat-total .stat-num { color: var(--primary-color); }

.stat-question {
  border-color: rgba(192, 105, 74, 0.3);
}
.stat-question .stat-num { color: var(--accent-color); }

.stat-knowledge {
  border-color: var(--primary-lighter);
}
.stat-knowledge .stat-num { color: var(--primary-color); }

.stat-method {
  border-color: rgba(123, 160, 122, 0.4);
}
.stat-method .stat-num { color: var(--success-color); }

.chunk-item {
  border: 2px solid var(--border-light);
  border-radius: var(--radius-hand-drawn-soft);
  margin-bottom: 14px;
  overflow: hidden;
  transition: all var(--transition-hover-lift);
  box-shadow: var(--shadow-sm);
  background: var(--bg-surface);
  animation: fadeInUp var(--transition-fade) forwards;
}

.chunk-item:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
  border-color: var(--primary-lighter);
}

.chunk-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: linear-gradient(135deg, var(--primary-bg) 0%, var(--bg-surface) 100%);
  border-bottom: 2px solid var(--border-light);
}

.chunk-index {
  font-family: var(--font-display);
  font-weight: 700;
  color: var(--primary-color);
  min-width: 32px;
  font-size: 14px;
}

.chunk-length {
  margin-left: auto;
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
  font-family: var(--font-heading);
}

.chunk-content {
  padding: 14px;
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 200px;
  overflow-y: auto;
}
</style>
