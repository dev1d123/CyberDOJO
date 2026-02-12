<template>
  <div class="quiz-detail-page" v-if="!quizCompleted">
    <!-- Modal de advertencia para reintentos -->
    <div v-if="showRestartWarning" class="modal-overlay" @click="showRestartWarning = false">
      <div class="modal-content" @click.stop>
        <h2>🎯 Reiniciar Quiz</h2>
        <p>Ya has intentado este quiz antes. Si lo reinicias, no habrá recompensa en este intento.</p>
        <p v-if="previousAttempts" class="attempts-text">📊 Intentos previos: {{ previousAttempts }}</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="goBack">Cancelar</button>
          <button class="btn-confirm" @click="confirmStart">Sí, intentar de nuevo</button>
        </div>
      </div>
    </div>

    <QuizHeader :current="answeredQuestions" :total="totalQuestions" :percent="progressPercent">
      <template #actions>
        <router-link to="/challenges/quiz" class="back-link">⬅️ Volver</router-link>
      </template>
    </QuizHeader>

    <div class="hero-row">
      <div class="mascot-area">
        <img class="mascot" :src="mascot" alt="mascot" :class="{ 'mascot-reaction': showMascotReaction }" />
      </div>
      <div class="message-area">
        <div :class="['alert', { 'alert-correct': lastAnswerCorrect === true, 'alert-wrong': lastAnswerCorrect === false }]">
          {{ mascotMessage }}
        </div>
        <p class="advice">{{ quizDescription }}</p>
      </div>
    </div>

    <div class="content-grid">
      <div class="main-col">
        <QuizQuestionPanel badge="Pregunta" :question="questionText" :hint="hintText" />

        <div class="hint-box" v-if="showHint && hintText">💡 Pista: {{ hintText }}</div>

        <!-- Opciones -->
        <div class="options-container">
          <button 
            v-for="alt in currentAnswer" 
            :key="alt.id"
            :class="['option-btn', { 'selected': selectedAnswer === alt.id }]"
            @click="selectAnswer(alt.id)"
            :disabled="questionAnswered"
          >
            {{ alt.content }}
          </button>
        </div>
      </div>

      <div class="side-col">
        <QuizSidebar :time-label="timeLabel" :points="totalPoints" @toggle-hint="showHint = !showHint" />
        
        <!-- Modal de Feedback -->
        <FeedbackModal 
          v-if="showModal" 
          :feedback-options="feedbackOptions"
          :user-selected-index="selectedAnswerIndex"
          :mascot-url="mascot" 
          @onContinue="goNextQuestion" 
          @onClose="showModal = false" 
        />

        <button @click="submitAnswer" class="next-btn" :disabled="selectedAnswer === null || questionAnswered || submitting || !canPlay || isTimeUp">
          {{ submitting ? '⏳ Enviando...' : 'Siguiente ▶️' }}
        </button>
      </div>
    </div>
  </div>

  <!-- Vista de Completado -->
  <ModalVictory 
    v-else
    :quiz-title="quizTitle"
    :total-correct="sessionStats.total_correct"
    :total-questions="sessionStats.total_answered"
    :coins-earned="sessionStats.coins_earned"
    :points-earned="sessionStats.points_earned"
    @onRetry="handleRetry"
    @onBack="goBack"
  />
</template>

<script setup lang="ts">
import QuizHeader from '@/components/quiz/quizPage/QuizHeader.vue'
import QuizQuestionPanel from '@/components/quiz/quizPage/QuizQuestionPanel.vue'
import QuizSidebar from '@/components/quiz/quizPage/QuizSidebar.vue'
import FeedbackModal from '@/components/quiz/quizPage/FeedbackModal.vue'
import ModalVictory from '@/components/quiz/quizPage/ModalVictory.vue'

import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { QuizService } from '@/services/quiz.service'

const mascot = 'https://lh3.googleusercontent.com/aida-public/AB6AXuCucjZBT2oZoN5rGKrDGU5Q9yq3f9tkghZGt5pjgZLPnrwZPlzx51O5syvPmrxMw9uR7djGOJodI2-z0YPaCfHQMw8Ptu-RD5shLTsY9mm4lR7j1f0ylbyId7-YVTjGo_C00NHByKcMLcxMhQZqC7cqy3Qlvk6uMEpeyHCm4fD222J3HgreRPI4Eyoy5VCcht_IBGGT3vlzJtXKNwqYmc0LV9CFCGOkMfrKcUg7HYnu6DL_JlavvApLhf_4xDZMGi-E0UmCJOuZ_gZ5'

const route = useRoute()
const router = useRouter()

// Estado UI
const showHint = ref(false)
const showModal = ref(false)
const showRestartWarning = ref(false)
const showMascotReaction = ref(false)
const submitting = ref(false)
const canPlay = ref(false)

// Datos del quiz
const quizId = ref<number | null>(null)
const sessionId = ref<number | null>(null)
const quizTitle = ref('Quiz')
const quizDescription = ref('')
const quizBasePoints = ref(0)
const quizDifficulty = ref(1)
const questions = ref<Array<any>>([])
const loading = ref(false)
const quizCompleted = ref(false)
const timeLimitSeconds = ref(0)
const timeRemaining = ref(0)
const totalPoints = ref(0)
const questionStartedAt = ref<number | null>(null)
let timerHandle: number | null = null

// Estado de respuestas
const currentQuestionIndex = ref(0)
const selectedAnswer = ref<number | null>(null)
const questionAnswered = ref(false)
const lastAnswerCorrect = ref<boolean | null>(null)
const lastFeedback = ref('')
const mascotMessage = ref('¡Responde correctamente!')
const previousAttempts = ref(0)

// Session stats para victory modal
const sessionStats = ref({
  total_correct: 0,
  total_answered: 0,
  coins_earned: 0,
  points_earned: 0
})

// Computados
const currentQuestion = computed(() => questions.value[currentQuestionIndex.value] ?? null)
const currentAnswer = computed(() => currentQuestion.value?.alternatives ?? [])
const totalQuestions = computed(() => questions.value.length)
const answeredQuestions = computed(() => currentQuestionIndex.value + 1)
const progressPercent = computed(() => {
  return totalQuestions.value > 0 ? Math.round((answeredQuestions.value / totalQuestions.value) * 100) : 0
})
const questionText = computed(() => currentQuestion.value?.content ?? 'Cargando...')
const hintText = computed(() => currentQuestion.value?.hints?.[0]?.content ?? '')
const isTimeUp = computed(() => timeLimitSeconds.value > 0 && timeRemaining.value === 0)
const timeLabel = computed(() => {
  const totalSeconds = Math.max(timeRemaining.value, 0)
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
})

// Opciones de feedback para el modal
const selectedAnswerIndex = computed(() => {
  if (!selectedAnswer.value) return -1
  const idx = currentAnswer.value.findIndex((alt: any) => alt.id === selectedAnswer.value)
  return idx
})

const feedbackOptions = computed(() => {
  return currentAnswer.value.map((alt: any) => ({
    title: alt.content ?? 'Opción',
    description: alt.feedback ?? 'Sin descripción',
    isCorrect: alt.is_correct ?? false
  }))
})

// Funciones
const getQuizParam = () => {
  return (route.params.id ?? route.params.slug) as string | number | undefined
}

onMounted(async () => {
  const param = getQuizParam()
  quizId.value = Number(param ?? 1)
  loading.value = true
  
  try {
    const quiz = await QuizService.getQuizById(quizId.value)
    
    quizTitle.value = quiz.title ?? 'Quiz'
    quizDescription.value = quiz.description ?? ''
    quizBasePoints.value = quiz.base_points ?? 0
    quizDifficulty.value = quiz.difficulty_level ?? 1
    
    questions.value = (quiz.questions ?? []).map((q: any) => ({
      id: q.id ?? 0,
      content: q.content ?? '',
      explanation: q.explanation ?? '',
      points: q.points ?? 10,
      display_order: q.display_order ?? 1,
      image_url: q.image_url ?? null,
      alternatives: (q.alternatives ?? []).map((alt: any) => ({
        id: alt.id ?? 0,
        content: alt.content ?? '',
        display_order: alt.display_order ?? 1,
        is_correct: alt.is_correct ?? false,
        feedback: alt.feedback ?? ''
      })),
      hints: (q.hints ?? []).map((hint: any) => ({
        id: hint.id ?? 0,
        content: hint.content ?? '',
        cost_points: hint.cost_points ?? 5,
        display_order: hint.display_order ?? 1
      }))
    }))
    timeLimitSeconds.value = quiz.time_limit_seconds ?? 0
    timeRemaining.value = timeLimitSeconds.value
    totalPoints.value = 0
    await startSession()
  } catch (err) {
    console.error('Error cargando quiz:', err)
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  stopTimer()
})

const selectAnswer = (altId: number) => {
  if (!questionAnswered.value) {
    selectedAnswer.value = altId
  }
}

const submitAnswer = async () => {
  if (selectedAnswer.value === null || questionAnswered.value) return
  if (!canPlay.value || isTimeUp.value) return
  
  submitting.value = true
  
  try {
    if (!sessionId.value) {
      throw new Error('No se pudo iniciar la sesión del quiz.')
    }

    const now = Date.now()
    const elapsedSeconds = questionStartedAt.value
      ? Math.max(1, Math.round((now - questionStartedAt.value) / 1000))
      : 0

    // Enviar respuesta
    const response = await QuizService.submitAnswer(quizId.value!, {
      question_id: currentQuestion.value!.id,
      selected_alternative_id: selectedAnswer.value,
      time_spent_seconds: elapsedSeconds
    })

    // Mostrar reacción de mascota
    lastAnswerCorrect.value = response.is_correct
    lastFeedback.value = response.feedback ?? ''
    mascotMessage.value = response.feedback ?? (response.is_correct ? '¡Correcto!' : 'Incorrecto')
    showMascotReaction.value = true
    questionAnswered.value = true
    showModal.value = true
    if (response.is_correct) {
      totalPoints.value += currentQuestion.value?.points ?? 0
    }

    // Si el quiz se completó
    if (response.quiz_completed) {
      sessionStats.value = {
        total_correct: response.total_correct ?? 0,
        total_answered: response.total_answered ?? 0,
        coins_earned: response.coins_earned ?? 0,
        points_earned: response.points_earned ?? 0
      }
      
      // Guardar monedas en localStorage (luego se sincronizará con servidor)
      const currentCoins = parseInt(localStorage.getItem('coins') ?? '0')
      localStorage.setItem('coins', String(currentCoins + sessionStats.value.coins_earned))
    }
  } catch (err) {
    console.error('Error enviando respuesta:', err)
    alert('Error al enviar respuesta: ' + (err as any)?.message)
  } finally {
    submitting.value = false
  }
}

const goNextQuestion = () => {
  showMascotReaction.value = false
  showModal.value = false

  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++
    selectedAnswer.value = null
    questionAnswered.value = false
    showHint.value = false
    questionStartedAt.value = Date.now()
  } else {
    // Mostrar victory modal
    quizCompleted.value = true
    stopTimer()
  }
}

const confirmStart = () => {
  showRestartWarning.value = false
  canPlay.value = true
  resetAttemptState()
}

const handleRetry = () => {
  quizCompleted.value = false
  currentQuestionIndex.value = 0
  selectedAnswer.value = null
  questionAnswered.value = false
  lastAnswerCorrect.value = null
  sessionId.value = null
  canPlay.value = false
  stopTimer()
  startSession()
}

const goBack = () => {
  router.push('/challenges/quiz')
}

const startSession = async () => {
  if (!quizId.value) return
  try {
    const startRes = await QuizService.startQuizSession(quizId.value)
    sessionId.value = startRes.id

    if (startRes.show_warning && (startRes.previous_attempts ?? 0) > 0) {
      previousAttempts.value = startRes.previous_attempts ?? 0
      showRestartWarning.value = true
      canPlay.value = false
      return
    }

    canPlay.value = true
    resetAttemptState()
  } catch (err) {
    console.error('Error iniciando sesión del quiz:', err)
    canPlay.value = false
  }
}

const resetAttemptState = () => {
  totalPoints.value = 0
  timeRemaining.value = timeLimitSeconds.value
  questionStartedAt.value = Date.now()
  if (timeRemaining.value > 0) {
    startTimer()
  }
}

const startTimer = () => {
  stopTimer()
  timerHandle = window.setInterval(() => {
    if (timeRemaining.value <= 0) {
      timeRemaining.value = 0
      stopTimer()
      return
    }
    timeRemaining.value -= 1
  }, 1000)
}

const stopTimer = () => {
  if (timerHandle) {
    window.clearInterval(timerHandle)
    timerHandle = null
  }
}
</script>

<style scoped>
.quiz-detail-page { 
  padding: 20px; 
  max-width: 1100px; 
  margin: 0 auto; 
  display: flex; 
  flex-direction: column; 
  gap: 18px;
  position: relative;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 20px;
  padding: 30px;
  max-width: 400px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-content h2 {
  margin-bottom: 12px;
  color: #1e4b66;
  font-size: 1.4em;
}

.modal-content p {
  color: #666;
  margin-bottom: 8px;
}

.attempts-text {
  font-weight: 700;
  color: #8b7cff;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.btn-cancel,
.btn-confirm {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel {
  background: #e0e0e0;
  color: #666;
}

.btn-cancel:hover {
  background: #d0d0d0;
}

.btn-confirm {
  background: #8b7cff;
  color: white;
}

.btn-confirm:hover {
  background: #7a6ddd;
}

.hero-row {
  display: flex;
  gap: 16px;
  align-items: flex-end;
}

.mascot-area {
  width: 120px;
}

.mascot {
  width: 100%;
  height: auto;
  transition: transform 0.3s ease;
}

.mascot.mascot-reaction {
  animation: bounce 0.6s ease;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.message-area .alert {
  background: #ff7a7a;
  color: white;
  padding: 14px;
  border-radius: 12px;
  font-weight: 900;
  min-height: 35px;
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
}

.alert-correct {
  background: #4caf50 !important;
}

.alert-wrong {
  background: #ff6b6b !important;
}

.message-area .advice {
  margin-top: 8px;
  color: rgba(30, 75, 102, 0.85);
  font-weight: 700;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 18px;
}

.main-col {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.side-col {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.hint-box {
  background: rgba(139, 124, 255, 0.12);
  padding: 12px;
  border-radius: 10px;
  text-align: center;
  font-weight: 800;
}

/* Opciones/Alternativas */
.options-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 16px 0;
}

.option-btn {
  background: white;
  border: 2px solid #e0e0e0;
  padding: 12px 16px;
  border-radius: 12px;
  text-align: left;
  cursor: pointer;
  font-weight: 700;
  color: #1e4b66;
  transition: all 0.2s ease;
}

.option-btn:hover:not(:disabled) {
  border-color: #8b7cff;
  background: #f8f9ff;
}

.option-btn.selected {
  background: #8b7cff;
  color: white;
  border-color: #8b7cff;
}

.option-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.next-btn {
  background: #1e4b66;
  color: white;
  padding: 12px;
  border-radius: 12px;
  font-weight: 900;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.next-btn:hover:not(:disabled) {
  background: #153a50;
}

.next-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.back-link {
  color: white;
  text-decoration: none;
  font-weight: 700;
}

@media (max-width: 900px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  .mascot-area {
    width: 92px;
  }
}
</style>