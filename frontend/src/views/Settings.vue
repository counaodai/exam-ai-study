<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('general')

const settings = ref({
  openai_api_key: '',
  openai_base_url: 'https://api.openai.com/v1',
  model: 'gpt-4o',
  embedding_provider: 'openai',
  embedding_model: 'text-embedding-3-small',
})

function handleSave() {
  ElMessage.success('设置已保存（功能待接入后端）')
}
</script>

<template>
  <div class="settings-page">
    <h1>设置</h1>

    <el-card>
      <el-tabs v-model="activeTab">
        <el-tab-pane label="通用设置" name="general">
          <el-form label-width="120px" style="max-width: 600px">
            <el-form-item label="OpenAI API Key">
              <el-input v-model="settings.openai_api_key" type="password" show-password placeholder="sk-..." />
            </el-form-item>
            <el-form-item label="API Base URL">
              <el-input v-model="settings.openai_base_url" />
            </el-form-item>
            <el-form-item label="模型">
              <el-select v-model="settings.model">
                <el-option label="GPT-4o" value="gpt-4o" />
                <el-option label="GPT-4o-mini" value="gpt-4o-mini" />
                <el-option label="Claude 3.5 Sonnet" value="claude-3-5-sonnet" />
              </el-select>
            </el-form-item>
            <el-form-item label="Embedding 方案">
              <el-radio-group v-model="settings.embedding_provider">
                <el-radio value="openai">OpenAI Embedding</el-radio>
                <el-radio value="local">本地 BGE-M3</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSave">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="分类规则" name="rules">
          <el-empty description="分类规则管理功能将在 Phase 2 实现" />
        </el-tab-pane>

        <el-tab-pane label="数据管理" name="data">
          <el-empty description="数据管理功能将在后续实现" />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<style scoped>
.settings-page {
  animation: fadeIn 0.4s ease-out;
}

.settings-page h1 {
  margin-bottom: 28px;
  font-size: 24px;
  font-family: var(--font-heading);
  position: relative;
  padding-left: 14px;
}

.settings-page h1::before {
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

:deep(.el-card) {
  overflow: hidden;
}

:deep(.el-form-item) {
  margin-bottom: 22px;
}

:deep(.el-form-item__label) {
  font-weight: 600;
  color: var(--text-regular);
}

:deep(.el-input__wrapper) {
  transition: all var(--transition-fast);
}

:deep(.el-input__wrapper:hover) {
  border-color: var(--primary-light);
}

:deep(.el-input__wrapper.is-focus) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(13, 148, 136, 0.1);
}

:deep(.el-radio-group) {
  display: flex;
  gap: 12px;
}

:deep(.el-radio-button) {
  border-radius: var(--radius-sm) !important;
}
</style>
