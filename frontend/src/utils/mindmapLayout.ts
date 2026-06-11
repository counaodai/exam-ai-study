/**
 * 思维导图自动布局工具
 * 基于 dagre 图布局算法，支持横向/纵向布局。
 * 仅服务于思维导图模块，不影响其他功能。
 */
import dagre from 'dagre'

export type LayoutDirection = 'LR' | 'TB' | 'RL' | 'BT'

interface FlowNodeLike {
  id: string
  position: { x: number; y: number }
  // 可选的尺寸（VueFlow 计算后会填充）
  width?: number
  height?: number
}

interface FlowEdgeLike {
  source: string
  target: string
}

export interface LayoutOptions {
  direction?: LayoutDirection
  nodeWidth?: number
  nodeHeight?: number
  rankSep?: number
  nodeSep?: number
}

/**
 * 计算自动布局后的节点位置
 * @returns 节点 ID -> { x, y } 的映射
 */
export function calcAutoLayout(
  nodes: FlowNodeLike[],
  edges: FlowEdgeLike[],
  options: LayoutOptions = {},
): Map<string, { x: number; y: number }> {
  const {
    direction = 'LR',
    nodeWidth = 200,
    nodeHeight = 110,
    rankSep = 80,
    nodeSep = 40,
  } = options

  const g = new dagre.graphlib.Graph()
  g.setDefaultEdgeLabel(() => ({}))
  g.setGraph({
    rankdir: direction,
    ranksep: rankSep,
    nodesep: nodeSep,
    marginx: 20,
    marginy: 20,
  })

  for (const n of nodes) {
    g.setNode(n.id, {
      width: n.width || nodeWidth,
      height: n.height || nodeHeight,
    })
  }
  for (const e of edges) {
    if (g.hasNode(e.source) && g.hasNode(e.target)) {
      g.setEdge(e.source, e.target)
    }
  }

  dagre.layout(g)

  const result = new Map<string, { x: number; y: number }>()
  for (const n of nodes) {
    const node = g.node(n.id)
    if (node) {
      // dagre 给的是中心点坐标，VueFlow 用的是左上角坐标
      result.set(n.id, {
        x: node.x - (n.width || nodeWidth) / 2,
        y: node.y - (n.height || nodeHeight) / 2,
      })
    }
  }
  return result
}
