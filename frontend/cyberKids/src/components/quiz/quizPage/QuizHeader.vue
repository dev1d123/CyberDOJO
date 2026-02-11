<template>
  <header class="quiz-header">
    <div class="left">
      <div class="icon-box">
        <span class="quiz-icon">🔒</span>
      </div>
      <div class="titles">
        <h1 class="title">Quiz de Ciberseguridad</h1>
        <div class="meta">
          <span class="progress">Pregunta {{ current }} de {{ total }}</span>
          <span class="percent">{{ percent }}%</span>
        </div>
        <div class="progress-bar"><div class="progress-fill" :style="{ width: percent + '%' }"></div></div>
      </div>
    </div>
    <div class="right">
      <slot name="actions" />
    </div>
  </header>
</template>

<script setup lang="ts">
const props = defineProps<{ current?: number; total?: number; percent?: number }>()
</script>

<style scoped>
.quiz-header{ display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.95); padding:16px; border-radius:16px; box-shadow:0 10px 30px rgba(0,0,0,0.08); }
.quiz-header .left{ display:flex; gap:12px; align-items:center }
.icon-box{ width:56px; height:56px; border-radius:12px; background:var(--primary,#ffd166); display:grid; place-items:center }
.quiz-icon{ font-size:28px }
.titles .title{ margin:0; font-weight:800; font-family: 'Fredoka', sans-serif; color:#1E4B66 }
.meta{ display:flex; gap:10px; font-weight:700; color:rgba(30,75,102,0.7); font-size:13px; margin-top:6px }
.progress-bar{ width:260px; height:10px; background:rgba(0,0,0,0.04); border-radius:999px; overflow:hidden; margin-top:8px }
.progress-fill{ height:100%; background:linear-gradient(90deg,#7be8c3,#6ecff5); }
.right{ display:flex; align-items:center; gap:12px }
@media (max-width:720px){ .progress-bar{ width:160px } .quiz-header{ padding:12px } }
</style>