<script setup lang="ts">
import { useRouter } from 'vue-router'

const emojiMap: Record<string, string> = {
  'phishing': '🎣',
  'password': '🔑',
  'share': '🌐',
  'devices': '📱',
  'volunteer_activism': '🛡️'
};

const props = defineProps<{ quiz: {
  id: number;
  title: string;
  description: string;
  difficulty: string;
  icon: string;
  color?: string;
  stars: number;
  isNew?: boolean;
} }>();

const router = useRouter();

function slugify(text: string) {
  return text
    .toString()
    .toLowerCase()
    .normalize('NFKD')
    .replace(/\s+/g, '-') // Replace spaces with -
    .replace(/[^a-z0-9\-]/g, '') // Remove non-alphanumeric
    .replace(/-+/g, '-') // Collapse dashes
    .replace(/^-+|-+$/g, ''); // Trim dashes
}

function goToDetail() {
  const slug = slugify(props.quiz.title || `quiz-${props.quiz.id}`);
  router.push(`/challenge/quiz/${slug}`);
}
</script>

<template>
  <article class="quiz-card group" @click="goToDetail">
    <div class="card-badge" v-if="quiz.isNew">NUEVO</div>
    
    <div :class="['card-deco', quiz.color]"></div>

    <div class="card-content">
      <div :class="['icon-box', quiz.color]">
        <span class="material-icons-round">{{ quiz.icon }}</span>
      </div>

      <div class="text-content">
        <h3 class="card-title">
          {{ quiz.title }} 
          <span class="emoji">{{ emojiMap[quiz.icon] || '🚀' }}</span>
        </h3>
        <p class="card-desc">{{ quiz.description }}</p>
      </div>

      <div class="card-footer">
        <div class="meta-info">
          <div class="stars">
            <span v-for="(_, i) in Math.floor(quiz.stars)" :key="i" class="material-icons-round star-filled">star</span>
            <span v-if="quiz.stars % 1 !== 0" class="material-icons-round star-filled">star_half</span>
            <span v-for="(_, i) in (3 - Math.ceil(quiz.stars))" :key="i" class="material-icons-round star-empty">star_border</span>
          </div>
          <span class="difficulty-label">{{ quiz.difficulty }}</span>
        </div>

        <button :class="['play-btn', quiz.color]" @click.stop="goToDetail">
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
  background: #FF7A7A;
  color: white;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  z-index: 10;
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