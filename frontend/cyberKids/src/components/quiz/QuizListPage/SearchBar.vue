<template>
  <div class="search-bar">
    <span class="material-icons-round">search</span>
    <input :placeholder="placeholder" :value="modelValue" @input="$emit('update:modelValue', $event.target.value)" />
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ modelValue: string; placeholder?: string }>();
const emit = defineEmits(['update:modelValue']);
</script>

<style scoped>
.search-bar{ display:flex; align-items:center; gap:10px; background:rgba(255,255,255,0.95); padding:8px 12px; border-radius:12px }
.search-bar input{ border:none; outline:none; font-weight:700 }
.search-bar .material-icons-round{ color:rgba(30,75,102,0.45) }
</style>
