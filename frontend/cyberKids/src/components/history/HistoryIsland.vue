<template>
  <button
    class="island"
    :class="{ selected }"
    :style="{ left: level.x, top: level.y }"
    type="button"
    @click="$emit('select', level)"
  >
    <span class="island-label" aria-hidden="true">
      Nivel {{ level.id }} - "{{ level.name }}"
    </span>
    <img class="island-image" :src="islandUrl" alt="Isla" />
  </button>
</template>

<script setup lang="ts">
import type { HistoryLevelDto } from '../../dto/history.dto';

defineProps<{
  level: HistoryLevelDto;
  islandUrl: string;
  selected: boolean;
}>();

defineEmits<{
  (e: 'select', level: HistoryLevelDto): void;
}>();
</script>

<style scoped>
.island {
  position: absolute;
  transform: translate(-50%, -50%) !important;
  background: transparent !important;
  border: 0 !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  padding: 0 !important;
  cursor: pointer;
  display: grid;
  place-items: center;
  gap: 10px;
  outline: none !important;
  isolation: isolate;
}

.island:hover {
  transform: translate(-50%, -50%) !important;
  box-shadow: none !important;
}

.island:focus,
.island:focus-visible {
  outline: none !important;
  box-shadow: none !important;
}

.island::after {
  content: '';
  position: absolute;
  inset: -18px;
  border-radius: 999px;
  background: radial-gradient(
    circle,
    rgba(72, 198, 239, 0.55) 0%,
    rgba(111, 134, 214, 0.22) 35%,
    rgba(240, 147, 251, 0) 70%
  );
  filter: blur(10px);
  opacity: 0.85;
  z-index: 0;
  animation: islandGlow 2.6s ease-in-out infinite;
}

.island-image {
  width: clamp(74px, 10vw, 120px);
  height: auto;
  transition: transform 0.2s ease, filter 0.2s ease;
  filter:
    drop-shadow(0 10px 18px rgba(0, 0, 0, 0.28))
    drop-shadow(0 0 14px rgba(72, 198, 239, 0.35));
  animation: islandZoom 2.6s ease-in-out infinite;
  position: relative;
  z-index: 1;
}

.island-label {
  color: white;
  font-weight: 800;
  font-size: clamp(0.9rem, 1.2vw, 1.15rem);
  text-shadow: 2px 2px 0px rgba(0, 0, 0, 0.35);
  background: rgba(0, 0, 0, 0.35);
  border: 2px solid rgba(255, 255, 255, 0.55);
  padding: 0.35rem 0.8rem;
  border-radius: 999px;
  animation: labelFloat 2.4s ease-in-out infinite;
  position: relative;
  z-index: 1;
}

@keyframes labelFloat {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-6px); }
}

.island:hover .island-image {
  transform: scale(1.08);
  filter:
    drop-shadow(0 16px 24px rgba(0, 0, 0, 0.35))
    drop-shadow(0 0 18px rgba(72, 198, 239, 0.45));
}

.island:hover .island-label {
  background: rgba(255, 255, 255, 0.18);
  border-color: rgba(255, 255, 255, 0.85);
}

.island.selected .island-image {
  transform: scale(1.1);
}

.island:hover::after {
  opacity: 1;
  animation-duration: 1.8s;
}

@keyframes islandGlow {
  0%, 100% {
    transform: scale(0.92);
    filter: blur(10px);
    opacity: 0.75;
  }
  50% {
    transform: scale(1.06);
    filter: blur(14px);
    opacity: 0.98;
  }
}

@keyframes islandZoom {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.085); }
}
</style>
