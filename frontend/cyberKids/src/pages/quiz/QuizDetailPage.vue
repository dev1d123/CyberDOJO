<template>
  <div class="quiz-detail-page">
    <QuizHeader :current="3" :total="10" :percent="30">
      <template #actions>
        <router-link to="/challenges/quiz" class="back-link">⬅️ Volver</router-link>
      </template>
    </QuizHeader>

    <div class="hero-row">
      <div class="mascot-area">
        <img class="mascot" :src="mascot" alt="robot" />
      </div>
      <div class="message-area">
        <div class="alert">¡Oh no! 😟</div>
        <p class="advice">Nunca compartas tu contraseña. Los bancos o juegos nunca la pedirán así.</p>
      </div>
    </div>

    <div class="content-grid">
      <div class="main-col">
        <QuizQuestionPanel badge="Pregunta" question="¿Qué debes hacer si recibes un correo extraño pidiendo tu contraseña?" hint="Parece urgente y dice que tu cuenta será bloqueada si no respondes ya mismo." />

        <div class="hint-box" v-if="showHint">💡 Pista: Recuerda verificar siempre el remitente del correo.</div>

        <QuizOptionsGrid :options="options" />
      </div>

      <div class="side-col">
        <QuizSidebar @toggle-hint="showHint = !showHint" />
        
        <FeedbackModal v-if="showModal" :selected-index="1" :mascot="mascot" @onContinue="showModal = false" @onClose="showModal = false" />

        <button @click="showFeedback" class="next-btn">Siguiente ▶️</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import QuizHeader from '@/components/quiz/quizPage/QuizHeader.vue'
import QuizQuestionPanel from '@/components/quiz/quizPage/QuizQuestionPanel.vue'
import QuizOptionsGrid from '@/components/quiz/quizPage/QuizOptionsGrid.vue'
import QuizSidebar from '@/components/quiz/quizPage/QuizSidebar.vue'
import FeedbackModal from '@/components/quiz/quizPage/FeedbackModal.vue'

import { ref } from 'vue'

const mascot = 'https://lh3.googleusercontent.com/aida-public/AB6AXuCucjZBT2oZoN5rGKrDGU5Q9yq3f9tkghZGt5pjgZLPnrwZPlzx51O5syvPmrxMw9uR7djGOJodI2-z0YPaCfHQMw8Ptu-RD5shLTsY9mm4lR7j1f0ylbyId7-YVTjGo_C00NHByKcMLcxMhQZqC7cqy3Qlvk6uMEpeyHCm4fD222J3HgreRPI4Eyoy5VCcht_IBGGT3vlzJtXKNwqYmc0LV9CFCGOkMfrKcUg7HYnu6DL_JlavvApLhf_4xDZMGi-E0UmCJOuZ_gZ5'
const showHint = ref(true)
const showModal = ref(false)

const options = [
  { text: 'Responder rápido con mi contraseña' },
  { text: 'Borrarlo y avisar a un adulto' },
  { text: 'Reenviarlo a todos mis amigos', disabled: true },
  { text: 'Hacer clic en el enlace adjunto', disabled: true },
]

const showFeedback = () => {
    showModal.value = true
}

const handleClose = () => {
  showModal.value = false
}
</script>

<style scoped>
.quiz-detail-page{ padding:20px; max-width:1100px; margin:0 auto; display:flex; flex-direction:column; gap:18px }
.hero-row{ display:flex; gap:16px; align-items:end }
.mascot-area{ width:120px }
.mascot{ width:100%; height:auto }
.message-area .alert{ background:#ff7a7a; color:white; padding:14px; border-radius:12px; font-weight:900 }
.message-area .advice{ margin-top:8px; color:rgba(30,75,102,0.85); font-weight:700 }
.content-grid{ display:grid; grid-template-columns: 1fr 320px; gap:18px }
.main-col{ display:flex; flex-direction:column; gap:12px }
.side-col{ display:flex; flex-direction:column; gap:12px }
.hint-box{ background:rgba(139,124,255,0.12); padding:12px; border-radius:10px; text-align:center; font-weight:800 }
.next-btn{ background:#1E4B66; color:white; padding:12px; border-radius:12px; font-weight:900 }
@media (max-width:900px){ .content-grid{ grid-template-columns:1fr } .hero-row{ flex-direction:row; } .mascot-area{ width:92px } }
</style>