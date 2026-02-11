<template>
  <article
    :class="`bg-white rounded-[2rem] p-6 shadow-soft hover:shadow-xl transition-all hover:-translate-y-1 relative group overflow-hidden border-b-4 border-${quiz.color}/30`"
  >
    <div
      v-if="quiz.isNew"
      class="absolute top-4 right-4 bg-coral text-white text-xs font-bold px-3 py-1 rounded-full shadow-sm z-10"
    >
      NUEVO
    </div>
    <div
      :class="`absolute -right-6 -top-6 w-32 h-32 bg-${quiz.color}/10 rounded-full group-hover:scale-150 transition-transform duration-500`"
    ></div>
    <div class="flex flex-col h-full gap-4 relative z-0">
      <div
        :class="`bg-${quiz.color}/20 w-16 h-16 rounded-2xl flex items-center justify-center text-${quiz.color} mb-2`"
      >
        <span class="material-icons-round text-4xl">{{ quiz.icon }}</span>
      </div>
      <div>
        <h3 class="font-fredoka text-xl font-bold text-deep-sea mb-2">
          {{ quiz.title }}
        </h3>
        <p class="text-deep-sea/60 text-sm font-medium leading-relaxed">
          {{ quiz.description }}
        </p>
      </div>
      <div class="flex items-center gap-1 text-yellow-400 mt-auto">
        <span v-for="n in Math.floor(quiz.stars)" :key="n" class="material-icons-round text-xl">star</span>
        <span v-if="quiz.stars % 1 !== 0" class="material-icons-round text-xl">star_half</span>
        <span v-for="n in 3 - Math.ceil(quiz.stars)" :key="n" class="material-icons-round text-xl">star_border</span>
        <span class="text-xs font-bold text-deep-sea/40 ml-2 uppercase">{{
          quiz.difficulty
        }}</span>
      </div>
      <button
        :class="`w-full mt-4 bg-${quiz.color} hover:bg-${quiz.color}-400 text-white font-bold py-3 rounded-xl shadow-button hover:shadow-button-hover active:shadow-button-active active:translate-y-1 border-b-4 border-${quiz.color}-700/20 transition-all flex items-center justify-center gap-2`"
      >
        <span class="material-icons-round">play_arrow</span>
        Jugar
      </button>
    </div>
  </article>
</template>

<script setup lang="ts">
defineProps({
  quiz: {
    type: Object,
    required: true,
  },
});
</script>
