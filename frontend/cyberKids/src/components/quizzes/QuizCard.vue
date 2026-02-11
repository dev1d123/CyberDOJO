<template>
  <article
    class="bg-white rounded-[2rem] p-6 shadow-soft hover:shadow-xl transition-all hover:-translate-y-1 relative group overflow-hidden border-b-4 border-sky-blue/30"
  >
    <div
      class="absolute -right-6 -top-6 w-32 h-32 bg-sky-blue/10 rounded-full group-hover:scale-150 transition-transform duration-500"
    ></div>
    <div class="flex flex-col h-full gap-4 relative z-0">
      <div
        class="bg-sky-blue/20 w-16 h-16 rounded-2xl flex items-center justify-center text-sky-700 mb-2"
      >
        <span class="material-icons-round text-4xl">quiz</span>
      </div>
      <div>
        <h3 class="font-fredoka text-xl font-bold text-deep-sea mb-2">
          Quizzes
        </h3>
        <p class="text-deep-sea/60 text-sm font-medium leading-relaxed">
          Pon a prueba tus conocimientos y aprende sobre seguridad.
        </p>
      </div>
      <div class="flex items-center gap-1 text-yellow-400 mt-auto">
        <span class="material-icons-round text-xl">star</span>
        <span class="material-icons-round text-xl">star</span>
        <span class="material-icons-round text-xl">star_half</span>
        <span class="text-xs font-bold text-deep-sea/40 ml-2 uppercase"
          >Varios</span
        >
      </div>
      <router-link
        to="/quiz"
        class="w-full mt-4 bg-sky-blue hover:bg-sky-400 text-white font-bold py-3 rounded-xl shadow-button hover:shadow-button-hover active:shadow-button-active active:translate-y-1 border-b-4 border-sky-700/20 transition-all flex items-center justify-center gap-2"
      >
        <span class="material-icons-round">play_arrow</span>
        Ir a Quizzes
      </router-link>
    </div>
  </article>
</template>
