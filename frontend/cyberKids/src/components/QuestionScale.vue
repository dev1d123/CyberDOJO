<template>
  <div class="question-container">
    <div class="question-text">{{ question.content }}</div>
    <div class="scale-container">
      <button
        v-for="option in sortedOptions"
        :key="option.option_id"
        class="scale-button"
        :class="{ selected: selectedOption === option.option_id }"
        :style="{ '--risk-color': getRiskColor(option.risk_value) }"
        @click="selectOption(option.option_id)"
      >
        <div class="scale-number">{{ option.risk_value }}</div>
        <div class="scale-label">{{ option.content }}</div>
      </button>
    </div>
    <div class="scale-labels">
      <span class="label-start">Menos</span>
      <span class="label-end">Más</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import type { OnboardingQuestion } from '@/dto/onboarding.dto';

const props = defineProps<{
  question: OnboardingQuestion;
  modelValue: number | null;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: number];
}>();

const selectedOption = ref<number | null>(props.modelValue);

const sortedOptions = computed(() => {
  return [...props.question.options].sort((a, b) => a.display_order - b.display_order);
});

const selectOption = (optionId: number) => {
  selectedOption.value = optionId;
  emit('update:modelValue', optionId);
};

const getRiskColor = (riskValue: number): string => {
  const colors = [
    '#4ade80', // Verde
    '#86efac', // Verde claro
    '#fbbf24', // Amarillo
    '#fb923c', // Naranja
    '#f87171'  // Rojo
  ];
  return colors[riskValue - 1] || colors[0];
};
</script>

<style scoped>
.question-container {
  width: 100%;
  padding: 2rem;
}

.question-text {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2c3e50;
  text-align: center;
  margin-bottom: 3rem;
  line-height: 1.4;
  animation: fadeInDown 0.6s ease-out;
}

.scale-container {
  display: flex;
  gap: 1rem;
  justify-content: center;
  max-width: 800px;
  margin: 0 auto 1.5rem;
  animation: fadeInUp 0.8s ease-out;
}

.scale-button {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1.5rem 1rem;
  background: var(--risk-color);
  border: 3px solid transparent;
  border-radius: 20px;
  color: white;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  animation: scaleUp 0.5s ease-out;
  animation-fill-mode: both;
  min-height: 130px;
}

.scale-button:nth-child(1) { animation-delay: 0.1s; }
.scale-button:nth-child(2) { animation-delay: 0.2s; }
.scale-button:nth-child(3) { animation-delay: 0.3s; }
.scale-button:nth-child(4) { animation-delay: 0.4s; }
.scale-button:nth-child(5) { animation-delay: 0.5s; }

.scale-button:hover {
  transform: translateY(-15px) scale(1.1);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
}

.scale-button.selected {
  border-color: #fff;
  transform: translateY(-20px) scale(1.15);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
  animation: wiggle 0.5s ease;
}

.scale-number {
  font-size: 3rem;
  font-weight: 900;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
  animation: bounce 2s ease-in-out infinite;
}

.scale-button.selected .scale-number {
  animation: heartbeat 0.8s ease infinite;
}

.scale-label {
  font-size: 0.9rem;
  font-weight: 600;
  text-align: center;
  opacity: 0.9;
  line-height: 1.2;
}

.scale-labels {
  display: flex;
  justify-content: space-between;
  max-width: 800px;
  margin: 0 auto;
  padding: 0 1rem;
  font-size: 1.2rem;
  font-weight: 700;
  color: #64748b;
  animation: fadeIn 1s ease-out 0.5s both;
}

.label-start {
  color: #4ade80;
}

.label-end {
  color: #f87171;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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

@keyframes scaleUp {
  from {
    opacity: 0;
    transform: scale(0.3);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes wiggle {
  0%, 100% {
    transform: translateY(-20px) scale(1.15) rotate(0deg);
  }
  25% {
    transform: translateY(-20px) scale(1.15) rotate(-5deg);
  }
  75% {
    transform: translateY(-20px) scale(1.15) rotate(5deg);
  }
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
}

@keyframes heartbeat {
  0%, 100% {
    transform: scale(1);
  }
  25% {
    transform: scale(1.2);
  }
  50% {
    transform: scale(1);
  }
  75% {
    transform: scale(1.2);
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
  .question-text {
    font-size: 1.4rem;
  }
  
  .scale-container {
    gap: 0.5rem;
  }
  
  .scale-button {
    padding: 1rem 0.5rem;
    min-height: 110px;
  }
  
  .scale-number {
    font-size: 2rem;
  }
  
  .scale-label {
    font-size: 0.7rem;
  }
  
  .scale-labels {
    font-size: 1rem;
  }
}
</style>
