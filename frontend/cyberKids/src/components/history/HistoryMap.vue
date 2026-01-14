<template>
  <div class="map-layer">
    <svg class="path-svg" viewBox="0 0 1000 600" preserveAspectRatio="none" aria-hidden="true">
      <path
        class="path-line"
        d="M 120 520
           C 210 500 235 470 260 440
           C 300 390 230 360 170 320
           C 130 290 220 260 340 240
           C 470 220 470 280 520 300
           C 600 330 640 250 700 220
           C 780 180 860 270 820 360
           C 780 430 720 470 650 480"
      />
    </svg>

    <HistoryIsland
      v-for="level in levels"
      :key="level.id"
      :level="level"
      :selected="selectedLevelId === level.id"
      :island-url="islandUrl"
      @select="$emit('select', $event)"
    />
  </div>
</template>

<script setup lang="ts">
import HistoryIsland from './HistoryIsland.vue';
import type { HistoryLevelDto } from '../../dto/history.dto';

defineProps<{
  levels: HistoryLevelDto[];
  selectedLevelId: number | null;
  islandUrl: string;
}>();

defineEmits<{
  (e: 'select', level: HistoryLevelDto): void;
}>();
</script>

<style scoped>
.map-layer {
  position: relative;
  width: min(1100px, 100%);
  height: 100%;
  border: 0 !important;
  outline: 0 !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  background: transparent !important;
}

.path-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.path-line {
  fill: none;
  stroke: rgba(255, 255, 255, 0.95);
  stroke-width: 6;
  stroke-linecap: round;
  stroke-dasharray: 10 14;
  filter: drop-shadow(0 6px 10px rgba(0, 0, 0, 0.25));
}
</style>
