<template>
  <div class="question-container">
    <div class="question-text">{{ question.content }}</div>
    <div class="yes-no-buttons">
      <button
        v-for="option in sortedOptions"
        :key="option.option_id"
        class="yes-no-button"
        :class="[
          { selected: selectedOption === option.option_id },
          option.risk_value === 1 ? 'safe-option' : 'risky-option'
        ]"
        @click="selectOption(option.option_id)"
      >
        <span class="option-icon">{{ option.risk_value === 1 ? '👍' : '👎' }}</span>
        <span class="option-text">{{ option.content }}</span>
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

.yes-no-buttons {
  display: flex;
  gap: 2rem;
  justify-content: center;
  max-width: 700px;
  margin: 0 auto;
}

.yes-no-button {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 3rem 2rem;
  border: 4px solid transparent;
  border-radius: 25px;
  font-size: 1.5rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  animation: zoomIn 0.6s ease-out;
  min-height: 200px;
}

.yes-no-button:nth-child(1) { animation-delay: 0.1s; }
.yes-no-button:nth-child(2) { animation-delay: 0.2s; }

.safe-option {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
  color: #2d5f5d;
}

.safe-option:hover {
  transform: translateY(-10px) scale(1.05);
  box-shadow: 0 15px 40px rgba(168, 237, 234, 0.5);
}

.risky-option {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  color: #8b4513;
}

.risky-option:hover {
  transform: translateY(-10px) scale(1.05);
  box-shadow: 0 15px 40px rgba(252, 182, 159, 0.5);
}

.yes-no-button.selected {
  border-color: #fff;
  transform: scale(1.1) rotate(2deg);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
  animation: bounce 0.6s ease;
}

.safe-option.selected {
  background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 100%);
  color: white;
}

.risky-option.selected {
  background: linear-gradient(135deg, #f857a6 0%, #ff5858 100%);
  color: white;
}

.option-icon {
  font-size: 4rem;
  animation: float 2s ease-in-out infinite;
}

.yes-no-button.selected .option-icon {
  animation: spin 0.6s ease;
}

.option-text {
  font-size: 1.8rem;
  text-transform: uppercase;
  letter-spacing: 2px;
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

@keyframes zoomIn {
  from {
    opacity: 0;
    transform: scale(0.5);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes bounce {
  0%, 100% {
    transform: scale(1.1) rotate(2deg);
  }
  25% {
    transform: scale(1.15) rotate(-2deg);
  }
  50% {
    transform: scale(1.2) rotate(2deg);
  }
  75% {
    transform: scale(1.15) rotate(-2deg);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg) scale(1);
  }
  50% {
    transform: rotate(180deg) scale(1.3);
  }
  to {
    transform: rotate(360deg) scale(1);
  }
}

@media (max-width: 768px) {
  .question-text {
    font-size: 1.4rem;
  }
  
  .yes-no-buttons {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .yes-no-button {
    min-height: 150px;
    padding: 2rem 1.5rem;
  }
  
  .option-icon {
    font-size: 3rem;
  }
  
  .option-text {
    font-size: 1.4rem;
  }
}
</style>
