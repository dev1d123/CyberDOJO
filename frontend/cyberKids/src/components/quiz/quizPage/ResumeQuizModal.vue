<template>
  <div class="modal-overlay" @click.self="$emit('cancel')">
    <div class="resume-modal">
      <div class="modal-icon">🔄</div>
      
      <h2 class="modal-title">Quiz sin Terminar</h2>
      
      <p class="modal-message">
        Saliste antes de completar este quiz. ¿Quieres intentarlo de nuevo?
      </p>
      
      <div class="progress-info">
        <div class="info-item">
          <span class="info-icon">📝</span>
          <span class="info-text">
            Última vez respondiste <strong>{{ answeredQuestions }}</strong> de <strong>{{ totalQuestions }}</strong> preguntas
          </span>
        </div>
        
        <div class="info-item">
          <span class="info-icon">🕐</span>
          <span class="info-text">
            Últ activity: <strong>{{ lastUpdated }}</strong>
          </span>
        </div>
      </div>

      <div class="modal-actions">
        <button class="btn btn-resume" @click="$emit('resume')">
          <span class="btn-icon">▶️</span>
          Intentar de nuevo
        </button>
        
        <button class="btn btn-restart" @click="$emit('cancel')">
          <span class="btn-icon">✕</span>
          Volver atrás
        </button>
      </div>

      <button class="btn-close" @click="$emit('cancel')">
        <span>✕</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  answeredQuestions: number
  totalQuestions: number
  totalPoints: number
  lastUpdatedAt: string
}>()

defineEmits<{
  resume: []
  restart: []
  cancel: []
}>()

const lastUpdated = computed(() => {
  try {
    const date = new Date(props.lastUpdatedAt)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 1) return 'hace un momento'
    if (diffMins < 60) return `hace ${diffMins} minuto${diffMins > 1 ? 's' : ''}`
    
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `hace ${diffHours} hora${diffHours > 1 ? 's' : ''}`
    
    const diffDays = Math.floor(diffHours / 24)
    return `hace ${diffDays} día${diffDays > 1 ? 's' : ''}`
  } catch {
    return 'recientemente'
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.resume-modal {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 24px;
  padding: 2.5rem;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  position: relative;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-icon {
  font-size: 4rem;
  text-align: center;
  margin-bottom: 1rem;
  animation: rotate 2s ease-in-out infinite;
}

@keyframes rotate {
  0%, 100% {
    transform: rotate(0deg);
  }
  50% {
    transform: rotate(180deg);
  }
}

.modal-title {
  font-size: 2rem;
  font-weight: 800;
  color: white;
  text-align: center;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.modal-message {
  color: rgba(255, 255, 255, 0.95);
  text-align: center;
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.progress-info {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: white;
  margin-bottom: 1rem;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.info-text {
  font-size: 1rem;
  line-height: 1.4;
}

.info-text strong {
  font-weight: 700;
}

.modal-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.btn {
  padding: 1rem 1.5rem;
  border: none;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
}

.btn:active {
  transform: translateY(0);
}

.btn-resume {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  color: white;
}

.btn-resume:hover {
  background: linear-gradient(135deg, #0e877a 0%, #2fd66c 100%);
}

.btn-restart {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.4);
}

.btn-restart:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.6);
}

.btn-icon {
  font-size: 1.2rem;
}

.btn-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

@media (max-width: 640px) {
  .resume-modal {
    padding: 2rem;
    width: 95%;
  }

  .modal-title {
    font-size: 1.5rem;
  }

  .modal-message {
    font-size: 1rem;
  }

  .btn {
    font-size: 1rem;
    padding: 0.875rem 1.25rem;
  }
}
</style>
