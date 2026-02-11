<template>
  <div class="feedback-overlay">
    <div class="feedback-modal">
      <button class="close-button" @click="$emit('onClose')" aria-label="Cerrar"></button>

      <aside class="mascot-panel">
        <div class="mascot-glow-effect"></div>
        <div class="mascot-image-container">
          <img :src="mascotUrl" alt="Mascota" class="mascot-animated" />
        </div>
        <div class="panel-text">
          <h2 class="feedback-title">¡Repasemos!</h2>
          <p class="feedback-subtitle">
            {{ resultMessage }}
          </p>
        </div>
      </aside>

      <main class="explanations-panel">
        <div class="explanations-scroll">
          <article
            v-for="(option, index) in feedbackOptions"
            :key="index"
            :class="[
              'explanation-card',
              option.isCorrect ? 'style-correct' : 'style-incorrect',
              { 'is-selected': index === userSelectedIndex }
            ]"
          >
            <div v-if="option.isCorrect" class="watermark-icon">check_circle</div>

            <div class="option-letter">
              {{ customLabels[index] ?? String.fromCharCode(65 + index) }}
            </div>

            <div class="option-content">
              <div class="option-header">
                <h3 class="option-title">{{ option.title }}</h3>
                <span v-if="option.isCorrect" class="correct-badge">Correcto</span>
              </div>
              <p class="option-description">{{ option.description }}</p>
            </div>
          </article>
        </div>

        <footer class="panel-footer">
          <button class="continue-button" @click="$emit('onContinue')">
            <span>Continuar</span>
            <span class="material-icon">arrow_forward_ios</span>
          </button>
        </footer>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface FeedbackOption {
  title: string;
  description: string;
  isCorrect?: boolean;
}

const props = withDefaults(defineProps<{
  feedbackOptions?: FeedbackOption[];
  userSelectedIndex?: number;
  customLabels?: string[];
  mascotUrl?: string;
}>(), {
  feedbackOptions: () => [
    { title: 'Opción no definida', description: 'No se proporcionó una explicación para esta respuesta.', isCorrect: true }
  ],
  userSelectedIndex: -1,
  customLabels: () => [],
  mascotUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCucjZBT2oZoN5rGKrDGU5Q9yq3f9tkghZGt5pjgZLPnrwZPlzx51O5syvPmrxMw9uR7djGOJodI2-z0YPaCfHQMw8Ptu-RD5shLTsY9mm4lR7j1f0ylbyId7-YVTjGo_C00NHByKcMLcxMhQZqC7cqy3Qlvk6uMEpeyHCm4fD222J3HgreRPI4Eyoy5VCcht_IBGGT3vlzJtXKNwqYmc0LV9CFCGOkMfrKcUg7HYnu6DL_JlavvApLhf_4xDZMGi-E0UmCJOuZ_gZ5'
});

const emit = defineEmits(['onClose', 'onContinue']);

// Mensaje dinámico basado en si acertó o no
const resultMessage = computed(() => {
  const correctIdx = props.feedbackOptions.findIndex(o => o.isCorrect);
  if (props.userSelectedIndex === -1) return 'Mira los detalles de esta pregunta.';
  return props.userSelectedIndex === correctIdx 
    ? '¡Excelente elección! Mira por qué es correcta.' 
    : `Mira por qué la opción ${String.fromCharCode(65 + correctIdx)} era la correcta.`;
});
</script>

<style scoped>
/* Variables según paleta de referencia */
:host {
  --primary: #ffd166;
  --deep-sea: #1e4b66;
  --mint: #7be8c3;
  --coral: #ff7a7a;
  --font-fredoka: 'Fredoka', sans-serif;
  --font-nunito: 'Nunito', sans-serif;
}

.feedback-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: rgba(30, 75, 102, 0.4);
  backdrop-filter: blur(8px);
  animation: fadeIn 0.3s ease-out;
}

.feedback-modal {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  width: 100%;
  max-width: 1152px; /* max-6xl */
  max-height: 90vh;
  border-radius: 2.5rem;
  border: 4px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: row;
  position: relative;
  /* allow decorative elements (like the close button) to protrude outside */
  overflow: visible;
  animation: popIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

/* --- PANEL IZQUIERDO --- */
.mascot-panel {
  width: 33.333%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2.5rem;
  position: relative;
  flex-shrink: 0;
}

.mascot-glow-effect {
  position: absolute;
  width: 80%;
  height: 60%;
  background: var(--primary);
  opacity: 0.2;
  filter: blur(60px);
  border-radius: 9999px;
  transform: translateY(20px);
}

.mascot-image-container {
  position: relative;
  width: 100%;
  max-width: 256px;
  aspect-ratio: 1;
}

.mascot-animated {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 10px 15px rgba(0,0,0,0.1));
  animation: float 4s ease-in-out infinite;
}

.panel-text {
  text-align: center;
  margin-top: 1.5rem;
  position: relative;
  z-index: 10;
}

.feedback-title {
  font-family: 'Fredoka', sans-serif;
  font-size: 2rem;
  font-weight: 700;
  color: #1e4b66;
  margin: 0 0 0.5rem 0;
}

.feedback-subtitle {
  font-family: 'Nunito', sans-serif;
  font-size: 1.125rem;
  font-weight: 600;
  color: rgba(30, 75, 102, 0.7);
  line-height: 1.25;
}

/* --- PANEL DERECHO --- */
.explanations-panel {
  width: 66.666%;
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
  height: auto;
  overflow: hidden;
}

.explanations-scroll {
  flex: 1;
  overflow-y: auto;
  padding-right: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.explanation-card {
  position: relative;
  display: flex;
  gap: 1rem;
  padding: 1.25rem;
  border-radius: 0.75rem;
  border-left: 8px solid;
  transition: all 0.2s ease;
  overflow: hidden;
}

/* Estilo Correcto */
.style-correct {
  background: rgba(123, 232, 195, 0.2); /* mint/20 */
  border-color: #7be8c3;
}

.style-correct.is-selected {
  ring: 2px solid rgba(123, 232, 195, 0.5);
}

/* Estilo Incorrecto */
.style-incorrect {
  background: rgba(255, 122, 122, 0.1); /* coral/10 */
  border-color: #ff7a7a;
}

.style-incorrect:hover {
  background: rgba(255, 122, 122, 0.2);
}

/* Marca de agua (Icono check) */
.watermark-icon {
  position: absolute;
  top: 0;
  right: 0;
  padding: 1rem;
  font-family: 'Material Icons Round';
  font-size: 4rem;
  color: #7be8c3;
  opacity: 0.15;
  pointer-events: none;
}

.option-letter {
  width: 2.5rem;
  height: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.5rem;
  font-family: 'Fredoka', sans-serif;
  font-weight: 700;
  font-size: 1.25rem;
  flex-shrink: 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.style-correct .option-letter { background: #7be8c3; color: #1e4b66; }
.style-incorrect .option-letter { background: #ff7a7a; color: white; }

.option-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  position: relative;
  z-index: 1;
}

.option-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.option-title {
  margin: 0;
  font-family: 'Fredoka', sans-serif;
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e4b66;
}

.style-incorrect .option-title { color: #ff7a7a; }

.correct-badge {
  background: #7be8c3;
  color: #1e4b66;
  font-size: 0.7rem;
  font-weight: 800;
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.option-description {
  margin: 0;
  font-family: 'Nunito', sans-serif;
  font-size: 1rem;
  font-weight: 700;
  color: rgba(30, 75, 102, 0.8);
  line-height: 1.4;
}

/* --- FOOTER Y BOTONES --- */
.panel-footer {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(0,0,0,0.05);
  display: flex;
  justify-content: flex-end;
}

.continue-button {
  background: #ffd166;
  color: #1e4b66;
  border: none;
  font-family: 'Fredoka', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  padding: 0.75rem 2.5rem;
  border-radius: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 6px 0px 0px rgba(0, 0, 0, 0.1);
  transition: all 0.2s;
}

.continue-button:hover {
  background: #ffc640;
  transform: scale(1.02);
}

.continue-button:active {
  transform: translateY(6px);
  box-shadow: none;
}

.material-icon {
  font-family: 'Material Icons Round';
  font-size: 1.5rem;
}

.close-button {
  position: absolute;
  top: -1.25rem;
  right: -1.25rem;
  background: rgb(202, 18, 18);
  border: none;
  font-size: 1.5rem;
  color: #ffffff;
  cursor: pointer;
  opacity: 0.95;
  z-index: 999;
  width:44px;
  height:44px;
  display:grid;
  place-items:center;
  border-radius:999px;
  box-shadow:0 8px 20px rgba(0,0,0,0.18);  

}

.close-button::before,
.close-button::after{
  content:'';
  position:absolute;
  width:18px;
  height:2.6px;
  background:#fff;
  left:50%;
  top:50%;
  transform-origin:center;
  border-radius:2px;
}
.close-button::before{ transform: translate(-50%,-50%) rotate(45deg);} 
.close-button::after{ transform: translate(-50%,-50%) rotate(-45deg);} 

.close-button:hover { opacity: 1; }

/* --- ANIMACIONES --- */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}

@keyframes popIn {
  0% { opacity: 0; transform: scale(0.8); }
  100% { opacity: 1; transform: scale(1); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* --- RESPONSIVIDAD --- */
@media (max-width: 900px) {
  .feedback-modal {
    flex-direction: column;
    max-height: 95vh;
  }
  .mascot-panel {
    width: 100%;
    padding: 1.5rem;
  }
  .mascot-image-container {
    width: 120px;
  }
  .explanations-panel {
    width: 100%;
    padding: 1.5rem;
  }
  .feedback-title { font-size: 1.5rem; }
  .continue-button { width: 100%; justify-content: center; }
}

/* Scrollbar personalizada */
.explanations-scroll::-webkit-scrollbar { width: 6px; }
.explanations-scroll::-webkit-scrollbar-track { background: transparent; }
.explanations-scroll::-webkit-scrollbar-thumb {
  background: rgba(30, 75, 102, 0.2);
  border-radius: 10px;
}
</style>