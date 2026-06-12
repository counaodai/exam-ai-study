<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('general')

// 通用设置
const settings = ref({
  openai_api_key: '',
  openai_base_url: 'https://api.openai.com/v1',
  model: 'gpt-4o',
  embedding_provider: 'openai',
  embedding_model: 'text-embedding-3-small',
})

// 分类规则
const rules = ref({
  enable_auto_classify: true,
  classify_level: 'two',
  rules_list: [
    { id: 1, name: '行测-言语理解', pattern: '阅读理解|逻辑填空|片段阅读', active: true },
    { id: 2, name: '行测-数量关系', pattern: '数量关系|数学运算|应用题', active: true },
    { id: 3, name: '行测-判断推理', pattern: '图形推理|类比推理|定义判断', active: true },
    { id: 4, name: '行测-资料分析', pattern: '资料分析|图表|统计', active: false },
    { id: 5, name: '申论-公文写作', pattern: '申论|公文|作文|对策', active: false },
  ],
})

// 数据管理
const dataStats = ref({
  total_documents: 12,
  total_questions: 386,
  total_mindmaps: 8,
  vector_count: 1247,
  storage_size: '156MB',
})

const showDeleteDialog = ref(false)
const showExportDialog = ref(false)
const exportFormat = ref('json')

function handleSave() {
  ElMessage.success('设置已保存，慢慢来，AI 会记住你的偏好')
}

function handleRuleToggle(id: number) {
  const rule = rules.value.rules_list.find(r => r.id === id)
  if (!rule) return
  rule.active = !rule.active
  ElMessage.info(rule.active ? `「${rule.name}」已开启` : `「${rule.name}」已关闭`)
}

function handleAddRule() {
  rules.value.rules_list.push({
    id: Date.now(),
    name: '新分类规则',
    pattern: '',
    active: true,
  })
  ElMessage.info('已添加新规则，点击编辑即可')
}

function handleRemoveRule(id: number) {
  rules.value.rules_list = rules.value.rules_list.filter(r => r.id !== id)
  ElMessage.info('规则已移除')
}

function handleClearCache() {
  ElMessage.success('缓存已清理，轻装上阵')
}

function handleExportData() {
  ElMessage.success('数据导出中，稍后会提示下载')
}

function handleDeleteAll() {
  showDeleteDialog.value = false
  ElMessage.warning('所有数据已清除，从零开始吧')
}

function handleBackup() {
  ElMessage.success('备份创建成功，数据稳稳的')
}
</script>

<template>
  <div class="settings-page">
    <!-- 页面标题区 -->
    <div class="page-header">
      <div class="header-icon">
        <iconify-icon icon="mdi:cog-outline" width="32" />
      </div>
      <div class="header-text">
        <h1>设置</h1>
        <p class="page-subtitle">慢慢来，慢慢来，这里能帮你定制专属学习方案</p>
      </div>
      <!-- 装饰波浪 -->
      <svg class="header-deco" viewBox="0 0 200 20" preserveAspectRatio="none" aria-hidden="true">
        <path
          d="M0,10 C20,2 40,18 60,10 C80,2 100,18 120,10 C140,2 160,18 180,10 C190,6 195,12 200,10"
          stroke="var(--primary-lighter)"
          stroke-width="1.5"
          fill="none"
          stroke-linecap="round"
        />
      </svg>
    </div>

    <!-- 主内容区 -->
    <el-card class="settings-card">
      <el-tabs v-model="activeTab" class="settings-tabs hand-drawn-tabs">
        <!-- ========== 通用设置 ========== -->
        <el-tab-pane name="general">
          <template #label>
            <span class="tab-label">
              <iconify-icon icon="mdi:palette-outline" width="16" />
              通用设置
            </span>
          </template>

          <div class="tab-section">
            <div class="section-header">
              <iconify-icon icon="mdi:lightbulb-outline" width="20" class="section-icon" />
              <span>AI 模型配置</span>
            </div>
            <p class="section-desc">想让 AI 更懂你？从这里调整模型参数</p>

            <el-form label-width="130px" class="settings-form" label-position="top">
              <el-form-item label="🔑 OpenAI API Key">
                <el-input
                  v-model="settings.openai_api_key"
                  type="password"
                  show-password
                  placeholder="sk-..."
                  clearable
                />
                <template #hint>输入你的 API Key，它会被安全地保存在本地</template>
              </el-form-item>

              <el-form-item label="🌐 API Base URL">
                <el-input v-model="settings.openai_base_url" placeholder="https://api.openai.com/v1" />
                <template #hint>兼容 Anthropic 接口协议的端点地址</template>
              </el-form-item>

              <el-form-item label="🤖 对话模型">
                <el-select v-model="settings.model" placeholder="选择默认模型">
                  <el-option label="GPT-4o（推荐）" value="gpt-4o" />
                  <el-option label="GPT-4o-mini（轻量）" value="gpt-4o-mini" />
                  <el-option label="Claude 3.5 Sonnet" value="claude-3-5-sonnet" />
                  <el-option label="mimo（兼容 Anthropic）" value="mimo" />
                </el-select>
              </el-form-item>
            </el-form>
          </div>

          <div class="tab-section">
            <div class="section-header">
              <iconify-icon icon="mdi:database-outline" width="20" class="section-icon" />
              <span>向量化方案</span>
            </div>
            <p class="section-desc">题目分类和检索需要用到向量嵌入</p>

            <el-form label-width="130px" class="settings-form" label-position="top">
              <el-form-item label="Embedding 方案">
                <el-radio-group v-model="settings.embedding_provider">
                  <el-radio-button value="openai">OpenAI Embedding</el-radio-button>
                  <el-radio-button value="local">本地 BGE-M3</el-radio-button>
                </el-radio-group>
              </el-form-item>

              <el-form-item v-if="settings.embedding_provider === 'openai'" label="嵌入模型">
                <el-select v-model="settings.embedding_model" placeholder="选择嵌入模型">
                  <el-option label="text-embedding-3-small" value="text-embedding-3-small" />
                  <el-option label="text-embedding-3-large" value="text-embedding-3-large" />
                  <el-option label="text-embedding-ada-002" value="text-embedding-ada-002" />
                </el-select>
              </el-form-item>

              <el-form-item v-if="settings.embedding_provider === 'local'" label="本地模型路径">
                <el-input placeholder="./models/bge-m3" />
              </el-form-item>
            </el-form>
          </div>

          <div class="tab-actions">
            <el-button type="primary" size="large" @click="handleSave">
              <iconify-icon icon="mdi:content-save-outline" width="18" />
              保存设置
            </el-button>
          </div>
        </el-tab-pane>

        <!-- ========== 分类规则 ========== -->
        <el-tab-pane name="rules">
          <template #label>
            <span class="tab-label">
              <iconify-icon icon="mdi:tag-outline" width="16" />
              分类规则
            </span>
          </template>

          <div class="tab-section">
            <div class="section-header">
              <iconify-icon icon="mdi:toggle-outline" width="20" class="section-icon" />
              <span>自动分类开关</span>
            </div>
            <p class="section-desc">开启后，AI 会自动给题目打标签、归分类</p>

            <div class="toggle-row">
              <div class="toggle-info">
                <span class="toggle-title">启用自动分类</span>
                <span class="toggle-desc">导入题目后自动执行两级分类</span>
              </div>
              <el-switch
                v-model="rules.enable_auto_classify"
                active-text="开启"
                inactive-text="关闭"
                inline-prompt
                style="--el-switch-on-color: #5B8C5A; --el-switch-off-color: #B5AA90"
              />
            </div>
          </div>

          <div class="tab-section">
            <div class="section-header">
              <iconify-icon icon="mdi:layers-triple-outline" width="20" class="section-icon" />
              <span>分类级别</span>
            </div>

            <el-radio-group v-model="rules.classify_level" class="level-selector">
              <el-radio-button value="one">一级分类（仅按考试模块）</el-radio-button>
              <el-radio-button value="two">二级分类（模块 + 考点）</el-radio-button>
            </el-radio-group>
          </div>

          <div class="tab-section">
            <div class="section-header section-header-actions">
              <div>
                <iconify-icon icon="mdi:format-list-checks-outline" width="20" class="section-icon" />
                <span>规则列表</span>
              </div>
              <el-button size="small" @click="handleAddRule">
                <iconify-icon icon="mdi:plus" width="16" />
                新增规则
              </el-button>
            </div>
            <p class="section-desc">匹配规则越详细，分类越精准</p>

            <div class="rules-list">
              <div
                v-for="rule in rules.rules_list"
                :key="rule.id"
                class="rule-item"
                :class="{ inactive: !rule.active }"
              >
                <div class="rule-left">
                  <el-tag
                    :type="rule.active ? 'success' : 'info'"
                    class="rule-status"
                    effect="light"
                  >
                    {{ rule.active ? '活跃' : '停用' }}
                  </el-tag>
                  <span class="rule-name">{{ rule.name }}</span>
                </div>
                <div class="rule-center">
                  <span class="rule-pattern">{{ rule.pattern || '未配置' }}</span>
                </div>
                <div class="rule-actions">
                  <button
                    class="action-btn edit-btn"
                    aria-label="编辑规则"
                  >
                    <iconify-icon icon="mdi:pencil-outline" width="16" />
                  </button>
                  <button
                    class="action-btn toggle-btn"
                    @click="handleRuleToggle(rule.id)"
                    :aria-label="rule.active ? '停用规则' : '启用规则'"
                  >
                    <iconify-icon :icon="rule.active ? 'mdi:toggle-switch' : 'mdi:toggle-switch-off-outline'" width="16" />
                  </button>
                  <button
                    class="action-btn delete-btn"
                    @click="handleRemoveRule(rule.id)"
                    aria-label="删除规则"
                  >
                    <iconify-icon icon="mdi:trash-can-outline" width="16" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- ========== 数据管理 ========== -->
        <el-tab-pane name="data">
          <template #label>
            <span class="tab-label">
              <iconify-icon icon="mdi:database-sync-outline" width="16" />
              数据管理
            </span>
          </template>

          <div class="tab-section">
            <div class="section-header">
              <iconify-icon icon="mdi:chart-pie-outline" width="20" class="section-icon" />
              <span>数据概览</span>
            </div>
            <p class="section-desc">你的学习仓库，一眼看得清</p>

            <div class="data-grid">
              <div class="data-card">
                <div class="data-icon">
                  <iconify-icon icon="mdi:file-document-outline" width="24" />
                </div>
                <div class="data-info">
                  <span class="data-value">{{ dataStats.total_documents }}</span>
                  <span class="data-label">文档数</span>
                </div>
              </div>
              <div class="data-card">
                <div class="data-icon">
                  <iconify-icon icon="mdi:format-list-bulleted" width="24" />
                </div>
                <div class="data-info">
                  <span class="data-value">{{ dataStats.total_questions }}</span>
                  <span class="data-label">题目数</span>
                </div>
              </div>
              <div class="data-card">
                <div class="data-icon">
                  <iconify-icon icon="mdi:sitemap-outline" width="24" />
                </div>
                <div class="data-info">
                  <span class="data-value">{{ dataStats.total_mindmaps }}</span>
                  <span class="data-label">思维导图</span>
                </div>
              </div>
              <div class="data-card">
                <div class="data-icon">
                  <iconify-icon icon="mdi:chart-histogram" width="24" />
                </div>
                <div class="data-info">
                  <span class="data-value">{{ dataStats.vector_count.toLocaleString() }}</span>
                  <span class="data-label">向量数</span>
                </div>
              </div>
              <div class="data-card data-card-wide">
                <div class="data-icon">
                  <iconify-icon icon="mdi:harddisk" width="24" />
                </div>
                <div class="data-info">
                  <span class="data-value">{{ dataStats.storage_size }}</span>
                  <span class="data-label">存储占用</span>
                </div>
              </div>
            </div>
          </div>

          <div class="tab-section">
            <div class="section-header">
              <iconify-icon icon="mdi:tools-outline" width="20" class="section-icon" />
              <span>数据操作</span>
            </div>
            <p class="section-desc">谨慎操作，建议先备份</p>

            <div class="action-cards">
              <div class="action-card action-card-success">
                <div class="action-card-icon">
                  <iconify-icon icon="mdi:download" width="28" />
                </div>
                <div class="action-card-info">
                  <span class="action-card-title">导出数据</span>
                  <span class="action-card-desc">导出所有题目、分类和思维导图数据</span>
                </div>
                <el-button size="default" @click="showExportDialog = true">
                  导出
                </el-button>
              </div>

              <div class="action-card action-card-info">
                <div class="action-card-icon">
                  <iconify-icon icon="mdi:backup" width="28" />
                </div>
                <div class="action-card-info">
                  <span class="action-card-title">创建备份</span>
                  <span class="action-card-desc">生成完整数据快照，随时可恢复</span>
                </div>
                <el-button type="success" size="default" @click="handleBackup">
                  备份
                </el-button>
              </div>

              <div class="action-card action-card-warning">
                <div class="action-card-icon">
                  <iconify-icon icon="mdi:broomball" width="28" />
                </div>
                <div class="action-card-info">
                  <span class="action-card-title">清理缓存</span>
                  <span class="action-card-desc">清除临时文件和未使用的向量</span>
                </div>
                <el-button type="warning" size="default" @click="handleClearCache">
                  清理
                </el-button>
              </div>

              <div class="action-card action-card-danger">
                <div class="action-card-icon">
                  <iconify-icon icon="mdi:delete-outline" width="28" />
                </div>
                <div class="action-card-info">
                  <span class="action-card-title">清空数据</span>
                  <span class="action-card-desc">删除所有文档、分类和记录</span>
                </div>
                <el-button type="danger" size="default" @click="showDeleteDialog = true">
                  清空
                </el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 清空数据确认对话框 -->
    <el-dialog
      v-model="showDeleteDialog"
      title="⚠️ 确定要清空所有数据？"
      width="420px"
      class="hand-drawn-dialog"
    >
      <p class="dialog-desc">这个操作不可撤销，所有题目、分类、思维导图都会被删除。</p>
      <p class="dialog-desc">建议先导出数据备份。</p>
      <template #footer>
        <el-button @click="showDeleteDialog = false">再想想</el-button>
        <el-button type="danger" @click="handleDeleteAll">是的，全部清空</el-button>
      </template>
    </el-dialog>

    <!-- 导出格式对话框 -->
    <el-dialog
      v-model="showExportDialog"
      title="📦 导出数据"
      width="420px"
      class="hand-drawn-dialog"
    >
      <el-form label-width="80px" label-position="left">
        <el-form-item label="导出格式">
          <el-radio-group v-model="exportFormat">
            <el-radio value="json">JSON</el-radio>
            <el-radio value="csv">CSV</el-radio>
            <el-radio value="xlsx">Excel</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showExportDialog = false">取消</el-button>
        <el-button type="primary" @click="handleExportData">开始导出</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
/* ---- 页面布局 ---- */
.settings-page {
  --settings-section-title: #5D4E37;
  --settings-icon-bg: #E8F0E4;
  animation: cardEnter 0.5s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}

/* ---- 页面标题区 ---- */
.page-header {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 28px;
  position: relative;
}

.header-icon {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-hand-drawn-soft);
  background: var(--primary-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(91, 140, 90, 0.25);
  transform: rotate(-3deg);
}

.header-text h1 {
  font-size: 26px;
  font-family: var(--font-heading);
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
  letter-spacing: 0.02em;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  font-family: var(--font-body);
  margin: 0;
}

.header-deco {
  position: absolute;
  bottom: -12px;
  left: 0;
  width: 100%;
  height: 20px;
  opacity: 0.5;
}

/* ---- 主卡片 ---- */
.settings-card {
  overflow: hidden;
  border-radius: var(--radius-hand-drawn) !important;
}

/* ---- 自定义标签页 ---- */
.settings-tabs {
  --el-text-color-regular: var(--text-secondary);
  --el-border-color: var(--border-light);
}

.hand-drawn-tabs :deep(.el-tabs__header) {
  margin-bottom: 24px;
  padding: 0 8px;
  border-bottom: none;
}

.hand-drawn-tabs :deep(.el-tabs__item) {
  height: 48px !important;
  line-height: 48px !important;
  padding: 0 24px !important;
  font-family: var(--font-heading) !important;
  font-weight: 600 !important;
  font-size: 15px !important;
  color: var(--text-secondary) !important;
  border-radius: var(--radius-hand-drawn-soft) !important;
  margin-right: 10px !important;
  transition: all var(--transition-hover-lift) !important;
  border: 2px solid transparent !important;
  background: var(--bg-muted) !important;
}

.hand-drawn-tabs :deep(.el-tabs__item:hover) {
  color: var(--primary-color) !important;
  background: var(--primary-bg) !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(91, 140, 90, 0.1);
}

.hand-drawn-tabs :deep(.el-tabs__item.is-active) {
  color: var(--primary-color) !important;
  background: var(--primary-bg) !important;
  border-color: var(--primary-lighter) !important;
  font-weight: 700 !important;
  box-shadow: 0 3px 12px rgba(91, 140, 90, 0.15) !important;
}

.hand-drawn-tabs :deep(.el-tabs__active-bar) {
  display: none !important;
}

.tab-label {
  display: flex !important;
  align-items: center;
  gap: 8px;
}

.tab-label .iconify-icon {
  transition: transform var(--transition-hover-lift);
}

.tab-label:hover .iconify-icon {
  transform: rotate(8deg) scale(1.1);
}

/* ---- 区块 ---- */
.tab-section {
  margin-bottom: 28px;
  padding-bottom: 28px;
  border-bottom: 2px dashed var(--border-light);
}

.tab-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
  font-family: var(--font-heading);
  font-size: 17px;
  font-weight: 700;
  color: var(--settings-section-title);
}

.section-header-actions {
  justify-content: space-between;
}

.section-icon {
  color: var(--primary-color);
}

.section-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 18px;
  font-family: var(--font-body);
  line-height: 1.6;
}

/* ---- 表单 ---- */
.settings-form {
  margin-top: 16px;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-form-item__label) {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-regular);
  padding-bottom: 8px;
}

:deep(.el-form-item .el-form-item__content) {
  margin-left: 0 !important;
}

:deep(.el-input__wrapper) {
  transition: all var(--transition-fade);
}

:deep(.el-select .el-input__wrapper) {
  border-radius: var(--radius-hand-drawn-soft) !important;
}

/* ---- 按钮区 ---- */
.tab-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 2px dashed var(--border-light);
  margin-top: 12px;
}

.tab-actions .el-button {
  padding: 14px 36px;
  font-size: 15px;
  border-radius: var(--radius-hand-drawn-soft) !important;
}

.tab-actions .el-button .iconify-icon {
  margin-right: 6px;
}

/* ---- 分类规则 - 开关行 ---- */
.toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: var(--bg-surface);
  border-radius: var(--radius-hand-drawn-soft);
  border: 2px solid var(--border-light);
}

.toggle-title {
  display: block;
  font-family: var(--font-heading);
  font-weight: 600;
  font-size: 15px;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.toggle-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

/* ---- 分类级别 ---- */
.level-selector {
  display: flex;
  gap: 10px;
  margin-top: 8px;
}

.level-selector .el-radio-button {
  border-radius: var(--radius-hand-drawn-soft) !important;
}

/* ---- 规则列表 ---- */
.rules-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.rule-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  background: var(--bg-surface);
  border-radius: var(--radius-hand-drawn-soft);
  border: 2px solid var(--border-light);
  transition: all var(--transition-hover-lift);
}

.rule-item:hover {
  border-color: var(--primary-lighter);
  transform: translateX(4px);
  box-shadow: var(--shadow-sm);
}

.rule-item.inactive {
  opacity: 0.6;
  background: var(--bg-muted);
}

.rule-left {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.rule-status {
  font-size: 11px;
  padding: 2px 10px;
  border-radius: var(--radius-full) !important;
}

.rule-name {
  font-family: var(--font-heading);
  font-weight: 600;
  font-size: 14px;
  color: var(--text-primary);
}

.rule-center {
  flex: 1;
  min-width: 0;
}

.rule-pattern {
  font-size: 13px;
  color: var(--text-secondary);
  font-family: var(--font-body);
  background: var(--bg-muted);
  padding: 4px 12px;
  border-radius: var(--radius-full);
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rule-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.action-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  border-radius: var(--radius-full);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  transform: scale(1.15);
}

.edit-btn:hover {
  background: var(--primary-bg);
  color: var(--primary-color);
}

.toggle-btn:hover {
  background: var(--primary-bg);
  color: var(--primary-color);
}

.delete-btn:hover {
  background: #FEF2F2;
  color: var(--danger-color);
}

/* ---- 数据管理 - 数据概览 ---- */
.data-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-top: 16px;
}

.data-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 16px;
  background: var(--bg-surface);
  border-radius: var(--radius-hand-drawn-soft);
  border: 2px solid var(--border-light);
  transition: all var(--transition-hover-lift);
}

.data-card:hover {
  border-color: var(--primary-lighter);
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.data-card-wide {
  grid-column: span 4;
  background: linear-gradient(135deg, var(--primary-bg) 0%, var(--bg-surface) 100%);
  border-color: var(--primary-lighter);
}

.data-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-hand-drawn-soft);
  background: var(--settings-icon-bg);
  color: var(--primary-color);
  flex-shrink: 0;
}

.data-info {
  display: flex;
  flex-direction: column;
}

.data-value {
  font-family: var(--font-heading);
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
}

.data-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-family: var(--font-body);
}

/* ---- 数据操作卡片 ---- */
.action-cards {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 16px;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 18px 20px;
  background: var(--bg-surface);
  border-radius: var(--radius-hand-drawn-soft);
  border: 2px solid var(--border-light);
  transition: all var(--transition-hover-lift);
}

.action-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.action-card-success {
  border-color: var(--success-color);
}

.action-card-info {
  border-color: var(--info-color);
}

.action-card-warning {
  border-color: var(--warning-color);
}

.action-card-danger {
  border-color: var(--danger-color);
}

.action-card-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-hand-drawn-soft);
  flex-shrink: 0;
}

.action-card-success .action-card-icon {
  background: rgba(123, 160, 122, 0.15);
  color: var(--success-color);
}

.action-card-info .action-card-icon {
  background: rgba(138, 126, 106, 0.15);
  color: var(--info-color);
}

.action-card-warning .action-card-icon {
  background: rgba(196, 163, 90, 0.15);
  color: var(--warning-color);
}

.action-card-danger .action-card-icon {
  background: rgba(192, 105, 74, 0.15);
  color: var(--danger-color);
}

.action-card-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.action-card-title {
  display: block;
  font-family: var(--font-heading);
  font-weight: 700;
  font-size: 15px;
  color: var(--text-primary);
}

.action-card-desc {
  font-size: 12px;
  color: var(--text-secondary);
  font-family: var(--font-body);
}

/* ---- 对话框 ---- */
.hand-drawn-dialog :deep(.el-dialog) {
  border-radius: var(--radius-hand-drawn) !important;
}

.dialog-desc {
  font-size: 14px;
  color: var(--text-regular);
  line-height: 1.7;
  font-family: var(--font-body);
  margin-bottom: 8px;
}

/* ---- 响应式 ---- */
@media (max-width: 1024px) {
  .data-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .data-card-wide {
    grid-column: span 2;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-icon {
    width: 44px;
    height: 44px;
  }

  .data-grid {
    grid-template-columns: 1fr;
  }

  .data-card-wide {
    grid-column: span 1;
  }

  .rule-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .rule-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .level-selector {
    flex-direction: column;
  }
}
</style>
