<template>
  <div class="question-container">
    <div class="question-text">{{ question.content }}</div>

    <div class="age-card">
      <div class="age-row">
        <input
          v-model.number="age"
          class="age-input"
          type="number"
          inputmode="numeric"
          min="1"
          max="120"
          placeholder="Escribe tu edad"
          @input="emitIfValid"
        />
        <span class="age-suffix">años</span>
      </div>

      <div class="age-hint">Solo la usamos para adaptar el contenido.</div>

      <div class="quick">
        <button type="button" class="chip" @click="setAge(8)">8</button>
        <button type="button" class="chip" @click="setAge(10)">10</button>
        <button type="button" class="chip" @click="setAge(12)">12</button>
        <button type="button" class="chip" @click="setAge(14)">14</button>
        <button type="button" class="chip" @click="setAge(16)">16</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import type { OnboardingQuestion } from '@/dto/onboarding.dto';

const props = defineProps<{
  question: OnboardingQuestion;
  modelValue: number | null;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: number | null];
}>();

const age = ref<number | null>(props.modelValue ?? null);

watch(
  () => props.modelValue,
  (v) => {
    age.value = v ?? null;
  }
);

const normalize = (value: number | null) => {
  if (value == null || Number.isNaN(value)) return null;
  const clipped = Math.max(1, Math.min(120, Math.round(value)));
  return clipped;
};

const emitIfValid = () => {
  emit('update:modelValue', normalize(age.value));
};

const setAge = (value: number) => {
  age.value = value;
  emitIfValid();
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
  margin-bottom: 2rem;
  line-height: 1.4;
  animation: fadeInDown 0.6s ease-out;
}

.age-card {
  max-width: 520px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 22px;
  padding: 18px;
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.18);
  animation: fadeInUp 0.8s ease-out;
}

.age-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.age-input {
  flex: 1;
  height: 54px;
  border-radius: 16px;
  border: 2px solid rgba(102, 126, 234, 0.25);
  padding: 0 14px;
  font-size: 1.25rem;
  font-weight: 800;
  outline: none;
  transition: border-color 160ms ease, box-shadow 160ms ease;
}

.age-input:focus {
  border-color: rgba(118, 75, 162, 0.7);
  box-shadow: 0 0 0 6px rgba(118, 75, 162, 0.15);
}

.age-suffix {
  font-size: 1rem;
  font-weight: 800;
  color: #64748b;
}

.age-hint {
  margin-top: 10px;
  font-size: 0.95rem;
  color: #64748b;
}

.quick {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}

.chip {
  border: 1px solid rgba(102, 126, 234, 0.25);
  background: rgba(102, 126, 234, 0.08);
  color: #334155;
  padding: 10px 12px;
  border-radius: 999px;
  font-weight: 900;
  cursor: pointer;
  transition: transform 140ms ease, background 140ms ease;
}

.chip:hover {
  transform: translateY(-2px);
  background: rgba(102, 126, 234, 0.14);
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

@media (max-width: 768px) {
  .question-text {
    font-size: 1.4rem;
  }
}
</style>
