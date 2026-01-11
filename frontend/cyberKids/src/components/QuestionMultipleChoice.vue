<template>
  <div class="question-container">
    <div class="question-text">{{ question.content }}</div>
    <div class="options-grid">
      <button
        v-for="option in sortedOptions"
        :key="option.option_id"
        class="option-button"
        :class="{ selected: selectedOption === option.option_id }"
        @click="selectOption(option.option_id)"
      >
        <span class="option-emoji">{{ getEmoji(option.risk_value) }}</span>
        <span class="option-text">{{ option.content }}</span>
        <div v-if="selectedOption === option.option_id" class="checkmark">✓</div>
      </button>
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

const getEmoji = (riskValue: number): string => {
  if (riskValue <= 1) return '😊';
  if (riskValue <= 2) return '🙂';
  if (riskValue <= 3) return '😐';
  if (riskValue <= 4) return '😟';
  return '😰';
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

.options-grid {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  max-width: 600px;
  margin: 0 auto;
}

.option-button {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: 3px solid transparent;
  border-radius: 20px;
  color: white;
  font-size: 1.3rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: slideInLeft 0.5s ease-out;
  animation-fill-mode: both;
}

.option-button:nth-child(1) { animation-delay: 0.1s; }
.option-button:nth-child(2) { animation-delay: 0.2s; }
.option-button:nth-child(3) { animation-delay: 0.3s; }
.option-button:nth-child(4) { animation-delay: 0.4s; }
.option-button:nth-child(5) { animation-delay: 0.5s; }

.option-button:hover {
  transform: translateX(10px) scale(1.02);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.option-button.selected {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border-color: #fff;
  transform: scale(1.05);
  box-shadow: 0 10px 30px rgba(245, 87, 108, 0.5);
  animation: pulse 0.6s ease;
}

.option-emoji {
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 2.5rem;
}

.option-text {
  flex: 1;
  text-align: left;
}

.checkmark {
  font-size: 2rem;
  font-weight: bold;
  color: white;
  animation: scaleIn 0.3s ease;
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

@keyframes pulse {
  0%, 100% {
    transform: scale(1.05);
  }
  50% {
    transform: scale(1.1);
  }
}

@keyframes scaleIn {
  from {
    transform: scale(0);
  }
  to {
    transform: scale(1);
  }
}

@media (max-width: 768px) {
  .question-text {
    font-size: 1.4rem;
  }
  
  .option-button {
    font-size: 1.1rem;
    padding: 1.2rem 1.5rem;
  }
  
  .option-emoji {
    font-size: 1.5rem;
  }
}
</style>
