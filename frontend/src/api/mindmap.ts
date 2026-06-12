import request from './request'
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

export function getMindMapList() {
  return request.get<any, MindMap[]>('/mindmaps')
}

export function getMindMapDetail(id: string) {
  return request.get<any, MindMap>(`/mindmaps/${id}`)
}

export function createMindMap(data: { title: string; root_module: string }) {
  return request.post<any, MindMap>('/mindmaps', data)
}

export function updateMindMap(id: string, data: { title: string }) {
  return request.put<any, MindMap>(`/mindmaps/${id}`, data)
}

export function deleteMindMap(id: string) {
  return request.delete<any, { message: string }>(`/mindmaps/${id}`)
}


export function addNode(mapId: string, data: CreateNodeRequest) {
  return request.post<any, { node: MindMapNode; edge: MindMapEdge | null }>(`/mindmaps/${mapId}/nodes`, data)
}

export function updateNode(mapId: string, nodeId: string, data: UpdateNodeRequest) {
  return request.put<any, { message: string }>(`/mindmaps/${mapId}/nodes/${nodeId}`, data)
}

export function deleteNode(mapId: string, nodeId: string) {
  return request.delete<any, { message: string; deleted_count: number }>(`/mindmaps/${mapId}/nodes/${nodeId}`)
}

export function getNodeQuestions(mapId: string, nodeId: string, page = 1, pageSize = 10) {
  return request.get<any, NodeQuestionsResponse>(`/mindmaps/${mapId}/nodes/${nodeId}/questions`, {
    params: { page, page_size: pageSize },
  })
}

// ===== 边（连线）API =====

export function addEdge(mapId: string, data: CreateEdgeRequest) {
  return request.post<any, MindMapEdge>(`/mindmaps/${mapId}/edges`, data)
}

export function updateEdge(mapId: string, edgeId: string, data: UpdateEdgeRequest) {
  return request.patch<any, MindMapEdge>(`/mindmaps/${mapId}/edges/${edgeId}`, data)
}

export function deleteEdge(mapId: string, edgeId: string) {
  return request.delete<any, { message: string }>(`/mindmaps/${mapId}/edges/${edgeId}`)
}
