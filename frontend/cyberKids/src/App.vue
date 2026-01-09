<script setup lang="ts">
import AnimatedBackground from './components/AnimatedBackground.vue';
import Navbar from './components/Navbar.vue';
import HomePage from './pages/HomePage.vue';
</script>

<template>
  <div class="app-container">
    <AnimatedBackground />
    <div class="content-wrapper">
      <Navbar />
      <HomePage />
    </div>
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
</style>
