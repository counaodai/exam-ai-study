<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useMindMapStore } from '@/stores/mindmap'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Search } from '@element-plus/icons-vue'

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

function openEditDialog(map: any) {
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

async function handleDelete(map: any) {
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
const filteredMindMaps = () => {
  if (!searchKeyword.value.trim()) {
    return mindMapStore.mindMaps
  }
  const kw = searchKeyword.value.toLowerCase()
  return mindMapStore.mindMaps.filter((m) => m.title.toLowerCase().includes(kw))
}
</script>

<template>
  <div class="mindmap-page">
    <div class="page-header">
      <div class="header-left">
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
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">新建思维导图</el-button>
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
      <el-col v-for="map in filteredMindMaps()" :key="map.id" :span="8">
        <el-card shadow="hover" class="map-card" @click="navigateToDetail(map.id)">
          <div class="card-header">
            <div class="map-title">{{ map.title }}</div>
            <div class="card-actions" @click.stop>
              <el-button size="small" :icon="Edit" circle text @click="openEditDialog(map)" />
              <el-button size="small" :icon="Delete" circle text type="danger" @click="handleDelete(map)" />
            </div>
          </div>
          <div class="map-info">
            <span>节点数：{{ map.nodes.length }}</span>
            <span>更新：{{ new Date(map.updated_at).toLocaleDateString() }}</span>
          </div>
        </el-card>
      </el-col>
      <el-col v-if="filteredMindMaps().length === 0" :span="24">
        <el-empty
          :description="mindMapStore.mindMaps.length === 0 ? '暂无思维导图，请先导入文档' : '没有找到匹配的思维导图'"
        />
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.mindmap-page {
  animation: fadeIn 0.4s ease-out;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left h1 {
  margin: 0;
  font-family: var(--font-heading);
  font-size: 24px;
  position: relative;
  padding-left: 14px;
}

.header-left h1::before {
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.map-card {
  cursor: pointer;
  margin-bottom: 20px;
  transition: all var(--transition-normal);
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
  background: radial-gradient(circle at top right, rgba(13, 148, 136, 0.06) 0%, transparent 70%);
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
  padding-top: 12px;
  border-top: 1px solid var(--border-light);
}

.map-info span {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
