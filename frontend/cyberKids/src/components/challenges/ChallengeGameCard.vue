<template>
  <button class="card" type="button" @click="emit('click')">
    <div class="card-top">
      <div class="title-wrap">
        <h2 class="title">{{ title }}</h2>
        <p class="subtitle">{{ subtitle }}</p>
      </div>

      <div class="gif-wrap" aria-hidden="true">
        <img class="gif" :src="gifUrl" :alt="''" />
      </div>
    </div>

    <div class="card-body">
      <div class="mechanic">
        <span class="badge">¿Cómo se juega?</span>
        <p class="mechanic-text">{{ mechanic }}</p>
      </div>

      <ChallengePreview :type="previewType" />

      <div class="cta" aria-hidden="true">
        <span class="cta-pill">¡Jugar!</span>
        <span class="cta-note">(por ahora: demo)</span>
      </div>
    </div>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import ChallengePreview from './ChallengePreview.vue';

type PreviewType = 'trust' | 'chat' | 'hunt';

const emit = defineEmits<{ (event: 'click'): void }>();

const props = defineProps<{
  title: string;
  subtitle: string;
  mechanic: string;
  gifSrc: string;
  previewType: PreviewType;
}>();

const gifUrl = computed(() => props.gifSrc);
</script>

<style scoped>
.card {
  width: 100%;
  height: 100%;
  min-height: 0;
  border: none;
  border-radius: 26px;
  cursor: pointer;
  text-align: left;
  padding: 0;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 18px 55px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  position: relative;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 15% 15%, rgba(255, 255, 255, 0.45), transparent 55%),
    radial-gradient(circle at 85% 15%, rgba(255, 255, 255, 0.25), transparent 60%),
    linear-gradient(135deg, rgba(72, 198, 239, 0.26) 0%, rgba(111, 134, 214, 0.22) 45%, rgba(240, 147, 251, 0.2) 100%);
  opacity: 0.95;
}

.card > * {
  position: relative;
}

.card:hover {
  transform: translateY(-6px) scale(1.01);
  box-shadow: 0 26px 70px rgba(0, 0, 0, 0.33);
}

.card:active {
  transform: translateY(-2px) scale(0.995);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  padding: clamp(14px, 2.2vh, 20px) clamp(14px, 2vw, 20px);
}

.title-wrap {
  min-width: 0;
}

.title {
  margin: 0;
  font-size: clamp(1.15rem, 1.65vw, 1.6rem);
  font-weight: 1000;
  color: white;
  text-shadow: 3px 3px 8px rgba(0, 0, 0, 0.25);
}

.subtitle {
  margin: 6px 0 0 0;
  color: rgba(255, 255, 255, 0.92);
  font-weight: 800;
  font-size: clamp(0.9rem, 1.1vw, 1.05rem);
  text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.18);
}

.gif-wrap {
  flex: 0 0 auto;
  width: clamp(62px, 9vh, 90px);
  height: clamp(62px, 9vh, 90px);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.65);
  border: 2px solid rgba(255, 255, 255, 0.75);
  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.15);
  display: grid;
  place-items: center;
  animation: floaty 2.6s ease-in-out infinite;
}

@keyframes floaty {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-6px);
  }
}

.gif {
  width: 88%;
  height: 88%;
  object-fit: contain;
  image-rendering: auto;
}

.card-body {
  padding: 0 clamp(14px, 2vw, 20px) clamp(14px, 2.2vh, 20px);
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
}

.mechanic {
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.92);
  border: 2px solid rgba(255, 255, 255, 0.65);
  padding: 10px 12px;
}

.badge {
  display: inline-block;
  font-weight: 1000;
  font-size: 0.78rem;
  color: #4c1d95;
  background: rgba(124, 58, 237, 0.12);
  border: 2px solid rgba(124, 58, 237, 0.18);
  padding: 4px 10px;
  border-radius: 999px;
}

.mechanic-text {
  margin: 8px 0 0 0;
  font-weight: 800;
  color: #334155;
  font-size: clamp(0.9rem, 1.05vw, 1rem);
  line-height: 1.15;
}

.cta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-top: auto;
}

.cta-pill {
  background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%);
  color: white;
  font-weight: 1000;
  padding: 10px 14px;
  border-radius: 999px;
  box-shadow: 0 14px 30px rgba(255, 107, 107, 0.35);
  transform: rotate(-1deg);
}

.cta-note {
  font-weight: 900;
  color: rgba(255, 255, 255, 0.92);
  text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.18);
  font-size: 0.9rem;
}

@media (max-width: 820px) {
  .card-top {
    padding: 14px;
  }

  .card-body {
    padding: 0 14px 14px;
  }

  .cta-note {
    display: none;
  }
}
</style>
