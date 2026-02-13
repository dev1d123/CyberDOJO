<template>
  <div class="modal-victory-overlay">
    <div class="modal-victory-content">
      <!-- Cabecera con animación confeti -->
      <div class="victory-header">
        <div class="confetti"></div>
        <h1 class="victory-title" :class="{ defeat: isDefeat }">{{ titleText }}</h1>
        <p class="victory-subtitle">{{ subtitleText }}</p>
      </div>

      <!-- Estadísticas -->
      <div class="stats-container">
        <div class="stat-item correct">
          <div class="stat-icon">✓</div>
          <div class="stat-content">
            <div class="stat-label">Respuestas Correctas</div>
            <div class="stat-value">{{ totalCorrect }}/{{ totalQuestions }}</div>
          </div>
        </div>

        <div class="stat-item percentage">
          <div class="stat-icon">📊</div>
          <div class="stat-content">
            <div class="stat-label">Porcentaje</div>
            <div class="stat-value">{{ percentage }}%</div>
          </div>
        </div>
      </div>

      <!-- Recompensas -->
      <div class="rewards-container">
        <div class="reward-item coins">
          <div class="reward-icon">🪙</div>
          <div class="reward-content">
            <div class="reward-label">Monedas Ganadas</div>
            <div class="reward-value">+{{ coinsEarned }}</div>
          </div>
        </div>

        <div class="reward-item points">
          <div class="reward-icon">⭐</div>
          <div class="reward-content">
            <div class="reward-label">Puntos</div>
            <div class="reward-value">+{{ pointsEarned }}</div>
          </div>
        </div>
      </div>

      <!-- Barra de progreso visual -->
      <div class="progress-visual">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: percentage + '%' }"></div>
        </div>
        <div class="progress-text">{{ percentage }}% Completado</div>
      </div>

      <!-- Acciones -->
      <div class="actions-container">
        <button class="btn-retry" @click="$emit('onRetry')">
          🔄 Intentar de Nuevo
        </button>
        <button class="btn-back" @click="$emit('onBack')">
          🏠 Volver a Misiones
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">

interface Props {
  quizTitle: string;
  totalCorrect: number;
  totalQuestions: number;
  coinsEarned: number;
  pointsEarned: number;
  isDefeat?: boolean;
}

const props = defineProps<Props>()

defineEmits<{
  onRetry: [];
  onBack: [];
}>()

const percentage = computed(() => {
  return props.totalQuestions > 0 
    ? Math.round((props.totalCorrect / props.totalQuestions) * 100)
    : 0
})

const titleText = computed(() => {
  return props.isDefeat ? '💪 Buen intento' : '🎉 ¡Felicidades! 🎉'
})

const subtitleText = computed(() => {
  return props.isDefeat
    ? 'No te rindas, puedes mejorar en el siguiente intento'
    : props.quizTitle
})
</script>

<style scoped>
.modal-victory-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(139, 124, 255, 0.1) 0%, rgba(106, 207, 245, 0.1) 100%);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-victory-content {
  background: white;
  border-radius: 24px;
  padding: 40px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
  overflow: hidden;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(40px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.victory-header {
  text-align: center;
  margin-bottom: 30px;
  position: relative;
  z-index: 10;
}

.confetti {
  position: absolute;
  width: 100%;
  height: 200px;
  top: -50px;
  left: 0;
}

.victory-title {
  font-size: 2.2em;
  color: #1e4b66;
  margin: 0;
  font-weight: 900;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.victory-subtitle {
  font-size: 1.1em;
  color: #8b7cff;
  margin: 8px 0 0 0;
  font-weight: 700;
}

/* Estadísticas */
.stats-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.stat-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-radius: 14px;
  background: #f8f9ff;
}

.stat-item.correct {
  border: 2px solid #4caf50;
  background: rgba(76, 175, 80, 0.08);
}

.stat-item.percentage {
  border: 2px solid #2196F3;
  background: rgba(33, 150, 243, 0.08);
}

.stat-icon {
  font-size: 1.8em;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  border-radius: 10px;
  background: white;
}

.stat-item.correct .stat-icon {
  color: #4caf50;
}

.stat-item.percentage .stat-icon {
  color: #2196F3;
}

.stat-label {
  font-size: 0.85em;
  color: #666;
  font-weight: 600;
}

.stat-value {
  font-size: 1.4em;
  color: #1e4b66;
  font-weight: 900;
}

/* Recompensas */
.rewards-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 24px;
}

.reward-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-radius: 14px;
  border: 2px solid #e0e0e0;
}

.reward-item.coins {
  background: rgba(255, 193, 7, 0.08);
  border-color: #ffc107;
}

.reward-item.points {
  background: rgba(255, 152, 0, 0.08);
  border-color: #ff9800;
}

.reward-icon {
  font-size: 1.8em;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  border-radius: 10px;
  background: white;
}

.reward-label {
  font-size: 0.85em;
  color: #666;
  font-weight: 600;
}

.reward-value {
  font-size: 1.4em;
  color: #1e4b66;
  font-weight: 900;
}

/* Barra de progreso */
.progress-visual {
  margin-bottom: 24px;
}

.progress-bar {
  width: 100%;
  height: 12px;
  background: #e0e0e0;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4caf50 0%, #8bc34a 100%);
  transition: width 1s cubic-bezier(0.34, 1.56, 0.64, 1);
  border-radius: 10px;
}

.progress-text {
  text-align: center;
  font-size: 0.9em;
  color: #666;
  font-weight: 700;
}

/* Botones */
.actions-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.btn-retry,
.btn-back {
  padding: 14px 20px;
  border-radius: 12px;
  font-weight: 900;
  font-size: 1em;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.btn-retry {
  background: #8b7cff;
  color: white;
  box-shadow: 0 4px 12px rgba(139, 124, 255, 0.3);
}

.btn-retry:hover {
  background: #7a6ddd;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(139, 124, 255, 0.4);
}

.btn-retry:active {
  transform: translateY(0);
}

.btn-back {
  background: #1e4b66;
  color: white;
  box-shadow: 0 4px 12px rgba(30, 75, 102, 0.3);
}

.btn-back:hover {
  background: #153a50;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(30, 75, 102, 0.4);
}

.btn-back:active {
  transform: translateY(0);
}

@media (max-width: 600px) {
  .modal-victory-content {
    padding: 24px;
  }

  .victory-title {
    font-size: 1.8em;
  }

  .stats-container,
  .rewards-container {
    grid-template-columns: 1fr;
  }
}
</style>
