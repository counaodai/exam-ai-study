<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import type { MindMap } from '@/types/mindmap'
import { useMindMapStore } from '@/stores/mindmap'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

const router = useRouter()
const mindMapStore = useMindMapStore()

const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const createForm = ref({ title: '', root_module: '' })
const editForm = ref({ mapId: '', title: '' })
const searchKeyword = ref('')

onMounted(() => {
  mindMapStore.fetchMindMaps()
})

function navigateToDetail(id: string) {
  router.push(`/mindmap/${id}`)
}

function openCreateDialog() {
  createForm.value = { title: '', root_module: '' }
  showCreateDialog.value = true
}

async function handleCreate() {
  if (!createForm.value.title.trim()) {
    ElMessage.warning('请输入思维导图标题')
    return
  }
  try {
    await mindMapStore.addMindMap(createForm.value.title.trim(), createForm.value.root_module.trim())
    ElMessage.success('创建成功')
    showCreateDialog.value = false
  } catch {
    ElMessage.error('创建失败')
  }
}

function openEditDialog(map: MindMap) {
  editForm.value = { mapId: map.id, title: map.title }
  showEditDialog.value = true
}

async function handleEdit() {
  if (!editForm.value.title.trim()) {
    ElMessage.warning('请输入思维导图标题')
    return
  }
  try {
    await mindMapStore.updateMindMapTitle(editForm.value.mapId, editForm.value.title.trim())
    ElMessage.success('更新成功')
    showEditDialog.value = false
  } catch {
    ElMessage.error('更新失败')
  }
}

async function handleDelete(map: MindMap) {
  try {
    await ElMessageBox.confirm(`确定要删除思维导图「${map.title}」吗？此操作不可恢复。`, '删除确认', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await mindMapStore.removeMindMap(map.id)
    ElMessage.success('删除成功')
  } catch {
    // 用户取消或请求失败
  }
}

// 过滤后的思维导图列表
const filteredMindMaps = computed(() => {
  if (!searchKeyword.value.trim()) {
    return mindMapStore.mindMaps
  }
  const kw = searchKeyword.value.toLowerCase()
  return mindMapStore.mindMaps.filter((m) => m.title.toLowerCase().includes(kw))
})
</script>

<template>
  <div class="mindmap-page">
    <div class="page-header">
      <div class="header-left">
        <iconify-icon icon="mdi:sitemap-outline" width="28" class="header-icon" />
        <h1>思维导图</h1>
      </div>
      <div class="header-actions">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索思维导图..."
          :prefix-icon="Search"
          clearable
          style="width: 240px"
        />
        <el-button type="primary" @click="openCreateDialog">
          <iconify-icon icon="mdi:plus" width="16" style="margin-right: 4px" />
          新建思维导图
        </el-button>
      </div>
    </div>

    <!-- 创建对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建思维导图" width="480px" destroy-on-close>
      <el-form label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="createForm.title" placeholder="例如：2024年行测真题" maxlength="100" />
        </el-form-item>
        <el-form-item label="所属模块">
          <el-input v-model="createForm.root_module" placeholder="例如：行政职业能力测验（可为空）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>

    <!-- 编辑对话框 -->
    <el-dialog v-model="showEditDialog" title="编辑思维导图" width="480px" destroy-on-close>
      <el-form label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="editForm.title" placeholder="请输入新标题" maxlength="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 思维导图列表 -->
    <el-row :gutter="20">
      <el-col v-for="map in filteredMindMaps" :key="map.id" :span="8">
        <el-card shadow="hover" class="map-card" @click="navigateToDetail(map.id)">
          <div class="card-header">
            <div class="map-title">{{ map.title }}</div>
            <div class="card-actions" @click.stop>
              <el-button size="small" circle text @click="openEditDialog(map)">
                <iconify-icon icon="mdi:pencil-outline" width="14" />
              </el-button>
              <el-button size="small" circle text type="danger" @click="handleDelete(map)">
                <iconify-icon icon="mdi:trash-can-outline" width="14" />
              </el-button>
            </div>
          </div>
          <div class="map-info">
            <span>
              <iconify-icon icon="mdi:dots-grid" width="14" />
              节点数：{{ map.nodes.length }}
            </span>
            <span>
              <iconify-icon icon="mdi:clock-outline" width="14" />
              更新：{{ new Date(map.updated_at).toLocaleDateString() }}
            </span>
          </div>
        </el-card>
      </el-col>
      <el-col v-if="filteredMindMaps.length === 0" :span="24">
        <el-empty
          :description="mindMapStore.mindMaps.length === 0 ? '还没有思维导图哦，先去导入一些文档吧' : '没找到匹配的，换个关键词试试'"
        />
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.mindmap-page {
  animation: fadeIn var(--transition-fade);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-left .header-icon {
  color: var(--primary-color, #5B8C5A);
}

.header-left h1 {
  margin: 0;
  font-family: var(--font-display);
  font-size: 26px;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.map-card {
  cursor: pointer;
  margin-bottom: 20px;
  transition: all var(--transition-hover-lift);
  overflow: hidden;
  position: relative;
}

.map-card::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 80px;
  height: 80px;
  background: radial-gradient(circle at top right, rgba(91, 140, 90, 0.08) 0%, transparent 70%);
  border-radius: 50%;
  transition: all var(--transition-normal);
}

.map-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-lg) !important;
}

.map-card:hover::after {
  transform: scale(1.5);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-right: 20px;
}

.map-title {
  font-size: 18px;
  font-weight: 600;
  font-family: var(--font-heading);
  margin-bottom: 14px;
  color: var(--text-primary);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity var(--transition-normal);
  position: relative;
  z-index: 1;
}

.map-card:hover .card-actions {
  opacity: 1;
}

.map-info {
  display: flex;
  justify-content: space-between;
  color: var(--text-muted);
  font-size: 13px;
  font-family: var(--font-body);
  padding-top: 12px;
  border-top: 1px solid var(--border-light);
}

.map-info span {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
