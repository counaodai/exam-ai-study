<script setup lang="ts">
import HomeHeader from '@/components/home/HomeHeader.vue'
import HomeHero from '@/components/home/HomeHero.vue'
import HomeFeatures from '@/components/home/HomeFeatures.vue'
import HomeStats from '@/components/home/HomeStats.vue'
import HomeFooter from '@/components/home/HomeFooter.vue'
</script>

<template>
  <div class="home-page">
    <HomeHeader />
    <main>
      <HomeHero />
      <HomeFeatures />
      <HomeStats />
    </main>
    <HomeFooter />
  </div>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
  font-family: var(--font-body);
  color: var(--text-primary);
  background: var(--bg-color);
}
</style>
