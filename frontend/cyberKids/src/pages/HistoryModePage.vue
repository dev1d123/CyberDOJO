<template>
  <div class="history-page" :style="{ backgroundImage: `url(${historyBackgroundUrl})` }">
    <div class="history-overlay">
      <BackToDashboardButton />
      <header class="history-header">
        <h1 class="history-title">Modo Historia</h1>
        <p class="history-subtitle">Elige una isla para comenzar tu aventura</p>
      </header>

      <main
        class="history-map-area"
        v-pet-hint="{ behavior: 'hover', vars: { target: 'el mapa: elige una isla para ver detalles' } }"
      >
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

            <button
              class="start-button"
              type="button"
              v-pet-hint="{ behavior: 'hover_button', vars: { target: 'acceder a este nivel' }, click: { behavior: 'open_page', vars: { target: 'la simulación' }, ttlMs: 1600, priority: 1 } }"
              @click="startLevel"
            >
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
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import BackToDashboardButton from '../components/BackToDashboardButton.vue';
import HistoryMap from '../components/history/HistoryMap.vue';
import type { HistoryLevelDto } from '../dto/history.dto';
import { SimulationService } from '../services/simulation.service';

const router = useRouter();

const historyBackgroundUrl = new URL('../assets/images/historyBackground.png', import.meta.url).href;
const islandUrl = new URL('../assets/images/island.png', import.meta.url).href;

const fallbackLevels: HistoryLevelDto[] = [
  { id: 1, name: 'Ingeniería Social', details: 'Detecta y resiste técnicas de manipulación en conversaciones.', currentScore: 60, totalScore: 180, x: '26%', y: '72%' },
  { id: 2, name: 'Suplantación Digital', details: 'Identifica ataques de phishing y enlaces maliciosos.', currentScore: 0, totalScore: 220, x: '12%', y: '52%' },
  { id: 3, name: 'Fuga de Datos', details: 'Protege información sensible en tus comunicaciones.', currentScore: 0, totalScore: 240, x: '34%', y: '34%' },
  { id: 4, name: 'Pretextos Falsos', details: 'Reconoce cuando alguien crea escenarios falsos para engañarte.', currentScore: 0, totalScore: 260, x: '56%', y: '50%' },
  { id: 5, name: 'Trampas Digitales', details: 'Evita caer en señuelos y ofertas demasiado buenas.', currentScore: 0, totalScore: 280, x: '76%', y: '30%' },
  { id: 6, name: 'Suplantación de Identidad', details: 'Verifica identidades y detecta impostores en línea.', currentScore: 0, totalScore: 300, x: '92%', y: '58%' },
];

const positionByScenarioId: Record<number, { x: string; y: string }> = {
  1: { x: '26%', y: '72%' },
  2: { x: '12%', y: '52%' },
  3: { x: '34%', y: '34%' },
  4: { x: '56%', y: '50%' },
  5: { x: '76%', y: '30%' },
  6: { x: '92%', y: '58%' },
};

const levels = ref<HistoryLevelDto[]>(fallbackLevels);

const selectedLevel = ref<HistoryLevelDto | null>(null);

onMounted(async () => {
  try {
    const scenarios = await SimulationService.getScenarios();
    if (scenarios.length === 0) return;

    levels.value = scenarios.map((s) => {
      const pos = positionByScenarioId[s.scenario_id] || { x: '50%', y: '50%' };
      return {
        id: s.scenario_id,
        name: s.name,
        details: s.description || 'Prepárate para enfrentar un escenario de ingeniería social.',
        currentScore: 0,
        totalScore: s.base_points || 0,
        x: pos.x,
        y: pos.y,
      };
    });
  } catch {
    // Fallback a hardcoded (evita romper la UI si la API falla)
    levels.value = fallbackLevels;
  }
});

const selectLevel = (level: HistoryLevelDto) => {
  selectedLevel.value = level;
};

const startLevel = () => {
  if (!selectedLevel.value) return;
  
  // Redirect to simulation page with scenario ID
  router.push(`/simulation/${selectedLevel.value.id}`);
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
