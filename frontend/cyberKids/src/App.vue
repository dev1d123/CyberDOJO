<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import AnimatedBackground from './components/AnimatedBackground.vue';
import Navbar from './components/Navbar.vue';
import PetViewer from './components/PetViewer.vue';
import AudioControls from './components/AudioControls.vue';
import AchievementToast from './components/AchievementToast.vue';
import { AudioService } from './services/audio.service';
import { setPetEquipped } from './stores/petState.store';

const route = useRoute();

const isHomeRoute = computed(() => route.path === '/');
const mutedBeforeHome = ref<boolean | null>(null);

// Inicializar sistema de audio
onMounted(() => {
  // Inicializar estado de mascota como no equipada por defecto
  setPetEquipped(null);

  // Preferencias de accesibilidad (evitar animaciones si el usuario lo pide)
  const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  const syncReducedMotion = () => {
    prefersReducedMotion.value = motionQuery.matches;
  };
  syncReducedMotion();

  if ('addEventListener' in motionQuery) {
    motionQuery.addEventListener('change', syncReducedMotion);
  } else {
    // @ts-expect-error - soporte legacy
    motionQuery.addListener(syncReducedMotion);
  }
  
  // Agregar event listener global para clicks
  const handleDocumentClick = () => {
    if (isHomeRoute.value) return;
    AudioService.playClick();
    AudioService.playBackgroundMusic(); // Siempre intentar reproducir background
  };

  document.addEventListener('click', handleDocumentClick);

  onUnmounted(() => {
    document.removeEventListener('click', handleDocumentClick);

    if ('removeEventListener' in motionQuery) {
      motionQuery.removeEventListener('change', syncReducedMotion);
    } else {
      // @ts-expect-error - soporte legacy
      motionQuery.removeListener(syncReducedMotion);
    }
  });
});

watch(
  () => route.path,
  (newPath, oldPath) => {
    if (newPath === '/') {
      if (mutedBeforeHome.value === null) {
        mutedBeforeHome.value = AudioService.getMuted();
      }
      AudioService.stopBackgroundMusic();
      AudioService.setMuted(true);
      return;
    }

    if (oldPath === '/' && mutedBeforeHome.value !== null) {
      AudioService.setMuted(mutedBeforeHome.value);
      mutedBeforeHome.value = null;
    }
  },
  { immediate: true }
);

// Solo mostrar el background y navbar en la página principal
const showLayout = computed(() => route.path === '/');

const showAudioControls = computed(() => {
  const hiddenRoutes = ['/', '/login', '/register'];
  return !hiddenRoutes.includes(route.path);
});

// Mostrar PetViewer en todas las páginas excepto home y login/register
const showPetViewer = computed(() => {
  const hiddenRoutes = ['/', '/login', '/register'];
  return !hiddenRoutes.includes(route.path);
});

const prefersReducedMotion = ref(false);
</script>

<template>
  <div class="app-container">
    <AnimatedBackground v-if="showLayout" />
    <div class="content-wrapper" :class="{ 'no-bg': !showLayout }">
      <Navbar v-if="showLayout" />
      <router-view :key="route.fullPath" />
    </div>
    <PetViewer v-if="showPetViewer" />
    <AudioControls v-if="showAudioControls" />
    <AchievementToast />
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
