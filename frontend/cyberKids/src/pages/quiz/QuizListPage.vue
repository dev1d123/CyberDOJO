<template>
  <div class="relative flex flex-col items-center min-h-screen p-6 text-deep-sea">
    <div class="floating-cloud cloud-1"></div>
    <div class="floating-cloud cloud-2"></div>
    <div class="floating-cloud cloud-3"></div>
    <div class="floating-cloud cloud-4"></div>
    <main class="relative z-10 w-full max-w-7xl flex flex-col gap-6 mb-8">
      <header class="flex flex-col md:flex-row items-end md:items-center justify-between gap-6 mb-4">
        <div class="flex items-center gap-6 w-full md:w-auto">
          <div class="relative w-24 h-24 md:w-32 md:h-32 shrink-0">
            <div
              class="absolute inset-0 bg-white rounded-full shadow-soft flex items-center justify-center overflow-hidden border-4 border-white"
            >
              <img
                alt="Friendly 3D robot mascot waving hello"
                class="w-full h-full object-cover scale-110 mt-2"
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuCucjZBT2oZoN5rGKrDGU5Q9yq3f9tkghZGt5pjgZLPnrwZPlzx51O5syvPmrxMw9uR7djGOJodI2-z0YPaCfHQMw8Ptu-RD5shLTsY9mm4lR7j1f0ylbyId7-YVTjGo_C00NHByKcMLcxMhQZqC7cqy3Qlvk6uMEpeyHCm4fD222J3HgreRPI4Eyoy5VCcht_IBGGT3vlzJtXKNwqYmc0LV9CFCGOkMfrKcUg7HYnu6DL_JlavvApLhf_4xDZMGi-E0UmCJOuZ_gZ5"
              />
            </div>
          </div>
          <div class="bg-white p-4 md:p-6 rounded-2xl rounded-tl-none shadow-soft relative flex-1">
            <h1 class="font-fredoka text-2xl md:text-3xl font-bold text-deep-sea leading-tight">
              ¡Elige tu próxima misión! 🚀
            </h1>
            <p class="text-deep-sea/70 font-medium mt-1">¿Qué quieres aprender hoy?</p>
            <div class="absolute top-0 -left-3 w-4 h-4 bg-white transform skew-x-12"></div>
          </div>
        </div>
        <div
          class="w-full md:w-auto flex flex-col md:flex-row gap-3 bg-white/90 backdrop-blur-sm p-3 rounded-2xl shadow-soft border border-white/50"
        >
          <div class="relative group">
            <span
              class="material-icons-round absolute left-3 top-1/2 -translate-y-1/2 text-deep-sea/40 group-focus-within:text-primary transition-colors"
              >search</span
            >
            <input
              class="pl-10 pr-4 py-3 bg-background-light rounded-xl border-none focus:ring-2 focus:ring-primary/50 text-deep-sea placeholder-deep-sea/40 font-medium w-full md:w-64 transition-all"
              placeholder="Buscar quiz..."
              type="text"
            />
          </div>
          <div class="flex gap-2 overflow-x-auto pb-1 md:pb-0 scrollbar-hide">
            <button
              class="px-4 py-3 bg-primary text-deep-sea font-bold rounded-xl shadow-button hover:shadow-button-hover active:shadow-button-active active:translate-y-1 transition-all whitespace-nowrap border-b-4 border-yellow-600/20"
            >
              Todos
            </button>
            <button
              class="px-4 py-3 bg-white hover:bg-background-light text-deep-sea font-bold rounded-xl border-b-4 border-gray-200 hover:border-gray-300 active:border-b-0 active:translate-y-1 transition-all whitespace-nowrap"
            >
              Phishing
            </button>
            <button
              class="px-4 py-3 bg-white hover:bg-background-light text-deep-sea font-bold rounded-xl border-b-4 border-gray-200 hover:border-gray-300 active:border-b-0 active:translate-y-1 transition-all whitespace-nowrap"
            >
              Contraseñas
            </button>
            <button
              class="px-4 py-3 bg-white hover:bg-background-light text-deep-sea font-bold rounded-xl border-b-4 border-gray-200 hover:border-gray-300 active:border-b-0 active:translate-y-1 transition-all whitespace-nowrap"
            >
              Privacidad
            </button>
          </div>
        </div>
      </header>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        <QuizListItem v-for="quiz in quizzes" :key="quiz.id" :quiz="quiz" />
        <article
          class="bg-white/50 backdrop-blur-sm rounded-[2rem] p-6 border-2 border-dashed border-white/60 flex flex-col items-center justify-center text-center gap-4 group"
        >
          <div
            class="bg-white/40 w-20 h-20 rounded-full flex items-center justify-center text-deep-sea/40 group-hover:scale-110 transition-transform"
          >
            <span class="material-icons-round text-4xl">lock_clock</span>
          </div>
          <h3 class="font-fredoka text-xl font-bold text-deep-sea/60">Próximamente</h3>
          <p class="text-deep-sea/50 text-sm font-medium">
            ¡Nuevas misiones están siendo preparadas!
          </p>
        </article>
      </div>
      <div class="flex justify-center mt-4">
        <button
          class="px-6 py-3 bg-white/20 hover:bg-white/30 text-white font-bold rounded-xl backdrop-blur-sm transition-colors flex items-center gap-2"
        >
          Ver más misiones
          <span class="material-icons-round">expand_more</span>
        </button>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import QuizListItem from '@/components/quizzes/list/QuizListItem.vue';

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
body {
  font-family: 'Plus Jakarta Sans', sans-serif;
  background: linear-gradient(135deg, #6ecff5 0%, #8b7cff 100%);
  min-height: 100vh;
  overflow-x: hidden;
}
.floating-cloud {
  position: absolute;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 999px;
  filter: blur(8px);
  z-index: 0;
}
.cloud-1 {
  top: 10%;
  left: 5%;
  width: 200px;
  height: 80px;
}
.cloud-2 {
  top: 25%;
  right: 10%;
  width: 150px;
  height: 60px;
}
.cloud-3 {
  bottom: 15%;
  left: 20%;
  width: 300px;
  height: 100px;
}
.cloud-4 {
  top: 60%;
  right: -5%;
  width: 250px;
  height: 90px;
  opacity: 0.3;
}
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 10px;
}
</style>
