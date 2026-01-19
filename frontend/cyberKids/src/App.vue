<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import AnimatedBackground from './components/AnimatedBackground.vue';
import Navbar from './components/Navbar.vue';
import PetViewer from './components/PetViewer.vue';

const route = useRoute();

// Solo mostrar el background y navbar en la página principal
const showLayout = computed(() => route.path === '/');

// Mostrar PetViewer en todas las páginas excepto home y login/register
const showPetViewer = computed(() => {
  const hiddenRoutes = ['/', '/login', '/register'];
  return !hiddenRoutes.includes(route.path);
});
</script>

<template>
  <div class="app-container">
    <AnimatedBackground v-if="showLayout" />
    <div class="content-wrapper" :class="{ 'no-bg': !showLayout }">
      <Navbar v-if="showLayout" />
      <router-view />
    </div>
    <PetViewer v-if="showPetViewer" />
  </div>
</template>

<style scoped>
.app-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  position: relative;
  background-color: #fee440;
}

.content-wrapper {
  position: relative;
  z-index: 1;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-wrapper.no-bg {
  background: transparent;
  overflow-y: auto;
}
</style>
