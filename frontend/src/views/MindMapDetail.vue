<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch, computed, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useMindMapStore } from '@/stores/mindmap'
import { VueFlow, useVueFlow, MarkerType } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import MindMapNode from '@/components/mindmap/MindMapNode.vue'
import NodeContextMenu from '@/components/mindmap/NodeContextMenu.vue'
import NodeDetailDrawer from '@/components/mindmap/NodeDetailDrawer.vue'
import EdgeContextMenu from '@/components/mindmap/EdgeContextMenu.vue'
import ImportEntryDialog from '@/components/mindmap/ImportEntryDialog.vue'
import { ArrowLeft, ArrowDown, FullScreen, Plus, Refresh, Search, MagicStick, Upload } from '@element-plus/icons-vue'
import type { MindMapNode as MindMapNodeType, NodeType, EdgeType } from '@/types/mindmap'
import { calcAutoLayout, type LayoutDirection } from '@/utils/mindmapLayout'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'

const route = useRoute()
const router = useRouter()
const mindMapStore = useMindMapStore()
const { fitView, setCenter, getNode } = useVueFlow()

const flowNodes = ref<any[]>([])
const flowEdges = ref<any[]>([])

const contextMenuVisible = ref(false)
const contextMenuPosition = ref({ x: 0, y: 0 })
const contextMenuNodeType = ref<NodeType>('topic')
const contextMenuNodeId = ref('')

const drawerVisible = ref(false)
const selectedNode = ref<MindMapNodeType | null>(null)

const addDialogVisible = ref(false)
const newNodeLabel = ref('')
const newNodeType = ref<NodeType>('topic')

// 边右键菜单
const edgeMenuVisible = ref(false)
const edgeMenuPosition = ref({ x: 0, y: 0 })
const edgeMenuEdgeId = ref('')
const edgeMenuType = ref<EdgeType>('default')
const edgeMenuColor = ref('#5B8C5A')
const edgeMenuHasArrow = ref(true)
const edgeMenuAnimated = ref(false)

// 布局方向
const layoutDirection = ref<LayoutDirection>('LR')

// 搜索
const searchKeyword = ref('')
const highlightNodeIds = ref<Set<string>>(new Set())

// 导入题目
const importDialogVisible = ref(false)
const highlightTargetNodeId = ref<string | null>(null)

const mapId = computed(() => route.params.moduleId as string)

let dragSaveTimer: ReturnType<typeof setTimeout> | null = null

onMounted(() => {
  if (mapId.value) {
    mindMapStore.fetchMindMapDetail(mapId.value)
  }
  window.addEventListener('keydown', handleGlobalKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
})

watch(
  () => mindMapStore.currentMindMap,
  (map) => {
    if (!map) {
      flowNodes.value = []
      flowEdges.value = []
      return
    }
    flowNodes.value = map.nodes.map((node) => ({
      id: node.id,
      position: { x: node.position.x, y: node.position.y },
      data: {
        label: node.label,
        type: node.type,
        question_count: node.question_count,
        mastery: node.mastery,
        method_id: node.metadata?.method_summary || null,
        highlight: highlightNodeIds.value.has(node.id) || highlightTargetNodeId.value === node.id,
      },
      type: 'mindmap',
    }))
    flowEdges.value = map.edges.map((edge) => buildFlowEdge(edge))
  },
  { immediate: true, deep: true },
)

// 把后端 edge 转成 vue-flow 需要的格式
function buildFlowEdge(edge: any) {
  const hasArrow = edge.has_arrow !== false
  const color = edge.color || '#5B8C5A'
  const strokeWidth = edge.stroke_width || 2
  return {
    id: edge.id,
    source: edge.source,
    target: edge.target,
    type: edge.edge_type || 'default',
    animated: !!edge.animated,
    updatable: true,
    label: edge.label || undefined,
    style: { stroke: color, strokeWidth },
    markerEnd: hasArrow
      ? { type: MarkerType.ArrowClosed, color, width: 18, height: 18 }
      : undefined,
    data: {
      edge_type: edge.edge_type || 'default',
      color,
      stroke_width: strokeWidth,
      has_arrow: hasArrow,
      animated: !!edge.animated,
      is_derived: !!edge.is_derived,
    },
  }
}

// ===== 节点交互 =====

function handleNodeClick(event: { node: any }) {
  const node = event.node
  const originalNode = mindMapStore.currentMindMap?.nodes.find((n) => n.id === node.id)
  if (originalNode) {
    selectedNode.value = originalNode
    drawerVisible.value = true
  }
}

function handleNodeContextMenu(payload: { nodeId: string; event: MouseEvent }) {
  const node = mindMapStore.currentMindMap?.nodes.find((n) => n.id === payload.nodeId)
  if (!node) return
  contextMenuNodeId.value = payload.nodeId
  contextMenuNodeType.value = node.type
  contextMenuPosition.value = { x: payload.event.clientX, y: payload.event.clientY }
  contextMenuVisible.value = true
}

async function handleContextMenuAction(action: string) {
  contextMenuVisible.value = false
  const nodeId = contextMenuNodeId.value
  const node = mindMapStore.currentMindMap?.nodes.find((n) => n.id === nodeId)
  if (!node) return

  switch (action) {
    case 'add':
      selectedNode.value = node
      newNodeLabel.value = ''
      newNodeType.value = 'topic'
      addDialogVisible.value = true
      break
    case 'edit':
      break
    case 'questions':
      selectedNode.value = node
      drawerVisible.value = true
      break
    case 'delete':
      await handleDeleteNode(nodeId)
      break
  }
}

async function handleDeleteNode(nodeId: string) {
  const node = mindMapStore.currentMindMap?.nodes.find((n) => n.id === nodeId)
  if (!node) return

  const childCount = mindMapStore.currentMindMap?.edges.filter((e) => e.source === nodeId).length ?? 0
  const message = childCount > 0
    ? `确定删除节点"${node.label}"吗？将同时删除 ${childCount} 个子节点。`
    : `确定删除节点"${node.label}"吗？`

  try {
    await ElMessageBox.confirm(message, '删除确认', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    const result = await mindMapStore.deleteNode(mapId.value, nodeId)
    ElMessage.success(`已删除 ${result.deleted_count} 个节点`)
  } catch {
    // 用户取消
  }
}

async function handleAddNode() {
  if (!newNodeLabel.value.trim()) {
    ElMessage.warning('请输入节点名称')
    return
  }
  try {
    await mindMapStore.addNode(mapId.value, {
      label: newNodeLabel.value.trim(),
      type: newNodeType.value,
      parent_id: contextMenuNodeId.value,
    })
    addDialogVisible.value = false
    ElMessage.success('节点添加成功')
  } catch {
    ElMessage.error('添加失败')
  }
}

async function handleLabelChange(payload: { nodeId: string; label: string }) {
  try {
    await mindMapStore.updateNodeLabel(mapId.value, payload.nodeId, payload.label)
    ElMessage.success('节点名称已更新')
  } catch {
    ElMessage.error('更新失败')
  }
}

function handleNodeDragStop(event: { nodes: any[] }) {
  if (dragSaveTimer) clearTimeout(dragSaveTimer)
  dragSaveTimer = setTimeout(() => {
    for (const node of event.nodes) {
      mindMapStore.updateNodePosition(mapId.value, node.id, node.position.x, node.position.y)
    }
  }, 500)
}

// ===== 边交互：新建/重连/右键菜单 =====

async function handleConnect(params: { source: string; target: string }) {
  if (!params.source || !params.target || params.source === params.target) return
  // 避免重复
  const exists = mindMapStore.currentMindMap?.edges.some(
    (e) => e.source === params.source && e.target === params.target,
  )
  if (exists) {
    ElMessage.warning('该连线已存在')
    return
  }
  try {
    await mindMapStore.addEdge(mapId.value, {
      source: params.source,
      target: params.target,
    })
    ElMessage.success('连线已添加')
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '添加连线失败')
  }
}

async function handleEdgeUpdate(payload: { edge: any; connection: { source: string; target: string } }) {
  const { edge, connection } = payload
  if (!connection.source || !connection.target) return
  try {
    await mindMapStore.updateEdge(mapId.value, edge.id, {
      source: connection.source,
      target: connection.target,
    })
    ElMessage.success('连线端点已更新')
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '更新失败')
  }
}

function handleEdgeContextMenu(payload: { event: MouseEvent | TouchEvent; edge: any }) {
  const evt = payload.event as MouseEvent
  evt.preventDefault?.()
  const e = payload.edge
  edgeMenuEdgeId.value = e.id
  edgeMenuType.value = (e.data?.edge_type as EdgeType) || 'default'
  edgeMenuColor.value = e.data?.color || '#5B8C5A'
  edgeMenuHasArrow.value = e.data?.has_arrow !== false
  edgeMenuAnimated.value = !!e.data?.animated
  edgeMenuPosition.value = { x: evt.clientX || 0, y: evt.clientY || 0 }
  edgeMenuVisible.value = true
}

async function handleEdgeMenuAction(payload: { type: string; value?: any }) {
  const edgeId = edgeMenuEdgeId.value
  const original = mindMapStore.currentMindMap?.edges.find((e) => e.id === edgeId)
  if (!original) return

  try {
    switch (payload.type) {
      case 'changeType':
        await mindMapStore.updateEdge(mapId.value, edgeId, { edge_type: payload.value })
        break
      case 'changeColor':
        await mindMapStore.updateEdge(mapId.value, edgeId, { color: payload.value })
        break
      case 'toggleArrow':
        await mindMapStore.updateEdge(mapId.value, edgeId, { has_arrow: !edgeMenuHasArrow.value })
        break
      case 'toggleAnimated':
        await mindMapStore.updateEdge(mapId.value, edgeId, { animated: !edgeMenuAnimated.value })
        break
      case 'reverse':
        await mindMapStore.updateEdge(mapId.value, edgeId, {
          source: original.target,
          target: original.source,
        })
        break
      case 'delete':
        await mindMapStore.deleteEdge(mapId.value, edgeId)
        ElMessage.success('连线已删除')
        return
    }
    ElMessage.success('已更新')
  } catch (err: any) {
    ElMessage.error(err?.response?.data?.detail || '操作失败')
  }
}

// ===== 自动布局 =====

async function applyAutoLayout(direction?: LayoutDirection) {
  if (direction) layoutDirection.value = direction
  const map = mindMapStore.currentMindMap
  if (!map) return

  const positions = calcAutoLayout(
    map.nodes.map((n) => ({ id: n.id, position: { x: n.position.x, y: n.position.y } })),
    map.edges.map((e) => ({ source: e.source, target: e.target })),
    { direction: layoutDirection.value },
  )

  // 批量更新前端 + 持久化
  const updatePromises: Promise<any>[] = []
  for (const node of map.nodes) {
    const pos = positions.get(node.id)
    if (pos) {
      node.position = { x: pos.x, y: pos.y }
      updatePromises.push(
        mindMapStore.updateNodePosition(mapId.value, node.id, pos.x, pos.y),
      )
    }
  }
  await Promise.all(updatePromises)
  await nextTick()
  fitView({ padding: 0.2 })
  ElMessage.success('已应用自动布局')
}

// ===== 搜索 =====

function handleSearch() {
  const kw = searchKeyword.value.trim().toLowerCase()
  if (!kw) {
    highlightNodeIds.value = new Set()
    // 重置高亮
    flowNodes.value = flowNodes.value.map((n) => ({ ...n, data: { ...n.data, highlight: false } }))
    return
  }
  const matched = (mindMapStore.currentMindMap?.nodes || []).filter((n) =>
    n.label.toLowerCase().includes(kw),
  )
  if (matched.length === 0) {
    ElMessage.warning('未找到匹配节点')
    return
  }
  highlightNodeIds.value = new Set(matched.map((n) => n.id))
  flowNodes.value = flowNodes.value.map((n) => ({
    ...n,
    data: { ...n.data, highlight: highlightNodeIds.value.has(n.id) },
  }))
  // 定位到第一个
  const first = matched[0]
  setCenter(first.position.x + 100, first.position.y + 50, { zoom: 1, duration: 400 })
}

// ===== 全局快捷键 =====

function handleGlobalKeydown(e: KeyboardEvent) {
  const target = e.target as HTMLElement
  const isInput = target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable

  // Ctrl+F 聚焦搜索框
  if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
    e.preventDefault()
    const input = document.querySelector('.mindmap-search input') as HTMLInputElement
    input?.focus()
    return
  }

  if (isInput) return

  // Delete 删除选中节点
  if (e.key === 'Delete' && selectedNode.value && selectedNode.value.type !== 'module') {
    handleDeleteNode(selectedNode.value.id)
  }
}

function handleFitView() {
  fitView({ padding: 0.2 })
}

function handleBack() {
  router.push('/mindmap')
}

async function handleRefresh() {
  if (mapId.value) {
    await mindMapStore.fetchMindMapDetail(mapId.value)
    ElMessage.success('思维导图已刷新')
  }
}

function handleViewMethod(nodeId: string) {
  const node = mindMapStore.currentMindMap?.nodes.find((n) => n.id === nodeId)
  if (node?.metadata?.method_summary) {
    router.push(`/methods/${node.metadata.method_summary}`)
  }
}

// ===== 导入题目 =====

function handleOpenImport() {
  importDialogVisible.value = true
}

async function handleImportCompleted(result: { importedCount: number; importedIds: string[]; updatedNodes: any[] }) {
  importDialogVisible.value = false

  if (result.importedCount > 0) {
    // 刷新思维导图数据
    await mindMapStore.refreshCurrentMindMap()

    // 定位到第一个更新的节点
    if (result.updatedNodes && result.updatedNodes.length > 0) {
      const firstNode = result.updatedNodes[0]
      highlightTargetNodeId.value = firstNode.node_id

      // 高亮目标节点
      const node = mindMapStore.currentMindMap?.nodes.find((n) => n.id === firstNode.node_id)
      if (node) {
        setCenter(node.position.x + 100, node.position.y + 50, { zoom: 1, duration: 500 })
        // 2秒后取消高亮
        setTimeout(() => {
          highlightTargetNodeId.value = null
        }, 3000)
      }
    }

    ElMessage.success(`成功导入 ${result.importedCount} 道题目，思维导图已更新`)
  }
}
</script>

<template>
  <div class="mindmap-detail">
    <div class="detail-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" @click="handleBack">返回</el-button>
        <h1>{{ mindMapStore.currentMindMap?.title || '加载中...' }}</h1>
      </div>
      <div class="header-right">
        <el-input
          v-model="searchKeyword"
          class="mindmap-search"
          placeholder="搜索节点..."
          clearable
          :prefix-icon="Search"
          style="width: 180px"
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />
        <el-dropdown @command="(d) => applyAutoLayout(d)">
          <el-button :icon="MagicStick">
            自动布局<el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="LR">横向（左→右）</el-dropdown-item>
              <el-dropdown-item command="TB">纵向（上→下）</el-dropdown-item>
              <el-dropdown-item command="RL">横向（右→左）</el-dropdown-item>
              <el-dropdown-item command="BT">纵向（下→上）</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button
          :icon="Plus"
          type="primary"
          @click="contextMenuNodeId = mindMapStore.currentMindMap?.nodes[0]?.id || ''; selectedNode = mindMapStore.currentMindMap?.nodes[0] || null; newNodeLabel = ''; newNodeType = 'topic'; addDialogVisible = true"
        >添加节点</el-button>
        <el-button :icon="Upload" type="success" @click="handleOpenImport">导入题目</el-button>
        <el-button :icon="Refresh" @click="handleRefresh">刷新</el-button>
        <el-button :icon="FullScreen" @click="handleFitView">适应画布</el-button>
        <el-tag v-if="mindMapStore.currentMindMap" type="info">
          节点：{{ mindMapStore.currentMindMap.nodes.length }} / 连线：{{ mindMapStore.currentMindMap.edges.length }}
        </el-tag>
      </div>
    </div>

    <div class="flow-container">
      <VueFlow
        v-if="mindMapStore.currentMindMap"
        :nodes="flowNodes"
        :edges="flowEdges"
        :default-viewport="{ zoom: 0.8, x: 0, y: 0 }"
        :min-zoom="0.2"
        :max-zoom="2"
        :edges-updatable="true"
        :connect-on-click="false"
        fit-view-on-init
        @node-click="handleNodeClick"
        @node-drag-stop="handleNodeDragStop"
        @connect="handleConnect"
        @edge-update="handleEdgeUpdate"
        @edge-context-menu="handleEdgeContextMenu"
      >
        <template #node-mindmap="nodeProps">
          <MindMapNode
            v-bind="nodeProps"
            @contextmenu="handleNodeContextMenu"
            @label-change="handleLabelChange"
          />
        </template>

        <Background pattern-color="#D9D0BC" :gap="16" />
        <Controls />
        <MiniMap
          :node-color="(node) => {
            const colors: Record<string, string> = {
              module: '#5B8C5A',
              topic: '#7BA07A',
              method: '#C4A35A',
              question: '#8A7E6A',
            }
            return colors[node.data?.type] || '#5B8C5A'
          }"
          :mask-color="'rgba(255, 255, 255, 0.8)'"
        />
      </VueFlow>

      <el-skeleton v-else :rows="10" animated />
    </div>

    <NodeContextMenu
      v-model:visible="contextMenuVisible"
      :position="contextMenuPosition"
      :node-type="contextMenuNodeType"
      @action="handleContextMenuAction"
    />

    <EdgeContextMenu
      v-model:visible="edgeMenuVisible"
      :position="edgeMenuPosition"
      :edge-id="edgeMenuEdgeId"
      :has-arrow="edgeMenuHasArrow"
      :animated="edgeMenuAnimated"
      :current-type="edgeMenuType"
      :current-color="edgeMenuColor"
      @action="handleEdgeMenuAction"
    />

    <NodeDetailDrawer
      v-model:visible="drawerVisible"
      :node="selectedNode"
      :map-id="mapId"
      @view-method="handleViewMethod"
    />

    <ImportEntryDialog
      v-model:visible="importDialogVisible"
      :mindmap-id="mapId"
      @imported="handleImportCompleted"
    />

    <el-dialog
      v-model="addDialogVisible"
      title="添加子节点"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form label-width="80px">
        <el-form-item label="节点名称">
          <el-input
            v-model="newNodeLabel"
            placeholder="请输入节点名称"
            maxlength="50"
            @keyup.enter="handleAddNode"
          />
        </el-form-item>
        <el-form-item label="节点类型">
          <el-select v-model="newNodeType" style="width: 100%">
            <el-option label="主题节点" value="topic" />
            <el-option label="方法论" value="method" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAddNode">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.mindmap-detail {
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  animation: fadeIn var(--transition-fade);
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 14px 18px;
  background: var(--bg-surface);
  border-radius: var(--radius-hand-drawn-soft);
  border: 2px solid var(--border-light);
  box-shadow: var(--shadow-sm);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.header-left h1 {
  margin: 0;
  font-size: 22px;
  font-family: var(--font-display);
  color: var(--text-primary);
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.flow-container {
  flex: 1;
  background: linear-gradient(180deg, var(--bg-color) 0%, var(--bg-muted) 100%);
  border-radius: var(--radius-hand-drawn);
  overflow: hidden;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-md);
  position: relative;
}

:deep(.vue-flow__node) {
  transition: box-shadow var(--transition-fast);
}

:deep(.vue-flow__edge-path) {
  stroke-opacity: 0.85;
}

:deep(.vue-flow__edge.selected .vue-flow__edge-path) {
  stroke-width: 3 !important;
  filter: drop-shadow(0 0 4px rgba(91, 140, 90, 0.4));
}

:deep(.vue-flow__edge:hover .vue-flow__edge-path) {
  cursor: pointer;
  stroke-opacity: 1;
}

:deep(.vue-flow__controls) {
  border-radius: var(--radius-hand-drawn-soft);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-light);
  overflow: hidden;
}

:deep(.vue-flow__minimap) {
  border-radius: var(--radius-hand-drawn-soft);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-light);
  overflow: hidden;
}

@media (max-width: 768px) {
  .mindmap-detail {
    height: calc(100vh - 100px);
  }
  
  .detail-header {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  
  .header-right {
    width: 100%;
    flex-wrap: wrap;
  }
}
</style>
