<template>
  <aside class="quiz-sidebar">
    <div class="panel time">
      <div class="label">Tiempo</div>
      <div class="value">00:32</div>
    </div>
    <div class="panel points">
      <div class="label">Puntos</div>
      <div class="value">350</div>
    </div>
    <button class="hint-btn" @click="$emit('toggle-hint')">💡 Mostrar Pista</button>
  </aside>
</template>

<script setup lang="ts">
</script>

<style scoped>
.quiz-sidebar{ display:flex; flex-direction:column; gap:12px }
.panel{ background:white; padding:12px; border-radius:12px; box-shadow:0 8px 30px rgba(0,0,0,0.06); text-align:center }
.panel .label{ font-size:12px; font-weight:800; color:rgba(30,75,102,0.6); text-transform:uppercase }
.panel .value{ font-weight:900; font-size:1.5rem; color:#1E4B66 }
.hint-btn{ background:white; padding:10px; border-radius:12px; font-weight:800; box-shadow:0 6px 0 rgba(0,0,0,0.04); cursor:pointer }
@media (max-width:900px){ .quiz-sidebar{ flex-direction:row; gap:8px } .panel{ flex:1 } }
</style>