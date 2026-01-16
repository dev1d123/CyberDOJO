<template>
  <header class="header">
    <button class="back" type="button" @click="emit('back')">
      <span class="back-icon" aria-hidden="true">⬅</span>
      <span class="back-text">Dashboard</span>
    </button>

    <div class="titles">
      <h1 class="title">Desafíos</h1>
      <p class="subtitle">¡Elige un minijuego y conviértete en héroe cibernético!</p>
    </div>

    <div class="mascot" aria-hidden="true">
      <img class="mascot-gif" :src="mascotGif" alt="" />
    </div>
  </header>
</template>

<script setup lang="ts">
const mascotGif = new URL('../../assets/gif/challengeGif.gif', import.meta.url).href;

const emit = defineEmits<{ (event: 'back'): void }>();
</script>

<style scoped>
.header {
  width: 100%;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 14px;
  padding: clamp(12px, 2.4vh, 18px) clamp(14px, 2.5vw, 24px);
}

.back {
  border: none;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 999px;
  font-weight: 1000;
  color: white;
  background: rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 14px 36px rgba(0, 0, 0, 0.18);
  transition: transform 0.18s ease, background 0.18s ease;
}

.back:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.24);
}

.back:active {
  transform: translateY(0px);
}

.back-icon {
  display: inline-block;
  animation: wiggle 1.6s ease-in-out infinite;
}

@keyframes wiggle {
  0%, 100% {
    transform: rotate(0deg);
  }
  50% {
    transform: rotate(-10deg);
  }
}

.back-text {
  font-size: 0.95rem;
}

.titles {
  text-align: center;
  min-width: 0;
}

.title {
  margin: 0;
  color: white;
  font-size: clamp(1.8rem, 3vw, 2.8rem);
  text-shadow: 4px 4px 10px rgba(0, 0, 0, 0.28);
}

.subtitle {
  margin: 6px 0 0 0;
  color: rgba(255, 255, 255, 0.92);
  font-weight: 800;
  font-size: clamp(0.95rem, 1.4vw, 1.15rem);
  text-shadow: 2px 2px 7px rgba(0, 0, 0, 0.2);
}

.mascot {
  width: clamp(52px, 8vh, 86px);
  height: clamp(52px, 8vh, 86px);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.62);
  border: 2px solid rgba(255, 255, 255, 0.75);
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.18);
  display: grid;
  place-items: center;
  animation: floaty 2.8s ease-in-out infinite;
}

@keyframes floaty {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-7px);
  }
}

.mascot-gif {
  width: 86%;
  height: 86%;
  object-fit: contain;
}

@media (max-width: 820px) {
  .header {
    grid-template-columns: auto 1fr;
  }

  .mascot {
    display: none;
  }
}
</style>
