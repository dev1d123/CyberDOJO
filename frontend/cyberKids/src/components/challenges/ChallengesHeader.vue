<template>
  <header class="header">
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
const mascotGif = '/assets/gif/challengeGif.gif';
</script>

<style scoped>
.header {
  width: 100%;
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: clamp(10px, 2vw, 18px);
  padding: clamp(10px, 2vh, 18px) clamp(12px, 3vw, 24px);
}

.titles {
  text-align: center;
  min-width: 0;
}

.title {
  margin: 0;
  color: white;
  font-size: clamp(1.5rem, 5vw, 2.8rem);
  text-shadow: 4px 4px 10px rgba(0, 0, 0, 0.28);
  font-weight: 1000;
}

.subtitle {
  margin: 4px 0 0 0;
  color: rgba(255, 255, 255, 0.92);
  font-weight: 800;
  font-size: clamp(0.8rem, 2.8vw, 1.15rem);
  text-shadow: 2px 2px 7px rgba(0, 0, 0, 0.2);
  line-height: 1.2;
}

.mascot {
  width: clamp(48px, 10vw, 86px);
  height: clamp(48px, 10vw, 86px);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.62);
  border: 2px solid rgba(255, 255, 255, 0.75);
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.18);
  display: grid;
  place-items: center;
  animation: floaty 2.8s ease-in-out infinite;
  flex-shrink: 0;
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

@media (max-width: 900px) {
  .header {
    padding: clamp(10px, 2.5vh, 16px) clamp(10px, 2.5vw, 18px);
    gap: clamp(8px, 2vw, 12px);
  }

  .mascot {
    width: clamp(40px, 9vw, 72px);
    height: clamp(40px, 9vw, 72px);
  }
}

@media (max-width: 640px) {
  .header {
    grid-template-columns: 1fr;
    padding: clamp(8px, 2.5vh, 14px) clamp(10px, 3vw, 14px);
    gap: clamp(6px, 2vh, 10px);
  }

  .titles {
    text-align: center;
  }

  .title {
    font-size: clamp(1.3rem, 5vw, 1.8rem);
  }

  .subtitle {
    font-size: clamp(0.75rem, 2.5vw, 0.95rem);
    margin: 3px 0 0 0;
  }

  .mascot {
    width: clamp(36px, 10vw, 60px);
    height: clamp(36px, 10vw, 60px);
    margin: 0 auto;
  }
}
</style>
