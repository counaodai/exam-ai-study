import { defineStore } from 'pinia'
import { ref } from 'vue'
import type {
  MindMap,
  MindMapNode,
  MindMapEdge,
  CreateNodeRequest,
  UpdateNodeRequest,
  CreateEdgeRequest,
  UpdateEdgeRequest,
  NodeQuestionsResponse,
} from '@/types/mindmap'
import * as mindmapApi from '@/api/mindmap'

export const useMindMapStore = defineStore('mindmap', () => {
  const mindMaps = ref<MindMap[]>([])
  const currentMindMap = ref<MindMap | null>(null)
  const loading = ref(false)
  const nodeQuestions = ref<NodeQuestionsResponse | null>(null)
  const nodeQuestionsLoading = ref(false)

  async function fetchMindMaps() {
    mindMaps.value = await mindmapApi.getMindMapList()
  }

  async function fetchMindMapDetail(id: string) {
    loading.value = true
    try {
      currentMindMap.value = await mindmapApi.getMindMapDetail(id)
    } finally {
      loading.value = false
    }
  }

  async function generateMindMap(docId: string) {
    loading.value = true
    try {
      const map = await mindmapApi.generateMindMap(docId)
      mindMaps.value.push(map)
      return map
    } finally {
      loading.value = false
    }
  }

  async function refreshCurrentMindMap() {
    if (currentMindMap.value) {
      await fetchMindMapDetail(currentMindMap.value.id)
    }
  }

  async function addMindMap(title: string, rootModule: string) {
    loading.value = true
    try {
      const map = await mindmapApi.createMindMap({ title, root_module: rootModule })
      mindMaps.value.push(map)
      return map
    } finally {
      loading.value = false
    }
  }

  async function updateMindMapTitle(mapId: string, title: string) {
    const updated = await mindmapApi.updateMindMap(mapId, { title })
    const idx = mindMaps.value.findIndex((m) => m.id === mapId)
    if (idx !== -1) {
      mindMaps.value[idx].title = title
    }
    if (currentMindMap.value && currentMindMap.value.id === mapId) {
      currentMindMap.value.title = title
    }
  }

  async function removeMindMap(mapId: string) {
    await mindmapApi.deleteMindMap(mapId)
    mindMaps.value = mindMaps.value.filter((m) => m.id !== mapId)
    if (currentMindMap.value && currentMindMap.value.id === mapId) {
      currentMindMap.value = null
    }
  }

  async function addNode(mapId: string, data: CreateNodeRequest) {
    const result = await mindmapApi.addNode(mapId, data)
    const { node: newNode, edge: newEdge } = result
    if (currentMindMap.value && currentMindMap.value.id === mapId) {
      currentMindMap.value.nodes.push(newNode)
      if (newEdge) {
        currentMindMap.value.edges.push(newEdge)
      }
    }
    return newNode
  }

  async function deleteNode(mapId: string, nodeId: string) {
    const result = await mindmapApi.deleteNode(mapId, nodeId)
    if (currentMindMap.value && currentMindMap.value.id === mapId) {
      const nodeIdsToDelete = new Set<string>()
      const collectDescendants = (nid: string) => {
        nodeIdsToDelete.add(nid)
        currentMindMap.value!.edges
          .filter((e) => e.source === nid)
          .forEach((e) => collectDescendants(e.target))
      }
      collectDescendants(nodeId)

      currentMindMap.value.nodes = currentMindMap.value.nodes.filter(
        (n) => !nodeIdsToDelete.has(n.id)
      )
      currentMindMap.value.edges = currentMindMap.value.edges.filter(
        (e) => !nodeIdsToDelete.has(e.source) && !nodeIdsToDelete.has(e.target)
      )
    }
    return result
  }

  async function updateNodePosition(mapId: string, nodeId: string, x: number, y: number) {
    await mindmapApi.updateNode(mapId, nodeId, { position_x: x, position_y: y })
    if (currentMindMap.value && currentMindMap.value.id === mapId) {
      const node = currentMindMap.value.nodes.find((n) => n.id === nodeId)
      if (node) {
        node.position = { x, y }
      }
    }
  }

  async function updateNodeLabel(mapId: string, nodeId: string, label: string) {
    await mindmapApi.updateNode(mapId, nodeId, { label })
    if (currentMindMap.value && currentMindMap.value.id === mapId) {
      const node = currentMindMap.value.nodes.find((n) => n.id === nodeId)
      if (node) {
        node.label = label
      }
    }
  }

  async function fetchNodeQuestions(mapId: string, nodeId: string, page = 1, pageSize = 10) {
    nodeQuestionsLoading.value = true
    try {
      nodeQuestions.value = await mindmapApi.getNodeQuestions(mapId, nodeId, page, pageSize)
    } finally {
      nodeQuestionsLoading.value = false
    }
  }

  // ===== 边（连线）操作 =====

  async function addEdge(mapId: string, data: CreateEdgeRequest): Promise<MindMapEdge> {
    const edge = await mindmapApi.addEdge(mapId, data)
    if (currentMindMap.value && currentMindMap.value.id === mapId) {
      currentMindMap.value.edges.push(edge)
    }
    return edge
  }

  async function updateEdge(mapId: string, edgeId: string, data: UpdateEdgeRequest): Promise<MindMapEdge> {
    const updated = await mindmapApi.updateEdge(mapId, edgeId, data)
    if (currentMindMap.value && currentMindMap.value.id === mapId) {
      const idx = currentMindMap.value.edges.findIndex((e) => e.id === edgeId)
      if (idx !== -1) {
        currentMindMap.value.edges.splice(idx, 1, updated)
      } else {
        // 派生边被持久化后，旧 derived-id 已替换为真实 id
        currentMindMap.value.edges.push(updated)
      }
    }
    return updated
  }

  async function deleteEdge(mapId: string, edgeId: string) {
    await mindmapApi.deleteEdge(mapId, edgeId)
    if (currentMindMap.value && currentMindMap.value.id === mapId) {
      currentMindMap.value.edges = currentMindMap.value.edges.filter((e) => e.id !== edgeId)
    }
  }

  return {
    mindMaps,
    currentMindMap,
    loading,
    nodeQuestions,
    nodeQuestionsLoading,
    fetchMindMaps,
    fetchMindMapDetail,
    addMindMap,
    updateMindMapTitle,
    removeMindMap,
    generateMindMap,
    refreshCurrentMindMap,
    addNode,
    deleteNode,
    updateNodePosition,
    updateNodeLabel,
    fetchNodeQuestions,
    addEdge,
    updateEdge,
    deleteEdge,
  }
})
