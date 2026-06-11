import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { MethodSummary } from '@/types/method'
import * as methodApi from '@/api/method'

export const useMethodStore = defineStore('method', () => {
  const methods = ref<MethodSummary[]>([])
  const currentMethod = ref<MethodSummary | null>(null)
  const loading = ref(false)

  async function fetchMethods(moduleId?: string) {
    loading.value = true
    try {
      methods.value = await methodApi.getMethodList(moduleId)
    } finally {
      loading.value = false
    }
  }

  async function fetchMethodDetail(id: string) {
    loading.value = true
    try {
      currentMethod.value = await methodApi.getMethodDetail(id)
    } finally {
      loading.value = false
    }
  }

  async function generateMethod(moduleId: string) {
    loading.value = true
    try {
      const method = await methodApi.generateMethod(moduleId)
      const index = methods.value.findIndex((m) => m.id === method.id)
      if (index === -1) {
        methods.value.unshift(method)
      } else {
        methods.value[index] = method
      }
      return method
    } finally {
      loading.value = false
    }
  }

  async function updateMethod(id: string, data: Partial<MethodSummary>) {
    loading.value = true
    try {
      const updated = await methodApi.updateMethod(id, data)
      const index = methods.value.findIndex((m) => m.id === id)
      if (index !== -1) {
        methods.value[index] = updated
      }
      if (currentMethod.value?.id === id) {
        currentMethod.value = updated
      }
      return updated
    } finally {
      loading.value = false
    }
  }

  return {
    methods,
    currentMethod,
    loading,
    fetchMethods,
    fetchMethodDetail,
    generateMethod,
    updateMethod,
  }
})
