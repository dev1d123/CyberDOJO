<template>
  <div class="quiz-page">
    <div class="floating-cloud cloud-1"></div>
    <div class="floating-cloud cloud-2"></div>
    <div class="floating-cloud cloud-3"></div>
    <div class="floating-cloud cloud-4"></div>

    <main class="main">
      <div class="back-container">
        <router-link to="/" class="back-btn">
          <span class="material-icons-round">arrow_back</span>
          <span>Regresar</span>
        </router-link>
      </div>

      <header class="page-header">
        <div class="controls-card">
          <div class="search-wrapper">
             <SearchBar v-model="search" :placeholder="searchPlaceholder" />
          </div>
          
          <div class="filters">
            <button 
              v-for="(f, index) in filters" 
              :key="f" 
              :class="['filter-btn', { 'active': index === 0 }]"
            >
              {{ f }}
            </button>
          </div>
        </div>

        <div class="mascot-section">
          <MascotWidget 
            :src="mascotSrc" 
            :title="header.title" 
            :subtitle="header.subtitle" 
          />
        </div>
      </header>

      <div class="list-grid">
        <QuizListItem v-for="quiz in quizzes" :key="quiz.id" :quiz="quiz" />

        <article class="coming-soon">
          <div class="coming-icon">
            <span class="material-icons-round">lock_clock</span>
          </div>
          <h3 class="coming-title">Próximamente</h3>
          <p class="coming-text">¡Nuevas misiones están siendo preparadas!</p>
        </article>
      </div>

      <div class="more-wrap">
        <button class="more-btn">
          Ver más misiones 
          <span class="material-icons-round">expand_more</span>
        </button>
      </div>
    </main>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import QuizListItem from '@/components/quiz/QuizListPage/QuizListItem.vue';
import SearchBar from '@/components/quiz/QuizListPage/SearchBar.vue';
import MascotWidget from '@/components/quiz/shared/MascotWidget.vue';

const mascotSrc = 'https://lh3.googleusercontent.com/aida-public/AB6AXuCucjZBT2oZoN5rGKrDGU5Q9yq3f9tkghZGt5pjgZLPnrwZPlzx51O5syvPmrxMw9uR7djGOJodI2-z0YPaCfHQMw8Ptu-RD5shLTsY9mm4lR7j1f0ylbyId7-YVTjGo_C00NHByKcMLcxMhQZqC7cqy3Qlvk6uMEpeyHCm4fD222J3HgreRPI4Eyoy5VCcht_IBGGT3vlzJtXKNwqYmc0LV9CFCGOkMfrKcUg7HYnu6DL_JlavvApLhf_4xDZMGi-E0UmCJOuZ_gZ5';

const header = {
  title: '¡Elige tu próxima misión! 🚀',
  subtitle: '¿Qué quieres aprender hoy?',
};

const search = ref('');
const searchPlaceholder = 'Buscar quiz...';

const filters = ['Todos', 'Phishing', 'Contraseñas', 'Privacidad'];

const quizzes = ref([
  {
    id: 1,
    title: 'Detectives del Phishing',
    description: 'Aprende a identificar correos falsos y trampas en internet.',
    difficulty: 'Fácil',
    icon: 'phishing',
    color: 'coral',
    stars: 1,
  },
  {
    id: 2,
    title: 'Claves Secretas',
    description: 'Crea contraseñas super seguras que ni los robots puedan adivinar.',
    difficulty: 'Medio',
    icon: 'password',
    color: 'mint',
    stars: 3,
  },
  {
    id: 3,
    title: 'Redes Seguras',
    description: '¿Qué compartir y qué no? Domina tu privacidad en redes.',
    difficulty: 'Medio',
    icon: 'share',
    color: 'purple-accent',
    stars: 2.5,
  },
  {
    id: 4,
    title: 'Guardián del Móvil',
    description: 'Protege tu tablet y celular de virus y apps maliciosas.',
    difficulty: 'Fácil',
    icon: 'devices',
    color: 'primary',
    stars: 1,
  },
  {
    id: 5,
    title: 'Héroes Digitales',
    description: 'Cómo actuar ante el ciberacoso y ayudar a tus amigos.',
    difficulty: 'Difícil',
    icon: 'volunteer_activism',
    color: 'sky-blue',
    stars: 3,
  },
]);
</script>
<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;500;700;800&display=swap');

/* Reset y Base */
.quiz-page {
  font-family: 'Plus Jakarta Sans', sans-serif;
  background: linear-gradient(135deg, #6ecff5 0%, #8b7cff 100%);
  min-height: 100vh;
  padding: 24px;
  position: relative;
  color: #1e4b66;
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow-x: hidden;
}

/* Nubes */
.floating-cloud { position: absolute; background: rgba(255, 255, 255, 0.4); border-radius: 999px; filter: blur(8px); z-index: 0; }
.cloud-1 { top: 10%; left: 5%; width: 200px; height: 80px; }
.cloud-2 { top: 25%; right: 10%; width: 150px; height: 60px; }
.cloud-3 { bottom: 15%; left: 20%; width: 300px; height: 100px; }
.cloud-4 { top: 60%; right: -5%; width: 250px; height: 90px; opacity: 0.3; }

.main {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 1280px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Botón Regresar */
.back-container { display: flex; justify-content: flex-start; }
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-weight: 700;
  border-radius: 12px;
  backdrop-filter: blur(4px);
  text-decoration: none;
  transition: background 0.2s;
}
.back-btn:hover { background: rgba(255, 255, 255, 0.3); }

/* Header y Controles */
.page-header { display: flex; flex-direction: column; gap: 24px; }

.controls-card {
  backdrop-filter: blur(8px);
  padding: 12px;
  border-radius: 1.5rem;
  box-shadow: 0 10px 40px -10px rgba(0,0,0,0.1);
  border: 1px solid rgba(255,255,255,0.5);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Filtros Estilo Pill */
.filters {
  display: flex;
  gap: 8px;
  justify-content: center;
  padding-bottom: 4px;
}
.filters::-webkit-scrollbar { display: none; }

.filter-btn {
  padding: 8px 24px;
  background: white;
  border-radius: 999px;
  font-weight: 700;
  color: #1e4b66;
  border: none;
  border-bottom: 4px solid #e5e7eb;
  transition: all 0.2s;
  white-space: nowrap;
  cursor: pointer;
}

.filter-btn.active {
  background: #ffd166;
  border-color: rgba(217, 119, 6, 0.2);
}

.filter-btn:hover:not(.active) { background: #f8f7f5; border-color: #d1d5db; }

/* Sección Mascota */
.mascot-section {
  display: flex;
  justify-content: center;
  width: 100%;
}

/* Grid */
.list-grid {
  display: grid;
  grid-template-columns: repeat(1, 1fr);
  gap: 24px;
}
@media (min-width: 768px) { .list-grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1024px) { .list-grid { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 1280px) { .list-grid { grid-template-columns: repeat(4, 1fr); } }

/* Coming Soon */
.coming-soon {
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(4px);
  border-radius: 2rem;
  padding: 32px;
  border: 2px dashed rgba(255, 255, 255, 0.6);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 16px;
  transition: opacity 0.3s;
}

.coming-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.4);
  display: grid;
  place-items: center;
  color: rgba(30, 75, 102, 0.4);
}

.coming-title {
  font-family: 'Fredoka', sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  color: rgba(30, 75, 102, 0.6);
}

/* Botón Ver Más */
.more-wrap { display: flex; justify-content: center; margin-top: 24px; }
.more-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 700;
  backdrop-filter: blur(4px);
  border: none;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: 0.3s;
}
.more-btn:hover { background: rgba(255, 255, 255, 0.3); }
</style>