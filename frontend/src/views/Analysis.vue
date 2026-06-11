<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, PieChart, LineChart, HeatmapChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  VisualMapComponent,
  CalendarComponent,
} from 'echarts/components'
import { ElMessage } from 'element-plus'
import type {
  OverviewStats,
  ModuleStats,
  SubModuleStats,
  TrendData,
  WeakPointStats,
  MethodCoverageStats,
} from '@/api/analysis'
import * as analysisApi from '@/api/analysis'

use([
  CanvasRenderer,
  BarChart,
  PieChart,
  LineChart,
  HeatmapChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  VisualMapComponent,
  CalendarComponent,
])

const loading = ref(true)
const overview = ref<OverviewStats | null>(null)
const moduleStats = ref<ModuleStats[]>([])
const subModuleStats = ref<SubModuleStats[]>([])
const trends = ref<TrendData[]>([])
const weakPoints = ref<WeakPointStats[]>([])
const methodCoverage = ref<MethodCoverageStats | null>(null)

const selectedModule = ref<string>('')

const barOption = computed(() => ({
  title: { text: '各模块题目数量', left: 'center' },
  tooltip: { trigger: 'axis' },
  xAxis: {
    data: moduleStats.value.map((m) => m.module_name),
    axisLabel: { rotate: 15 },
  },
  yAxis: { type: 'value' },
  series: [
    {
      type: 'bar',
      data: moduleStats.value.map((m) => m.question_count),
      itemStyle: {
        color: (params: any) => {
          const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
          return colors[params.dataIndex % colors.length]
        },
      },
      label: { show: true, position: 'top' },
    },
  ],
}))

const pieOption = computed(() => ({
  title: { text: '题目分布', left: 'center' },
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: { orient: 'vertical', left: 'left' },
  series: [
    {
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: false },
      emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
      labelLine: { show: false },
      data: moduleStats.value.map((m) => ({
        name: m.module_name,
        value: m.question_count,
      })),
    },
  ],
}))

const lineOption = computed(() => ({
  title: { text: '学习趋势（近30天）', left: 'center' },
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: trends.value.map((t) => t.date.slice(5)),
    axisLabel: { rotate: 45 },
  },
  yAxis: { type: 'value' },
  series: [
    {
      type: 'line',
      data: trends.value.map((t) => t.count),
      smooth: true,
      areaStyle: { opacity: 0.3 },
      itemStyle: { color: '#409EFF' },
    },
  ],
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
}))

const masteryOption = computed(() => ({
  title: { text: '各模块掌握度', left: 'center' },
  tooltip: { trigger: 'axis' },
  xAxis: {
    data: moduleStats.value.map((m) => m.module_name),
    axisLabel: { rotate: 15 },
  },
  yAxis: { type: 'value', max: 100 },
  series: [
    {
      type: 'bar',
      data: moduleStats.value.map((m) => m.avg_mastery),
      itemStyle: {
        color: (params: any) => {
          const value = params.value
          if (value >= 80) return '#67C23A'
          if (value >= 60) return '#E6A23C'
          return '#F56C6C'
        },
      },
      label: { show: true, position: 'top', formatter: '{c}%' },
    },
  ],
}))

const coverageProgress = computed(() => {
  return methodCoverage.value?.coverage_rate ?? 0
})

const coverageColor = computed(() => {
  const rate = coverageProgress.value
  if (rate >= 80) return '#67C23A'
  if (rate >= 50) return '#E6A23C'
  return '#F56C6C'
})

async function loadData() {
  loading.value = true
  try {
    const [ov, ms, tr, wp, mc] = await Promise.all([
      analysisApi.getOverviewStats(),
      analysisApi.getModuleStats(),
      analysisApi.getTrends(30),
      analysisApi.getWeakPoints(10),
      analysisApi.getMethodCoverage(),
    ])
    overview.value = ov
    moduleStats.value = ms
    trends.value = tr
    weakPoints.value = wp
    methodCoverage.value = mc
  } catch (e) {
    ElMessage.error('加载统计数据失败')
  } finally {
    loading.value = false
  }
}

async function handleModuleClick(moduleName: string) {
  selectedModule.value = moduleName
  try {
    subModuleStats.value = await analysisApi.getSubModuleStats(moduleName)
  } catch (e) {
    ElMessage.error('加载子分类数据失败')
  }
}

function getMasteryColor(mastery: number): string {
  if (mastery >= 80) return '#67C23A'
  if (mastery >= 60) return '#E6A23C'
  return '#F56C6C'
}

function getMasteryTag(mastery: number): 'success' | 'warning' | 'danger' {
  if (mastery >= 80) return 'success'
  if (mastery >= 60) return 'warning'
  return 'danger'
}

onMounted(loadData)
</script>

<template>
  <div class="analysis-page" v-loading="loading">
    <div class="page-header">
      <h1>统计分析</h1>
      <el-button type="primary" @click="loadData">刷新数据</el-button>
    </div>

    <el-row :gutter="20" class="overview-row">
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover">
          <el-statistic title="文档总数" :value="overview?.total_documents ?? 0">
            <template #suffix>
              <span class="stat-suffix">份</span>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover">
          <el-statistic title="题目总数" :value="overview?.total_questions ?? 0">
            <template #suffix>
              <span class="stat-suffix">道</span>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover">
          <el-statistic title="对话次数" :value="overview?.total_conversations ?? 0">
            <template #suffix>
              <span class="stat-suffix">次</span>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover">
          <el-statistic title="方法论数" :value="overview?.total_methods ?? 0">
            <template #suffix>
              <span class="stat-suffix">个</span>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>方法论覆盖度</span>
              <el-tag :type="coverageProgress >= 50 ? 'success' : 'warning'" size="small">
                {{ coverageProgress }}%
              </el-tag>
            </div>
          </template>
          <el-progress
            :percentage="coverageProgress"
            :color="coverageColor"
            :stroke-width="20"
            :text-inside="true"
          />
          <div class="coverage-info">
            <span>已覆盖 {{ methodCoverage?.covered_sub_modules ?? 0 }} / {{ methodCoverage?.total_sub_modules ?? 0 }} 个子分类</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="12">
        <el-card shadow="hover" class="chart-card">
          <v-chart :option="barOption" style="height: 350px" autoresize />
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card shadow="hover" class="chart-card">
          <v-chart :option="pieOption" style="height: 350px" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="12">
        <el-card shadow="hover" class="chart-card">
          <v-chart :option="lineOption" style="height: 350px" autoresize />
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card shadow="hover" class="chart-card">
          <v-chart :option="masteryOption" style="height: 350px" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="chart-row">
      <el-col :xs="24" :lg="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>薄弱环节排行</span>
              <el-tag type="danger" size="small">TOP 10</el-tag>
            </div>
          </template>
          <el-table :data="weakPoints" style="width: 100%" max-height="350">
            <el-table-column type="index" label="排名" width="60" />
            <el-table-column prop="module_name" label="一级模块" width="120" />
            <el-table-column prop="sub_module_name" label="二级分类" />
            <el-table-column prop="question_count" label="题目数" width="80" align="center" />
            <el-table-column label="掌握度" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getMasteryTag(row.avg_mastery)" size="small">
                  {{ row.avg_mastery }}%
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>子分类详情</span>
              <el-select
                v-model="selectedModule"
                placeholder="选择模块查看子分类"
                clearable
                style="width: 200px"
                @change="handleModuleClick"
              >
                <el-option
                  v-for="m in moduleStats"
                  :key="m.module_name"
                  :label="m.module_name"
                  :value="m.module_name"
                />
              </el-select>
            </div>
          </template>
          <el-table :data="subModuleStats" style="width: 100%" max-height="350">
            <el-table-column prop="sub_module_name" label="二级分类" />
            <el-table-column prop="question_count" label="题目数" width="80" align="center" />
            <el-table-column label="掌握度" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="getMasteryTag(row.avg_mastery)" size="small">
                  {{ row.avg_mastery }}%
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="掌握度条" width="120">
              <template #default="{ row }">
                <el-progress
                  :percentage="row.avg_mastery"
                  :color="getMasteryColor(row.avg_mastery)"
                  :show-text="false"
                  :stroke-width="8"
                />
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!selectedModule" description="请选择模块查看子分类详情" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.analysis-page {
  padding: 20px;
  animation: fadeIn 0.4s ease-out;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  margin: 0;
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

.overview-row {
  margin-bottom: 24px;
}

.overview-row .el-card {
  text-align: center;
  overflow: hidden;
  position: relative;
}

.overview-row .el-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 50px;
  height: 3px;
  background: var(--primary-gradient);
  border-radius: 0 0 2px 2px;
  transition: width var(--transition-normal);
}

.overview-row .el-card:hover::before {
  width: 80%;
}

.stat-suffix {
  font-size: 13px;
  color: var(--text-muted);
  margin-left: 4px;
  font-weight: 500;
}

.chart-row {
  margin-bottom: 24px;
}

.chart-card {
  height: 100%;
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 15px;
  color: var(--text-primary);
}

:deep(.el-statistic .el-statistic__head) {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

:deep(.el-statistic .el-statistic__content) {
  font-size: 28px;
  font-weight: 700;
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.coverage-info {
  margin-top: 14px;
  text-align: center;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
}

:deep(.el-progress__text) {
  font-weight: 600;
  font-size: 14px !important;
}

:deep(.el-table) {
  border-radius: var(--radius-md);
  overflow: hidden;
}

:deep(.el-table th.el-table__cell) {
  background: var(--bg-muted) !important;
}

:deep(.el-table td.el-table__cell) {
  transition: background-color var(--transition-fast);
}

:deep(.el-table body tr:hover > td) {
  background-color: rgba(240, 253, 250, 0.5) !important;
}

:deep(.el-select) {
  width: 200px;
}
</style>