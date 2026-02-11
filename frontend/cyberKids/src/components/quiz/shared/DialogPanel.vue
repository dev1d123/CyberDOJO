<template>
  <div class="dialog-panel">
    <div class="dialog-content">
      <slot />
    </div>
    <div class="dialog-corner" aria-hidden="true"></div>
  </div>
</template>

<script setup lang="ts">
// Simple wrapper panel that renders slot content inside a styled dialog card
</script>

<style scoped>
.dialog-panel {
  position: relative;
  background: rgba(255,255,255,0.98);
  border-radius: 24px;
  padding: 18px 20px;
  box-shadow: 0 10px 40px -10px rgba(0,0,0,0.12);
  border: 1px solid rgba(255,255,255,0.6);
  display: flex;
  align-items: center;
  min-width: 220px;
}
.dialog-content { flex: 1 }
.dialog-corner {
  position: absolute;
  top: 0;
  left: -12px;
  width: 18px;
  height: 18px;
  background: rgba(255,255,255,0.98);
  transform: skewX(-12deg) translateY(-6px);
  border-top-left-radius: 6px;
  box-shadow: none;
}

/* Responsive tweaks similar to the original layout */
@media (min-width: 768px) {
  .dialog-panel { padding: 20px 24px; min-width: 360px }
}
</style>
