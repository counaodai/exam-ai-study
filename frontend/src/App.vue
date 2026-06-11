<script setup lang="ts">
import AppSidebar from './components/layout/AppSidebar.vue'
import AppHeader from './components/layout/AppHeader.vue'
</script>

<template>
  <el-container class="app-container">
    <AppSidebar />
    <el-container>
      <AppHeader />
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.app-container {
  height: 100vh;
  overflow: hidden;
}

.app-main {
  background-color: var(--bg-color);
  overflow-y: auto;
  padding: 24px;
}
</style>
