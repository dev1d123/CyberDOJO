<template>
  <section class="question-panel question-entrance">
    <div class="badge">{{ badge }}</div>
    <div class="question-content">
      <div class="question-icon">🎯</div>
      <h2 class="question-title">{{ question }}</h2>
      <p class="question-sub">{{ hint }}</p>
    </div>
  </section>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'
const props = defineProps<{ badge?: string; question: string; hint?: string }>()
const badge = props.badge ?? ''
const question = props.question
const hint = props.hint ?? ''
</script>

<style scoped>
.question-panel{ background:white; padding:24px; border-radius:20px; box-shadow:0 10px 40px rgba(0,0,0,0.06); text-align:center; overflow:visible }
.question-entrance{ animation: questionFlip 420ms cubic-bezier(.2,.9,.3,1) both }
.question-icon{ transform-origin: center; }
.badge{ position:absolute; transform:translateY(-50%); background:#ff7a7a; color:white; padding:6px 10px; border-radius:999px; font-weight:800 }
.question-content{ display:flex; flex-direction:column; align-items:center; gap:12px }
.question-icon{ font-size:48px }
.question-title{ margin:0; font-family:'Fredoka',sans-serif; font-size:1.6rem; color:#1E4B66 }
.question-sub{ margin:0; color:rgba(30,75,102,0.65); font-weight:700 }
@media (max-width:720px){ .question-title{ font-size:1.25rem } }

@keyframes questionFlip {
  0% { transform: rotateY(-25deg) scale(.98); opacity: 0 }
  60% { transform: rotateY(10deg) scale(1.02); opacity: 1 }
  100% { transform: rotateY(0deg) scale(1); opacity: 1 }
}
</style>