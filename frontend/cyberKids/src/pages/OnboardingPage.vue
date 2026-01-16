<template>
  <div class="onboarding-page">
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Cargando preguntas...</p>
    </div>

    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠️</div>
      <h2>Oops! Algo salió mal</h2>
      <p>{{ error }}</p>
      <button @click="loadQuestions" class="retry-button">Intentar de nuevo</button>
    </div>

    <div v-else-if="questions.length > 0 && currentQuestion" class="questionnaire-container">
      <!-- Progress Bar -->
      <div class="progress-container">
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: `${progressPercentage}%` }"
          ></div>
        </div>
        <div class="progress-text">
          Pregunta {{ currentQuestionIndex + 1 }} de {{ questions.length }}
        </div>
      </div>

      <!-- Question Content -->
      <transition name="slide-fade" mode="out-in">
        <div :key="currentQuestion.question_id" class="question-wrapper">
          <QuestionMultipleChoice
            v-if="currentQuestion.response_type === 'multiple_choice'"
            :question="currentQuestion"
            v-model="answers[currentQuestion.question_id]"
          />
          
          <QuestionYesNo
            v-else-if="currentQuestion.response_type === 'yes_no'"
            :question="currentQuestion"
            v-model="answers[currentQuestion.question_id]"
          />
          
          <QuestionScale
            v-else-if="currentQuestion.response_type === 'scale'"
            :question="currentQuestion"
            v-model="answers[currentQuestion.question_id]"
          />
        </div>
      </transition>

      <!-- Navigation Buttons -->
      <div class="navigation-buttons">
        <button
          v-if="currentQuestionIndex > 0"
          @click="previousQuestion"
          class="nav-button prev-button"
        >
          ← Anterior
        </button>
        
        <button
          v-if="currentQuestionIndex < questions.length - 1"
          @click="nextQuestion"
          class="nav-button next-button"
          :disabled="answers[currentQuestion.question_id] == null"
        >
          Siguiente →
        </button>
        
        <button
          v-else
          @click="submitAnswers"
          class="nav-button submit-button"
          :disabled="answers[currentQuestion.question_id] == null || submitting"
        >
          {{ submitting ? 'Enviando...' : '✓ Terminar' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import QuestionMultipleChoice from '@/components/QuestionMultipleChoice.vue';
import QuestionYesNo from '@/components/QuestionYesNo.vue';
import QuestionScale from '@/components/QuestionScale.vue';
import { OnboardingService } from '@/services/onboarding.service';
import type { OnboardingQuestion, OnboardingResponse, UserAnswer } from '@/dto/onboarding.dto';

const router = useRouter();

const questions = ref<OnboardingQuestion[]>([]);
const currentQuestionIndex = ref(0);
const answers = ref<Record<number, number | null>>({});
const loading = ref(true);
const error = ref<string | null>(null);
const submitting = ref(false);

const currentQuestion = computed<OnboardingQuestion | null>(
  () => questions.value[currentQuestionIndex.value] ?? null
);

const progressPercentage = computed(() => {
  return ((currentQuestionIndex.value + 1) / questions.value.length) * 100;
});

const loadQuestions = async () => {
  try {
    loading.value = true;
    error.value = null;
    questions.value = await OnboardingService.getActiveQuestions();
  } catch (err) {
    error.value = 'No se pudieron cargar las preguntas. Por favor, intenta de nuevo.';
    console.error('Error loading questions:', err);
  } finally {
    loading.value = false;
  }
};

const nextQuestion = () => {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++;
  }
};

const previousQuestion = () => {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--;
  }
};

const submitAnswers = async () => {
  try {
    submitting.value = true;
    
    // Obtener user_id del localStorage
    let userId = localStorage.getItem('user_id');
    
    // Si no está en localStorage, intentar extraer del token
    if (!userId) {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const payloadPart = token.split('.')[1];
          if (!payloadPart) {
            throw new Error('Token inválido: no payload');
          }
          const tokenPayload = JSON.parse(atob(payloadPart));
          userId = tokenPayload.user_id?.toString();
        } catch (e) {
          console.error('Error al decodificar token:', e);
        }
      }
    }
    
    if (!userId) {
      throw new Error('No se encontró información del usuario. Por favor, inicia sesión nuevamente.');
    }
    
    const userIdNum = parseInt(userId);

    // Enviar cada respuesta al backend
    const responsePromises = questions.value.map((question) => {
      const selectedOptionId = answers.value[question.question_id];
      if (selectedOptionId == null) {
        throw new Error('Faltan respuestas. Por favor completa todas las preguntas.');
      }
      const response: OnboardingResponse = {
        user: userIdNum,
        question: question.question_id,
        option: selectedOptionId
      };
      return OnboardingService.submitResponse(response);
    });

    await Promise.all(responsePromises);

    // Preparar datos para el dashboard
    const userAnswers: UserAnswer[] = questions.value.map((question) => {
      const selectedOptionId = answers.value[question.question_id];
      if (selectedOptionId == null) {
        throw new Error('Faltan respuestas. Por favor completa todas las preguntas.');
      }

      const selectedOption = question.options.find((opt) => opt.option_id === selectedOptionId);
      if (!selectedOption) {
        throw new Error('Respuesta inválida. Por favor intenta nuevamente.');
      }
      
      return {
        question_id: question.question_id,
        question_content: question.content,
        option_id: selectedOption.option_id,
        option_content: selectedOption.content,
        risk_value: selectedOption.risk_value,
        risk_weight: question.risk_weight
      };
    });

    // Calcular nivel de riesgo
    const result = OnboardingService.calculateRiskLevel(userAnswers);

    // Guardar resultados en localStorage y navegar al dashboard
    localStorage.setItem('onboarding_results', JSON.stringify({
      answers: userAnswers,
      ...result
    }));

    // Mostrar resultados en consola
    console.log('='.repeat(60));
    console.log('📊 RESULTADOS DEL ONBOARDING');
    console.log('='.repeat(60));
    console.log('\n🎯 Respuestas:');
    userAnswers.forEach((answer, index) => {
      console.log(`\n${index + 1}. ${answer.question_content}`);
      console.log(`   → ${answer.option_content}`);
      console.log(`   Riesgo: ${answer.risk_value} | Peso: ${answer.risk_weight}`);
    });
    console.log('\n' + '='.repeat(60));
    console.log(`🎲 Puntuación de Riesgo: ${result.total_risk_score}%`);
    console.log(`⚠️  Nivel de Riesgo: ${result.risk_level.toUpperCase()}`);
    console.log('='.repeat(60));
    console.log('\n📋 Recomendaciones:');
    result.recommendations.forEach((rec, index) => {
      console.log(`${index + 1}. ${rec}`);
    });
    console.log('\n' + '='.repeat(60));

    router.push('/results');
  } catch (err) {
    console.error('Error submitting answers:', err);
    error.value = 'No se pudieron enviar las respuestas. Por favor, intenta de nuevo.';
  } finally {
    submitting.value = false;
  }
};

onMounted(() => {
  loadQuestions();
});
</script>

<style scoped>
.onboarding-page {
  min-height: 100vh;
  height: 100vh;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.loading-container,
.error-container {
  text-align: center;
  color: white;
  animation: fadeIn 0.5s ease;
}

.spinner {
  width: 60px;
  height: 60px;
  border: 5px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

.error-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.error-container h2 {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.retry-button {
  margin-top: 1.5rem;
  padding: 1rem 2rem;
  background: white;
  color: #667eea;
  border: none;
  border-radius: 15px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-button:hover {
  transform: scale(1.05);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.questionnaire-container {
  width: 100%;
  max-width: 900px;
  height: 90vh;
  background: white;
  border-radius: 30px;
  padding: 2rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  animation: slideUp 0.6s ease-out;
}

.progress-container {
  margin-bottom: 2rem;
}

.progress-bar {
  width: 100%;
  height: 12px;
  background: #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  transition: width 0.5s ease;
  animation: shimmer 2s infinite;
}

.progress-text {
  text-align: center;
  font-size: 1.1rem;
  font-weight: 600;
  color: #64748b;
}

.question-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow-y: auto;
  margin-bottom: 2rem;
}

.navigation-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  padding-top: 1rem;
  border-top: 2px solid #e2e8f0;
}

.nav-button {
  padding: 1rem 2.5rem;
  border: none;
  border-radius: 15px;
  font-size: 1.2rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.prev-button {
  background: linear-gradient(135deg, #cbd5e1 0%, #94a3b8 100%);
  color: white;
}

.next-button,
.submit-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.nav-button:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.nav-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.submit-button {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

/* Animations */
.slide-fade-enter-active {
  transition: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from {
  transform: translateX(100px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(-100px);
  opacity: 0;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(50px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes shimmer {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}

@media (max-width: 768px) {
  .onboarding-page {
    padding: 1rem;
  }
  
  .questionnaire-container {
    height: 95vh;
    padding: 1.5rem;
  }
  
  .nav-button {
    padding: 0.8rem 1.5rem;
    font-size: 1rem;
  }
  
  .navigation-buttons {
    flex-direction: column;
  }
}
</style>
