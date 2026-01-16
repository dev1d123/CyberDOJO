<template>
  <div class="challenges-page" :style="pageStyle">
    <div class="overlay">
      <ChallengesHeader @back="goBack" />

      <main class="content">
        <section class="grid" aria-label="Minijuegos de desafíos">
          <ChallengeGameCard
            title="¿Confías o no?"
            subtitle="Mensajes cortos: ¡elige si es seguro!"
            mechanic="Aparecen chats/notificaciones. Desliza entre Seguro y Peligroso."
            :gif-src="trustGif"
            preview-type="trust"
            @click="start('trust')"
          />

          <ChallengeGameCard
            title="El chat sospechoso"
            subtitle="Un NPC te escribe... ¿qué respondes?"
            mechanic="Cada turno eliges una respuesta (o reportas) para mantenerte a salvo."
            :gif-src="chatGif"
            preview-type="chat"
            @click="start('chat')"
          />

          <ChallengeGameCard
            title="Caza el engaño"
            subtitle="¡Toca lo peligroso antes del tiempo!"
            mechanic="Se muestra una publicación/conversación. Marca frases peligrosas antes de que se acabe el tiempo."
            :gif-src="huntGif"
            preview-type="hunt"
            @click="start('hunt')"
          />
        </section>

        <section class="hint" aria-label="Consejo">
          <div class="hint-card">
            <span class="hint-title">Tip rápido</span>
            <p class="hint-text">Si alguien te presiona, pide secretos o te asusta para que actúes rápido… probablemente es una trampa.</p>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import ChallengeGameCard from '../components/challenges/ChallengeGameCard.vue';
import ChallengesHeader from '../components/challenges/ChallengesHeader.vue';

const router = useRouter();

// Nota: el usuario indicó que el fondo está en /src/assets/images/challengeBackground.png.
// En este repo aún no existe, así que lo referenciamos como string (no rompe el build).
// Cuando el archivo esté presente, se mostrará automáticamente.
const backgroundUrl = '/src/assets/images/challengeBackground.png';

const trustGif = new URL('../assets/gif/welcome.gif', import.meta.url).href;
const chatGif = new URL('../assets/gif/settingGif.gif', import.meta.url).href;
const huntGif = new URL('../assets/gif/logo.gif', import.meta.url).href;

const pageStyle = computed(() => {
  return {
    backgroundImage: `url(${backgroundUrl})`,
  } as const;
});

type ChallengeId = 'trust' | 'chat' | 'hunt';

const start = (id: ChallengeId) => {
  const map: Record<ChallengeId, string> = {
    trust: '¿Confías o no?',
    chat: 'El chat sospechoso',
    hunt: 'Caza el engaño',
  };

  alert(`Abrir minijuego: ${map[id]} (pronto)`);
};

const goBack = () => {
  router.push('/dashboard');
};
</script>

<style scoped>
.challenges-page {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-color: #1f1b3a;
}

.overlay {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  background: radial-gradient(circle at 20% 0%, rgba(255, 255, 255, 0.12), transparent 55%),
    radial-gradient(circle at 100% 30%, rgba(72, 198, 239, 0.18), transparent 55%),
    rgba(0, 0, 0, 0.28);
  animation: overlayGlow 10s ease-in-out infinite;
}

@keyframes overlayGlow {
  0%, 100% {
    filter: saturate(1);
  }
  50% {
    filter: saturate(1.15);
  }
}

.content {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: clamp(10px, 2vh, 16px);
  padding: 0 clamp(14px, 2.5vw, 24px) clamp(14px, 2.4vh, 20px);
  max-width: 1300px;
  width: 100%;
  margin: 0 auto;
}

.grid {
  flex: 1 1 auto;
  min-height: 0;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: clamp(12px, 2vw, 18px);
}

.hint {
  flex: 0 0 auto;
}

.hint-card {
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.65);
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.22);
  padding: clamp(10px, 2vh, 16px) clamp(12px, 2.2vw, 18px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
}

.hint-title {
  font-weight: 1000;
  color: #4c1d95;
  background: rgba(124, 58, 237, 0.12);
  border: 2px solid rgba(124, 58, 237, 0.18);
  padding: 6px 12px;
  border-radius: 999px;
  white-space: nowrap;
}

.hint-text {
  margin: 0;
  font-weight: 850;
  color: #334155;
  font-size: clamp(0.95rem, 1.2vw, 1.05rem);
  line-height: 1.2;
}

@media (max-width: 980px) {
  .grid {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 520px) {
  .hint-card {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
