<template>
  <div class="results-page">
    <div v-if="results" class="results-container">
      <!-- Header with Risk Level -->
      <div class="header-section">
        <div class="risk-badge" :class="`risk-${results.risk_level}`">
          <div class="risk-icon">{{ getRiskIcon(results.risk_level) }}</div>
          <div class="risk-info">
            <h1>Nivel de Riesgo</h1>
            <h2>{{ getRiskLevelText(results.risk_level) }}</h2>
            <div class="risk-score">{{ results.total_risk_score }}%</div>
          </div>
        </div>
      </div>

      <!-- Answers Section -->
      <div class="answers-section">
        <h3 class="section-title">📝 Tus Respuestas</h3>
        <div class="answers-grid">
          <div 
            v-for="(answer, index) in results.answers" 
            :key="answer.question_id"
            class="answer-card"
          >
            <div class="answer-number">{{ index + 1 }}</div>
            <div class="answer-content">
              <div class="answer-question">{{ answer.question_content }}</div>
              <div class="answer-response">
                <span class="answer-icon">→</span>
                {{ answer.option_content }}
              </div>
              <div class="answer-risk">
                <span class="risk-label">Riesgo:</span>
                <div class="risk-bars">
                  <div 
                    v-for="i in 5" 
                    :key="i"
                    class="risk-bar"
                    :class="{ active: i <= answer.risk_value }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recommendations Section -->
      <div class="recommendations-section">
        <h3 class="section-title">💡 Recomendaciones</h3>
        <div class="recommendations-list">
          <div 
            v-for="(recommendation, index) in results.recommendations" 
            :key="index"
            class="recommendation-card"
          >
            <div class="recommendation-number">{{ index + 1 }}</div>
            <p>{{ recommendation }}</p>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="actions-section">
        <button @click="goToDashboard" class="action-button primary">
          🎮 Ir al Dashboard
        </button>
        <button @click="retakeTest" class="action-button secondary">
          🔄 Repetir Test
        </button>
      </div>
    </div>

    <div v-else class="no-results">
      <div class="no-results-icon">📋</div>
      <h2>No hay resultados disponibles</h2>
      <p>Completa el cuestionario de onboarding primero</p>
      <button @click="goToOnboarding" class="action-button primary">
        Comenzar Onboarding
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import type { OnboardingResult } from '@/dto/onboarding.dto';

const router = useRouter();
const results = ref<OnboardingResult | null>(null);

const loadResults = () => {
  const resultsStr = localStorage.getItem('onboarding_results');
  if (resultsStr) {
    results.value = JSON.parse(resultsStr);
  }
};

const getRiskIcon = (level: string): string => {
  const icons = {
    low: '✅',
    medium: '⚠️',
    high: '🚨',
    critical: '🆘'
  };
  return icons[level as keyof typeof icons] || '❓';
};

const getRiskLevelText = (level: string): string => {
  const texts = {
    low: 'Bajo',
    medium: 'Medio',
    high: 'Alto',
    critical: 'Crítico'
  };
  return texts[level as keyof typeof texts] || 'Desconocido';
};

const goToDashboard = () => {
  router.push('/dashboard');
};

const retakeTest = () => {
  localStorage.removeItem('onboarding_results');
  router.push('/onboarding');
};

const goToOnboarding = () => {
  router.push('/onboarding');
};

onMounted(() => {
  loadResults();
});
</script>

<style scoped>
.results-page {
  min-height: 100vh;
  height: 100vh;
  overflow-y: auto;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.results-container {
  max-width: 1000px;
  margin: 0 auto;
  animation: fadeInUp 0.8s ease;
}

.header-section {
  margin-bottom: 2rem;
}

.risk-badge {
  background: white;
  border-radius: 25px;
  padding: 2rem;
  display: flex;
  align-items: center;
  gap: 2rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: bounceIn 0.8s ease;
}

.risk-icon {
  font-size: 5rem;
  animation: float 3s ease-in-out infinite;
}

.risk-info h1 {
  font-size: 1.3rem;
  color: #64748b;
  margin-bottom: 0.5rem;
}

.risk-info h2 {
  font-size: 2.5rem;
  font-weight: 900;
  margin-bottom: 0.5rem;
}

.risk-score {
  font-size: 3rem;
  font-weight: 900;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.risk-low .risk-info h2 {
  color: #22c55e;
}

.risk-medium .risk-info h2 {
  color: #f59e0b;
}

.risk-high .risk-info h2 {
  color: #ef4444;
}

.risk-critical .risk-info h2 {
  color: #dc2626;
  animation: pulse 1s ease infinite;
}

.section-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1.5rem;
  text-align: center;
}

.answers-section {
  margin-bottom: 2rem;
}

.answers-grid {
  display: grid;
  gap: 1.5rem;
}

.answer-card {
  background: white;
  border-radius: 20px;
  padding: 1.5rem;
  display: flex;
  gap: 1.5rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
  animation: slideInLeft 0.6s ease;
  animation-fill-mode: both;
}

.answer-card:nth-child(1) { animation-delay: 0.1s; }
.answer-card:nth-child(2) { animation-delay: 0.2s; }
.answer-card:nth-child(3) { animation-delay: 0.3s; }
.answer-card:nth-child(4) { animation-delay: 0.4s; }
.answer-card:nth-child(5) { animation-delay: 0.5s; }
.answer-card:nth-child(6) { animation-delay: 0.6s; }

.answer-card:hover {
  transform: translateX(10px);
}

.answer-number {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 900;
  flex-shrink: 0;
}

.answer-content {
  flex: 1;
}

.answer-question {
  font-size: 1.1rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 0.8rem;
  line-height: 1.4;
}

.answer-response {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  color: #64748b;
  margin-bottom: 0.8rem;
}

.answer-icon {
  font-size: 1.3rem;
  color: #667eea;
}

.answer-risk {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.risk-label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #64748b;
}

.risk-bars {
  display: flex;
  gap: 4px;
}

.risk-bar {
  width: 30px;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.risk-bar.active {
  background: linear-gradient(90deg, #f59e0b 0%, #ef4444 100%);
}

.recommendations-section {
  margin-bottom: 2rem;
}

.recommendations-list {
  display: grid;
  gap: 1rem;
}

.recommendation-card {
  background: white;
  border-radius: 15px;
  padding: 1.5rem;
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  animation: slideInRight 0.6s ease;
  animation-fill-mode: both;
}

.recommendation-card:nth-child(1) { animation-delay: 0.7s; }
.recommendation-card:nth-child(2) { animation-delay: 0.8s; }
.recommendation-card:nth-child(3) { animation-delay: 0.9s; }
.recommendation-card:nth-child(4) { animation-delay: 1.0s; }
.recommendation-card:nth-child(5) { animation-delay: 1.1s; }
.recommendation-card:nth-child(6) { animation-delay: 1.2s; }

.recommendation-number {
  width: 30px;
  height: 30px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 900;
  flex-shrink: 0;
}

.recommendation-card p {
  flex: 1;
  font-size: 1rem;
  line-height: 1.5;
  color: #2c3e50;
}

.actions-section {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.action-button {
  padding: 1.2rem 2.5rem;
  border: none;
  border-radius: 15px;
  font-size: 1.2rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: fadeIn 1s ease 1.3s both;
}

.action-button.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.action-button.secondary {
  background: white;
  color: #667eea;
}

.action-button:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
}

.no-results {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  text-align: center;
  animation: fadeIn 0.5s ease;
}

.no-results-icon {
  font-size: 5rem;
  margin-bottom: 1rem;
}

.no-results h2 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.no-results p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.3);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .results-page {
    padding: 1rem;
  }
  
  .risk-badge {
    flex-direction: column;
    text-align: center;
  }
  
  .risk-icon {
    font-size: 4rem;
  }
  
  .answer-card {
    flex-direction: column;
  }
  
  .actions-section {
    flex-direction: column;
  }
  
  .action-button {
    width: 100%;
  }
}
</style>
