<template>
  <div class="challenges-page" :style="pageStyle">
    <div class="overlay">
      <BackToDashboardButton />
      <ChallengesHeader />

      <main class="content">
        <section class="grid" aria-label="Minijuegos de desafíos">
          <div v-pet-hint="{ behavior: 'hover_module', vars: { target: '¿Confías o no?' }, click: { behavior: 'start_challenge', vars: { target: '¿Confías o no?' }, ttlMs: 1800, priority: 1 } }">
            <ChallengeGameCard
              title="¿Confías o no?"
              subtitle="Mensajes cortos: ¡elige si es seguro!"
              mechanic="Aparecen chats/notificaciones. Desliza entre Seguro y Peligroso."
              :gif-src="trustGif"
              preview-type="trust"
              @click="start('trust')"
            />
          </div>

          <div v-pet-hint="{ behavior: 'hover_module', vars: { target: 'El chat sospechoso' }, click: { behavior: 'start_challenge', vars: { target: 'El chat sospechoso' }, ttlMs: 1800, priority: 1 } }">
            <ChallengeGameCard
              title="El chat sospechoso"
              subtitle="Un NPC te escribe... ¿qué respondes?"
              mechanic="Cada turno eliges una respuesta (o reportas) para mantenerte a salvo."
              :gif-src="chatGif"
              preview-type="chat"
              @click="start('chat')"
            />
          </div>

          <div v-pet-hint="{ behavior: 'hover_module', vars: { target: 'Caza el engaño' }, click: { behavior: 'start_challenge', vars: { target: 'Caza el engaño' }, ttlMs: 1800, priority: 1 } }">
            <ChallengeGameCard
              title="Caza el engaño"
              subtitle="¡Toca lo peligroso antes del tiempo!"
              mechanic="Se muestra una publicación/conversación. Marca frases peligrosas antes de que se acabe el tiempo."
              :gif-src="huntGif"
              preview-type="hunt"
              @click="start('hunt')"
            />
          </div>
          <!--  Agregado por Julio: tarjeta de Quiz (sintaxis simplificada para evitar errores de parsing) -->
          <div class="quiz-card-wrap">
            <ChallengeGameCard
              title="Quiz de Amenazas"
              subtitle="Pon a prueba tu ciber-instinto"
              mechanic="Responde una serie de preguntas interactivas sobre cómo reconocer mensajes falsos y estafas digitales."
              :gif-src="huntGif"
              preview-type="quiz"
              @click="start('quiz')"
            />
          </div>
          <!-- Fin agregado por Julio -->
          
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
import BackToDashboardButton from '../components/BackToDashboardButton.vue';
import ChallengeGameCard from '../components/challenges/ChallengeGameCard.vue';
import ChallengesHeader from '../components/challenges/ChallengesHeader.vue';

const router = useRouter();

const backgroundUrl = new URL('../assets/images/challengeBackground.png', import.meta.url).href;

const trustGif = new URL('../assets/gif/welcome.gif', import.meta.url).href;
const chatGif = new URL('../assets/gif/settingGif.gif', import.meta.url).href;
const huntGif = new URL('../assets/gif/logo.gif', import.meta.url).href;

const pageStyle = computed(() => {
  return {
    backgroundImage: `url(${backgroundUrl})`,
  } as const;
});

// Actualiza el tipo para incluir 'quiz'
type ChallengeId = 'trust' | 'chat' | 'hunt' | 'quiz';

const start = (id: ChallengeId) => {
  const map: Record<ChallengeId, string> = {
    trust: '¿Confías o no?',
    chat: 'El chat sospechoso',
    hunt: 'Caza el engaño',
    quiz: 'Quiz de Amenazas', // Agregado
  };

  console.log(`Iniciando lógica real para: ${map[id]}`);

  // AQUÍ ES DONDE OCURRE LA MAGIA:
  if (id === 'quiz') {
    // redirigir a la página de quizzes que creamos
    router.push('/challenges/quiz');
  } else {
    alert(`¡Iniciando el desafío: ${map[id]}! (Aquí va la lógica real)`);
  }
}
</script>

<style scoped>
.challenges-page {
  min-height: 100vh;
  width: 100%;
  overflow-x: hidden;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  background-color: #1f1b3a;
  display: flex;
  flex-direction: column;
}

.overlay {
  flex: 1;
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
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: clamp(10px, 2vh, 16px);
  padding: clamp(12px, 3vh, 20px) clamp(12px, 4vw, 24px);
  max-width: 1300px;
  width: 100%;
  margin: 0 auto;
}

.grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: clamp(10px, 2vw, 18px);
}

@media (max-width: 1200px) {
  .grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: clamp(8px, 2vw, 16px);
  }
}

@media (max-width: 640px) {
  .grid {
    grid-template-columns: 1fr;
    gap: clamp(10px, 3vw, 14px);
  }

  .content {
    padding: clamp(10px, 3vh, 16px) clamp(10px, 3.5vw, 16px);
    gap: clamp(8px, 2vh, 14px);
  }
}

.hint {
  flex: 0 0 auto;
}

.hint-card {
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(255, 255, 255, 0.65);
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.22);
  padding: clamp(10px, 2.5vh, 16px) clamp(12px, 3vw, 20px);
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
  font-size: clamp(0.7rem, 2vw, 0.85rem);
}

.hint-text {
  margin: 0;
  font-weight: 850;
  color: #334155;
  font-size: clamp(0.85rem, 2.5vw, 1.05rem);
  line-height: 1.3;
}

@media (max-width: 640px) {
  .hint-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
    padding: clamp(10px, 3vh, 14px) clamp(10px, 3vw, 14px);
  }

  .hint-title {
    font-size: clamp(0.65rem, 2.5vw, 0.75rem);
  }

  .hint-text {
    font-size: clamp(0.8rem, 2vw, 0.95rem);
  }
}
</style>
