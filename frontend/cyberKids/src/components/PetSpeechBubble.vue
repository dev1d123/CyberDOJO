<script setup lang="ts">
import { computed, onUnmounted, ref, watch } from 'vue';
import { PetSpeech } from '@/stores/petSpeech.store';
import { hasPetEquipped } from '@/stores/petState.store';

const props = defineProps<{
  anchorEl: HTMLElement | null;
  isPetVisible: boolean;
  dimmed?: boolean;
}>();

const position = ref({ left: 0, top: 0 });
let rafId: number | null = null;

const shouldShow = computed(() => {
  // Solo mostrar si hay mascota equipada Y el resto de condiciones se cumplen
  return Boolean(
    hasPetEquipped.value && 
    props.isPetVisible && 
    props.anchorEl && 
    PetSpeech.isOpen.value && 
    PetSpeech.text.value
  );
});

function updatePosition() {
  if (!props.anchorEl) return;
  const rect = props.anchorEl.getBoundingClientRect();

  // Center above the pet
  const left = rect.left + rect.width / 2;
  const top = rect.top - 8;

  position.value = { left, top };
}

function startLoop() {
  if (rafId !== null) return;
  const loop = () => {
    if (shouldShow.value) {
      updatePosition();
      rafId = requestAnimationFrame(loop);
    } else {
      stopLoop();
    }
  };
  rafId = requestAnimationFrame(loop);
}

function stopLoop() {
  if (rafId !== null) {
    cancelAnimationFrame(rafId);
    rafId = null;
  }
}

watch(shouldShow, (show) => {
  if (show) startLoop();
  else stopLoop();
}, { immediate: true });

onUnmounted(() => {
  stopLoop();
});

const bubbleStyle = computed(() => ({
  left: `${position.value.left}px`,
  top: `${position.value.top}px`,
  opacity: props.dimmed ? 0.45 : 1,
}));

function handleBubbleClick() {
  // If the text is still being typed, reveal immediately.
  if (PetSpeech.isTyping.value) {
    PetSpeech.revealAll();
  }
}
</script>

<template>
  <Transition name="pet-bubble" appear>
    <div v-if="shouldShow" class="pet-speech" :style="bubbleStyle" role="status" aria-live="polite">
      <div class="bubble" @click="handleBubbleClick">
        <div class="text">
          {{ PetSpeech.typedText.value }}
          <span v-if="PetSpeech.isTyping.value" class="caret" aria-hidden="true">▍</span>
        </div>
      </div>
      <div class="arrow" />
    </div>
  </Transition>
</template>

<style scoped>
.pet-speech {
  position: fixed;
  transform: translate(-50%, -100%);
  z-index: 10000;
  pointer-events: none;
  transition: opacity 180ms ease;
}

.pet-bubble-enter-active {
  transition: transform 260ms cubic-bezier(0.2, 0.9, 0.2, 1.15), opacity 180ms ease;
}

.pet-bubble-leave-active {
  transition: transform 180ms ease, opacity 140ms ease;
}

.pet-bubble-enter-from,
.pet-bubble-leave-to {
  opacity: 0;
  transform: translate(-50%, -100%) translateY(18px) scale(0.2);
}

.pet-bubble-enter-to,
.pet-bubble-leave-from {
  opacity: 1;
  transform: translate(-50%, -100%) translateY(0) scale(1);
}

.bubble {
  pointer-events: auto;
  position: relative;
  max-width: 280px;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(0, 0, 0, 0.9);
  color: #ffffff;
  border: 2px solid rgba(255, 107, 107, 0.95);
  box-shadow: 0 10px 24px rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(6px);
  transform-origin: 50% 100%;
}

.text {
  font-size: 1.2rem;
  line-height: 1.3;
  white-space: normal;
}

.caret {
  display: inline-block;
  margin-left: 2px;
  opacity: 0.9;
  animation: caretBlink 900ms steps(2, jump-none) infinite;
}

@keyframes caretBlink {
  0%, 49% { opacity: 0.95; }
  50%, 100% { opacity: 0.2; }
}

.arrow {
  width: 0;
  height: 0;
  margin: 0 auto;
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-top: 12px solid rgba(255, 107, 107, 0.95);
  filter: drop-shadow(0 6px 10px rgba(0, 0, 0, 0.25));
}
</style>
