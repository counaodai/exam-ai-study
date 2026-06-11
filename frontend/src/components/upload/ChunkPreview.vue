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
        <el-tag type="info" size="large">总计 {{ stats.total }} 个分块</el-tag>
        <el-tag v-if="stats.questions" type="danger">题目 {{ stats.questions }}</el-tag>
        <el-tag v-if="stats.knowledge" type="primary">知识点 {{ stats.knowledge }}</el-tag>
        <el-tag v-if="stats.methods" type="success">方法 {{ stats.methods }}</el-tag>
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

    <el-empty v-else description="暂无分块数据" />
  </div>
</template>

<style scoped>
.chunk-stats {
  display: flex;
  gap: 10px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}

.chunk-item {
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  margin-bottom: 14px;
  overflow: hidden;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-sm);
}

.chunk-item:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.chunk-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: linear-gradient(90deg, var(--bg-muted) 0%, rgba(241, 245, 249, 0.5) 100%);
  border-bottom: 1px solid var(--border-light);
}

.chunk-index {
  font-weight: 700;
  color: var(--primary-color);
  min-width: 30px;
  font-size: 13px;
}

.chunk-length {
  margin-left: auto;
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
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
