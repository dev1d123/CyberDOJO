<template>
  <div class="mascot-widget">
    <div class="avatar-bg">
      <img :src="src" alt="mascot" />
    </div>
    <DialogPanel>
      <div class="mascot-text">
        <h2 class="mascot-title">{{ title }}</h2>
        <p class="mascot-sub">{{ subtitle }}</p>
      </div>
    </DialogPanel>
  </div>
</template>

<script setup lang="ts">
import DialogPanel from './DialogPanel.vue'

const props = defineProps<{ src: string; title: string; subtitle?: string }>();
</script>

<style scoped>
.mascot-widget{ display:flex; gap:16px; align-items:flex-start }
.avatar-bg{ width:96px; height:96px; border-radius:999px; background:white; padding:6px; display:grid; place-items:center; box-shadow:0 18px 40px rgba(0,0,0,0.12) }
.avatar-bg img{ width:100%; height:100%; object-fit:cover }
.mascot-text{ margin:0 }
.mascot-title{ margin:0; font-weight:900; color:#1E4B66; font-size:1.25rem }
.mascot-sub{ margin:6px 0 0 0; color:rgba(30,75,102,0.75); font-weight:700 }

@media (min-width: 768px) {
  .mascot-widget{ align-items:center }
}
</style>
