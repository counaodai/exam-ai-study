<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppSidebar from './components/layout/AppSidebar.vue'
import AppHeader from './components/layout/AppHeader.vue'

const route = useRoute()
const showAppLayout = computed(() => route.meta.layout !== 'landing')
</script>

<template>
  <div v-if="showAppLayout" class="app-container">
    <AppSidebar />
    <div class="app-right">
      <AppHeader />
      <main class="app-main">
        <router-view />
      </main>
    </div>
  </div>
  <router-view v-else />
</template>

<style scoped>
.app-container {
  height: 100vh;
  overflow: hidden;
  display: flex;
}

.app-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.app-main {
  background-color: var(--bg-color);
  overflow-y: auto;
  padding: 24px;
  position: relative;
}
</style>
