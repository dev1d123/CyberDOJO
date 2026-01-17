<template>
  <div class="history-page" :style="{ backgroundImage: `url(${historyBackgroundUrl})` }">
    <div class="history-overlay">
      <BackToDashboardButton />
      <header class="history-header">
        <h1 class="history-title">Modo Historia</h1>
        <p class="history-subtitle">Elige una isla para comenzar tu aventura</p>
      </header>

      <main class="history-map-area">
        <HistoryMap
          :levels="levels"
          :selected-level-id="selectedLevel?.id ?? null"
          :island-url="islandUrl"
          @select="selectLevel"
        />
      </main>

      <section class="info-panel">
        <div class="info-content">
          <template v-if="selectedLevel">
            <div class="info-text">
              <h2 class="info-title">Nivel {{ selectedLevel.id }} - {{ selectedLevel.name }}</h2>
              <p class="info-details">{{ selectedLevel.details }}</p>
            </div>

            <div class="info-scores">
              <div class="score-box">
                <span class="score-label">Puntaje actual</span>
                <span class="score-value">{{ selectedLevel.currentScore }}</span>
              </div>
              <div class="score-box">
                <span class="score-label">Puntaje total</span>
                <span class="score-value">{{ selectedLevel.totalScore }}</span>
              </div>
            </div>

            <button class="start-button" type="button" @click="startLevel">
              Acceder a este nivel
            </button>
          </template>

          <template v-else>
            <div class="info-text">
              <h2 class="info-title">Selecciona una isla</h2>
              <p class="info-details">Haz clic en cualquier isla para ver sus detalles y puntajes.</p>
            </div>
          </template>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import BackToDashboardButton from '../components/BackToDashboardButton.vue';
import HistoryMap from '../components/history/HistoryMap.vue';
import type { HistoryLevelDto } from '../dto/history.dto';

const historyBackgroundUrl = new URL('../assets/images/historyBackground.png', import.meta.url).href;
const islandUrl = new URL('../assets/images/island.png', import.meta.url).href;

const levels: HistoryLevelDto[] = [
  { id: 1, name: 'Bienvenida', details: 'Aprende lo básico para comenzar tu entrenamiento.', currentScore: 120, totalScore: 200, x: '8%', y: '86%' },
  { id: 2, name: 'Contraseñas', details: 'Crea contraseñas fuertes y seguras.', currentScore: 60, totalScore: 180, x: '26%', y: '72%' },
  { id: 3, name: 'Phishing', details: 'Identifica mensajes y enlaces sospechosos.', currentScore: 0, totalScore: 220, x: '12%', y: '52%' },
  { id: 4, name: 'Privacidad', details: 'Configura tu privacidad en internet.', currentScore: 0, totalScore: 240, x: '34%', y: '34%' },
  { id: 5, name: 'Redes Sociales', details: 'Publica con cuidado y protege tu información.', currentScore: 0, totalScore: 260, x: '56%', y: '50%' },
  { id: 6, name: 'Dispositivos', details: 'Mantén tus dispositivos protegidos y actualizados.', currentScore: 0, totalScore: 280, x: '76%', y: '30%' },
  { id: 7, name: 'Ciberacoso', details: 'Aprende cómo actuar ante situaciones peligrosas.', currentScore: 0, totalScore: 300, x: '92%', y: '58%' },
  { id: 8, name: 'Final', details: 'Demuestra todo lo aprendido en el reto final.', currentScore: 0, totalScore: 350, x: '68%', y: '84%' },
];

const selectedLevel = ref<HistoryLevelDto | null>(null);

const selectLevel = (level: HistoryLevelDto) => {
  selectedLevel.value = level;
};

const startLevel = () => {
  if (!selectedLevel.value) return;
  alert(`Acceder a Nivel ${selectedLevel.value.id} - ${selectedLevel.value.name}`);
};
</script>

<style scoped>
.history-page {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

.history-overlay {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  background: rgba(0, 0, 0, 0.25);
}

.history-header {
  padding: clamp(12px, 2.5vh, 22px) clamp(12px, 2.5vw, 24px);
  text-align: center;
}

.history-title {
  margin: 0;
  color: white;
  font-size: clamp(1.8rem, 3.2vw, 3rem);
  text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.35);
}

.history-subtitle {
  margin: 6px 0 0 0;
  color: rgba(255, 255, 255, 0.9);
  font-size: clamp(1rem, 1.4vw, 1.2rem);
}

.history-map-area {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 clamp(10px, 2vw, 22px);
}

.info-panel {
  flex: 0 0 auto;
  padding: clamp(10px, 2vh, 18px) clamp(12px, 2.5vw, 24px);
}

.info-content {
  max-width: 1200px;
  margin: 0 auto;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.28);
  padding: clamp(12px, 2vh, 18px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.info-text {
  min-width: 0;
}

.info-title {
  margin: 0;
  color: #2c3e50;
  font-size: clamp(1.2rem, 1.8vw, 1.6rem);
}

.info-details {
  margin: 6px 0 0 0;
  color: #555;
  font-size: clamp(0.95rem, 1.2vw, 1.05rem);
}

.info-scores {
  display: flex;
  gap: 12px;
  flex: 0 0 auto;
}

.score-box {
  background: rgba(102, 126, 234, 0.12);
  border: 2px solid rgba(102, 126, 234, 0.35);
  border-radius: 18px;
  padding: 10px 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 140px;
}

.score-label {
  color: #667eea;
  font-weight: 800;
  font-size: 0.95rem;
}

.score-value {
  color: #2c3e50;
  font-weight: 900;
  font-size: 1.4rem;
}

.start-button {
  flex: 0 0 auto;
  background: linear-gradient(135deg, #48c6ef 0%, #6f86d6 100%);
  color: white;
  border: none;
  padding: 0.9rem 1.4rem;
  border-radius: 18px;
  font-size: 1.1rem;
  font-weight: 900;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 10px 24px rgba(72, 198, 239, 0.35);
}

.start-button:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 14px 30px rgba(72, 198, 239, 0.5);
}

@media (max-width: 900px) {
  .info-content {
    flex-direction: column;
    align-items: stretch;
  }

  .info-scores {
    justify-content: center;
  }

  .start-button {
    width: 100%;
  }
}
</style>
