<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useMethodStore } from '@/stores/method'
import { Document, View, Loading } from '@element-plus/icons-vue'
import type { MethodSummary } from '@/types/method'

const router = useRouter()
const methodStore = useMethodStore()
const filterModule = ref('')

const primaryModules = ['言语理解与表达', '数量关系', '判断推理', '资料分析', '常识判断']

const filteredMethods = computed(() => {
  if (!filterModule.value) return methodStore.methods
  return methodStore.methods.filter((m) =>
    m.method_name.includes(filterModule.value),
  )
})

onMounted(() => {
  methodStore.fetchMethods()
})

function handleViewDetail(method: MethodSummary) {
  router.push(`/methods/${method.id}`)
}

function handleFilter(module: string) {
  filterModule.value = filterModule.value === module ? '' : module
}
</script>

<template>
  <div class="method-list-page">
    <div class="page-header">
      <h1>方法论总结</h1>
      <p>AI 自动分析题目生成的解题方法论</p>
    </div>

    <div class="filter-bar">
      <el-button
        v-for="mod in primaryModules"
        :key="mod"
        :type="filterModule === mod ? 'primary' : 'default'"
        @click="handleFilter(mod)"
      >
        {{ mod }}
      </el-button>
      <el-button
        v-if="filterModule"
        type="info"
        @click="filterModule = ''"
      >
        清除筛选
      </el-button>
    </div>

    <div v-if="methodStore.loading" class="loading-state">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="filteredMethods.length === 0" class="empty-state">
      <el-empty description="暂无方法论">
        <template #image>
          <div class="empty-icon">📚</div>
        </template>
        <p class="empty-tip">当某个分类积累足够题目后，系统会自动生成方法论</p>
      </el-empty>
    </div>

    <div v-else class="method-grid">
      <el-card
        v-for="method in filteredMethods"
        :key="method.id"
        class="method-card"
        shadow="hover"
        @click="handleViewDetail(method)"
      >
        <div class="card-header">
          <h3 class="method-name">{{ method.method_name }}</h3>
          <el-tag v-if="method.is_auto_generated" type="success" size="small">
            AI 生成
          </el-tag>
          <el-tag v-else type="warning" size="small">
            手动编辑
          </el-tag>
        </div>

        <p class="method-summary">{{ method.summary }}</p>

        <div class="card-stats">
          <span class="stat-item">
            <el-icon><Document /></el-icon>
            {{ method.question_count }} 道题目
          </span>
          <span class="stat-item">
            <el-icon><View /></el-icon>
            {{ method.steps.length }} 个步骤
          </span>
        </div>

        <div class="card-footer">
          <el-button type="primary" link>
            查看详情 →
          </el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.method-list-page {
  padding: 0 4px;
  animation: fadeIn 0.4s ease-out;
}

.page-header {
  margin-bottom: 28px;
}

.page-header h1 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-family: var(--font-heading);
  color: var(--text-primary);
  position: relative;
  padding-left: 14px;
}

.page-header h1::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 22px;
  background: var(--primary-gradient);
  border-radius: 2px;
}

.page-header p {
  margin: 0;
  color: var(--text-muted);
  font-size: 14px;
  padding-left: 14px;
}

.filter-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 28px;
  flex-wrap: wrap;
}

.loading-state {
  padding: 20px;
}

.empty-state {
  padding: 60px 0;
}

.empty-icon {
  font-size: 64px;
  opacity: 0.7;
}

.empty-tip {
  color: var(--text-muted);
  font-size: 14px;
  margin-top: 8px;
}

.method-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.method-card {
  cursor: pointer;
  transition: all var(--transition-normal);
  overflow: hidden;
  position: relative;
}

.method-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--primary-gradient);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform var(--transition-normal);
}

.method-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg) !important;
}

.method-card:hover::before {
  transform: scaleX(1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
}

.method-name {
  margin: 0;
  font-size: 17px;
  font-family: var(--font-heading);
  color: var(--text-primary);
  flex: 1;
  line-height: 1.4;
}

.method-summary {
  font-size: 14px;
  color: var(--text-regular);
  line-height: 1.7;
  margin: 0 0 16px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 14px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 500;
}

.card-footer {
  border-top: 1px solid var(--border-light);
  padding-top: 14px;
}

.card-footer .el-button {
  font-weight: 600;
  color: var(--primary-color);
  padding: 0;
}

.card-footer .el-button:hover {
  color: var(--primary-light);
}

@media (max-width: 768px) {
  .method-grid {
    grid-template-columns: 1fr;
  }
}
</style>
