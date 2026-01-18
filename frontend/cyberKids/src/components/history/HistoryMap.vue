<template>
  <div class="map-layer">
    <svg class="path-svg" viewBox="0 0 1000 600" preserveAspectRatio="none" aria-hidden="true">
      <path
        class="path-line"
        d="M 260 432
           Q 200 470 120 312
           Q 100 250 340 204
           Q 450 180 560 300
           Q 620 360 760 180
           Q 850 80 920 348"
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
