<script setup lang="ts">
import { useRouter } from 'vue-router'
import { computed, onMounted, ref } from 'vue'
import { useQuizProgress } from '@/composables/useQuizProgress'

const { hasProgress } = useQuizProgress()

const emojiMap: Record<string, string> = {
  'phishing': '🎣',
  'password': '🔑',
  'passwords': '🔑',
  'share': '🌐',
  'devices': '📱',
  'volunteer_activism': '🛡️',
  'privacy': '🔐',
  'grooming': '⚠️',
  'cyberbullying': '😢',
  'general': '🚀'
};

const props = defineProps<{ quiz: {
  id: number;
  title: string;
  description?: string;
  difficulty?: number;
  base_points?: number;
  category?: string;
  segment?: string;
  image_url?: string | null;
  progress?: { answered?: number; total?: number; percentage?: number };
  status?: string;
} }>();

const router = useRouter();
const isInProgress = ref(false)

onMounted(() => {
  // Verificar si hay progreso guardado localmente
  isInProgress.value = hasProgress(props.quiz.id)
})

// Derivar datos para compatibilidad con template
const icon = computed(() => {
  const category = (props.quiz.category || 'general').toLowerCase();
  return emojiMap[category] || '🚀';
});

const stars = computed(() => {
  // Derivar estrellas basadas en difficulty (1-5)
  return (props.quiz.difficulty ?? 3) / 1.5; // Escalar de 1-5 a 1-3.33
});

const color = computed(() => {
  const difficulty = props.quiz.difficulty ?? 3;
  if (difficulty <= 1) return 'easy';
  if (difficulty <= 2) return 'normal';
  if (difficulty <= 3) return 'hard';
  return 'very-hard';
});

const displayStatus = computed(() => {
  // Priorizar el estado local de progreso
  if (isInProgress.value) return 'in_progress'
  return props.quiz.status
})

function goToDetail() {
  router.push(`/challenge/quiz/${props.quiz.id}`);
}
</script>

<template>
  <article class="quiz-card group" @click="goToDetail">
    <!-- Estado del Quiz -->
    <div v-if="displayStatus === 'completed'" class="card-badge completed">
      <span class="badge-icon">✓</span> REALIZADO
    </div>
    <div v-else-if="displayStatus === 'in_progress'" class="card-badge in-progress">
      <span class="badge-icon">⏸</span> EN PROGRESO
    </div>
    <div v-else-if="displayStatus === 'not_started'" class="card-badge not-started">
      <span class="badge-icon">○</span> NO INICIADO
    </div>
    
    <div :class="['card-deco', color]"></div>

    <div class="card-content">
      <!-- Imagen -->
      <div v-if="quiz.image_url" class="image-box">
        <img :src="quiz.image_url" alt="quiz image" class="quiz-image" />
      </div>

      <div v-else :class="['placeholder-image', color]">
        <img src="https://static.vecteezy.com/system/resources/previews/006/980/868/non_2x/cartoon-character-of-children-playing-with-their-pets-free-vector.jpg" alt="quiz image" class="quiz-image" />
      </div>
    
      <!-- Título y descripción -->
      <div class="text-content">
        <h3 class="card-title">
          {{ quiz.title }} 
          <span class="emoji">{{ icon }}</span>
        </h3>
        <p class="card-desc">{{ quiz.description ?? 'Quiz de ciberseguridad' }}</p>
      </div>

      <!-- Barra de progreso (respondidas / total) -->
      <div class="progress-section">
        <div class="progress-header">
          <span class="progress-label">Progreso</span>
          <span class="progress-value">{{ quiz.progress?.percentage ?? 0 }}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: (quiz.progress?.percentage ?? 0) + '%' }"></div>
        </div>
        <div class="progress-stats">
          <span class="stat">{{ quiz.progress?.answered ?? 0 }}/{{ quiz.progress?.total ?? 0 }} respondidas</span>
        </div>
      </div>

      <!-- Footer -->
      <div class="card-footer">
        <div class="meta-info">
          <div class="stars">
            <span v-for="(_, i) in Math.floor(stars)" :key="`filled-${i}`" class="material-icons-round star-filled">star</span>
            <span v-if="stars % 1 !== 0" class="material-icons-round star-filled">star_half</span>
            <span v-for="(_, i) in (3 - Math.ceil(stars))" :key="`empty-${i}`" class="material-icons-round star-empty">star_border</span>
          </div>
          <span class="difficulty-label">Nivel {{ quiz.difficulty ?? 3 }}</span>
        </div>

        <button :class="['play-btn', color]" @click.stop="goToDetail">
          <span class="play-icon">▶️</span>
          <span class="play-text">Jugar</span>
        </button>
      </div>
    </div>
  </article>
</template>

<style scoped>
/* FUENTES */
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@600;700&family=Plus+Jakarta+Sans:wght@500;700;800&display=swap');

.quiz-card {
  background: white;
  border-radius: 2rem; /* 32px */
  padding: 1.5rem;
  box-shadow: 0 10px 40px -10px rgba(0,0,0,0.1);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  border-bottom: 4px solid rgba(0,0,0,0.05);
  height: 100%;
}

.quiz-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
}

/* DECORACIÓN FONDO */
.card-deco {
  position: absolute;
  right: -1.5rem;
  top: -1.5rem;
  width: 8rem;
  height: 8rem;
  border-radius: 9999px;
  opacity: 0.1;
  transition: transform 0.5s ease;
}
.quiz-card:hover .card-deco { transform: scale(1.5); }

/* BADGE */
.card-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  backdrop-filter: blur(10px);
}

.card-badge.completed {
  background: rgba(76, 175, 80, 0.95);
  color: white;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.card-badge.in-progress {
  background: rgba(255, 152, 0, 0.95);
  color: white;
  border: 1px solid rgba(255, 152, 0, 0.3);
}

.card-badge.not-started {
  background: rgba(160, 174, 192, 0.95);
  color: white;
  border: 1px solid rgba(160, 174, 192, 0.3);
}

.card-badge.in-progress {
  background: rgba(139, 124, 255, 0.95);
  color: white;
  border: 1px solid rgba(139, 124, 255, 0.3);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
}

.badge-icon {
  font-size: 1rem;
}

/* BARRA DE PROGRESO */
.progress-section {
  background: rgba(139, 124, 255, 0.05);
  padding: 0.75rem;
  border-radius: 1rem;
  margin: 0.5rem 0;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.progress-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: rgba(30, 75, 102, 0.6);
  text-transform: uppercase;
}

.progress-value {
  font-size: 0.9rem;
  font-weight: 800;
  color: #8b7cff;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(30, 75, 102, 0.1);
  border-radius: 9999px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8b7cff 0%, #6ecff5 100%);
  border-radius: 9999px;
  transition: width 0.5s ease;
}

.progress-stats {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  font-weight: 600;
  color: rgba(30, 75, 102, 0.7);
}

.stat {
  display: flex;
  align-items: center;
}


/* CONTENIDO */
.card-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 1rem;
}

.icon-box {
  width: 4rem;
  height: 4rem;
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.icon-box .material-icons-round { font-size: 2.25rem; }

.image-box { width: 4rem; height: 4rem; border-radius: 1rem; overflow: hidden; display:flex; align-items:center; justify-content:center; }
.quiz-image { width: 100%; height: 100%; object-fit: cover; display: block; }

.text-content { flex-grow: 1; }

.card-title {
  font-family: 'Fredoka', sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  color: #1E4B66;
  margin-bottom: 0.5rem;
  line-height: 1.2;
}

.card-desc {
  color: rgba(30, 75, 102, 0.6);
  font-size: 0.875rem;
  font-weight: 500;
  line-height: 1.5;
}

/* FOOTER */
.card-footer {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.meta-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stars {
  display: flex;
  color: #fbbf24;
}
.stars .material-icons-round { font-size: 1.25rem; }

.difficulty-label {
  font-size: 0.75rem;
  font-weight: 800;
  color: rgba(30, 75, 102, 0.4);
  text-transform: uppercase;
}

/* BOTÓN (Adaptado del HTML con shadow-button) */
.play-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border-radius: 0.75rem;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  color: white;
  box-shadow: 0 4px 0px 0px rgba(0,0,0,0.1);
}

.play-btn:active {
  transform: translateY(2px);
  box-shadow: 0 0px 0px 0px rgba(0,0,0,0.1);
}

/* VARIANTES DE COLOR (Igual que el HTML) */
.coral { background-color: #FF7A7A; }
.coral.icon-box, .coral.card-deco { background-color: rgba(255, 122, 122, 0.1); color: #FF7A7A; }
.coral.play-btn:hover { background-color: #ff8e8e; }

.mint { background-color: #14b8a6; }
.mint.icon-box, .mint.card-deco { background-color: rgba(20, 184, 166, 0.1); color: #14b8a6; }
.mint.play-btn:hover { background-color: #2dd4bf; }

.purple-accent { background-color: #8B7CFF; }
.purple-accent.icon-box, .purple-accent.card-deco { background-color: rgba(139, 124, 255, 0.1); color: #8B7CFF; }
.purple-accent.play-btn:hover { background-color: #a396ff; }

.primary { background-color: #ffd166; color: #1E4B66 !important; }
.primary.icon-box, .primary.card-deco { background-color: rgba(255, 209, 102, 0.2); color: #d97706; }
.primary.play-btn:hover { background-color: #ffdb85; }

.sky-blue { background-color: #6ECFF5; }
.sky-blue.icon-box, .sky-blue.card-deco { background-color: rgba(110, 207, 245, 0.1); color: #0284c7; }
.sky-blue.play-btn:hover { background-color: #89d9f7; }

/* RESPONSIVE */
@media (max-width: 640px) {
  .quiz-card { padding: 1.25rem; }
  .play-text { font-size: 0.9rem; }
}
</style>