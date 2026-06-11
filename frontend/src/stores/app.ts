import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const isSidebarCollapsed = ref(false)
  const loading = ref(false)

  function toggleSidebar() {
    isSidebarCollapsed.value = !isSidebarCollapsed.value
  }

  function setLoading(val: boolean) {
    loading.value = val
  }

  return {
    isSidebarCollapsed,
    loading,
    toggleSidebar,
    setLoading,
  }
})
