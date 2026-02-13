<template>
  <div class="options-grid">
    <button
      v-for="(opt, i) in options"
      :key="i"
      :class="['option', { disabled: opt.disabled, selected: selectedIndex === i, appear: true }]"
      :style="{ animationDelay: (i * 80) + 'ms' }"
      @click="onClick(i, opt.disabled)"
      :aria-disabled="opt.disabled"
    >
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
import { ref } from 'vue'
const props = defineProps<{ options: Array<{ text: string; disabled?: boolean }>; labels?: string[] }>()
const options = props.options || []
const labels = props.labels || []
const selectedIndex = ref(-1)
const emit = defineEmits<{
  select: [index: number]
  selectIndex: [index: number]
}>()
function onClick(i: number, disabled?: boolean){
  if(disabled) return
  selectedIndex.value = i
  emit('select', i)
  emit('selectIndex', i)
}
</script>

<style scoped>
.options-grid{ display:grid; grid-template-columns:1fr 1fr; gap:12px }
.option{ display:flex; gap:12px; align-items:center; padding:14px; border-radius:14px; border:1px solid rgba(0,0,0,0.04); background:white; cursor:pointer; transition:transform .14s ease, box-shadow .14s ease; transform-origin:center }
.option:active{ transform:translateY(2px) }
.option.disabled{ opacity:0.55; cursor:not-allowed }
.option-icon{ width:44px; height:44px; border-radius:10px; background:rgba(0,0,0,0.03); display:grid; place-items:center; font-weight:800 }
.option-text{ font-weight:800; color:#1E4B66 }

/* Appear + bounce animation */
.option.appear{ animation: optionBounce 520ms cubic-bezier(.22,.9,.36,1) both }
@keyframes optionBounce{
  0%{ transform: translateY(18px) scale(0.98); opacity:0 }
  60%{ transform: translateY(-6px) scale(1.02); opacity:1 }
  100%{ transform: translateY(0) scale(1); opacity:1 }
}

/* Selected enlarge */
.option.selected{ transform: scale(1.04); box-shadow: 0 10px 30px rgba(30,75,102,0.08) }

@media (max-width:720px){ .options-grid{ grid-template-columns:1fr } }
</style>