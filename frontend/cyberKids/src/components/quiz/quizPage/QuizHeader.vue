<template>
  <header class="quiz-navbar">
    <div class="navbar-brand">
      <div class="brand-icon-wrapper">
        <slot name="icon">
          <span class="brand-emoji">🔒</span>
        </slot>
      </div>

      <div class="brand-content">
        <h1 class="brand-title">{{ quizTitle }}</h1>
        
        <div class="progress-container">
          <div class="progress-labels">
            <span class="label-step">Pregunta {{ currentQuestion }} de {{ totalQuestions }}</span>
            <span class="label-percentage">{{ progressPercentage }}%</span>
          </div>
          <div class="progress-track">
            <div 
              class="progress-fill" 
              :style="{ width: `${progressPercentage}%` }"
              role="progressbar"
              :aria-valuenow="progressPercentage"
              aria-valuemin="0"
              aria-valuemax="100"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <div class="navbar-actions">
      <slot name="actions" />
    </div>
  </header>
</template>

<script setup lang="ts">
const props = withDefaults(defineProps<{
  quizTitle?: string;
  currentQuestion?: number;
  totalQuestions?: number;
  progressPercentage?: number;
}>(), {
  quizTitle: 'Quiz de Ciberseguridad',
  currentQuestion: 1,
  totalQuestions: 10,
  progressPercentage: 0
});
</script>

<style scoped>
/* Contenedor Principal */
.quiz-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.95);
  padding: 1rem 1.5rem;
  border-radius: 1.25rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(10px);
  gap: 1.5rem;
  width: 100%;
  box-sizing: border-box;
}

/* Sección Izquierda: Icono + Texto */
.navbar-brand {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.brand-icon-wrapper {
  width: 52px;
  height: 52px;
  min-width: 52px;
  background: var(--primary, #ffd166);
  border-radius: 14px;
  display: grid;
  place-items: center;
  font-size: 1.75rem;
  box-shadow: 0 4px 0 rgba(0,0,0,0.05);
}

.brand-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  width: 100%;
}

.brand-title {
  margin: 0;
  font-family: 'Fredoka', sans-serif;
  font-size: 2.25rem;
  font-weight: 800;
  color: #1e4b66;
  white-space: nowrap;
}

/* Barra de Progreso */
.progress-container {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  max-width: 300px; /* Ancho máximo en escritorio */
  width: 100%;
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  font-family: 'Fredoka', sans-serif;
  font-weight: 700;
  font-size: 0.8rem;
  color: rgba(30, 75, 102, 0.6);
}

.progress-track {
  height: 10px;
  background: rgba(30, 75, 102, 0.08);
  border-radius: 99px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #7be8c3, #6ecff5);
  border-radius: 99px;
  transition: width 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

/* Sección Derecha */
.navbar-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

/* --- RESPONSIVIDAD --- */

@media (max-width: 768px) {
  .quiz-navbar {
    padding: 1rem;
  }
  
  .brand-title {
    font-size: 1.1rem;
  }

  .progress-container {
    max-width: 200px;
  }
}

@media (max-width: 580px) {
  .quiz-navbar {
    flex-direction: column; /* Apilado vertical */
    align-items: stretch;
    gap: 1rem;
  }

  .navbar-brand {
    width: 100%;
  }

  .progress-container {
    max-width: 100%; /* Ocupa todo el ancho en móvil */
  }

  .navbar-actions {
    justify-content: flex-end;
    border-top: 1px solid rgba(0,0,0,0.05);
    padding-top: 0.75rem;
  }
}
</style>