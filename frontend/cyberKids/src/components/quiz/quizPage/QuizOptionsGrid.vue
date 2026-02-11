<template>
  <div class="options-grid">
    <button v-for="(opt, i) in options" :key="i" :class="['option', { disabled: opt.disabled }]">
      <div class="option-left">
        <div class="option-icon">{{ labels[i] ?? String.fromCharCode(65+i) }}</div>
      </div>
      <div class="option-body">
        <div class="option-text">{{ opt.text }}</div>
      </div>
    </button>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue'
const props = defineProps<{ options: Array<{ text: string; disabled?: boolean }>; labels?: string[] }>()
const options = props.options || []
const labels = props.labels || []
</script>

<style scoped>
.options-grid{ display:grid; grid-template-columns:1fr 1fr; gap:12px }
.option{ display:flex; gap:12px; align-items:center; padding:14px; border-radius:14px; border:1px solid rgba(0,0,0,0.04); background:white; cursor:pointer; transition:transform .12s }
.option:active{ transform:translateY(2px) }
.option.disabled{ opacity:0.55; cursor:not-allowed }
.option-icon{ width:44px; height:44px; border-radius:10px; background:rgba(0,0,0,0.03); display:grid; place-items:center; font-weight:800 }
.option-text{ font-weight:800; color:#1E4B66 }
@media (max-width:720px){ .options-grid{ grid-template-columns:1fr } }
</style>