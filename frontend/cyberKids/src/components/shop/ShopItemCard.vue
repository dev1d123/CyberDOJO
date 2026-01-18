<script setup lang="ts">
import { computed } from 'vue';
import type { ShopItem } from './shop.types';

const props = defineProps<{
  item: ShopItem;
  selected?: boolean;
}>();

defineEmits<{
  (e: 'select', value: ShopItem): void;
}>();

const themeClass = computed(() => {
  if (props.item.category !== 'sounds') return '';
  return `sound-${props.item.theme}`;
});
</script>

<template>
  <button
    class="card"
    :class="[{ selected: !!selected }, themeClass]"
    type="button"
    @click="$emit('select', item)"
  >
    <div class="media" :class="{ 'is-sound': item.category === 'sounds' }">
      <img
        v-if="item.category === 'pets'"
        class="pet-img"
        :src="item.imageSrc"
        :alt="item.alt"
        draggable="false"
      />

      <div v-else class="sound-visual" aria-hidden="true">
        <div class="bars">
          <span class="bar" />
          <span class="bar" />
          <span class="bar" />
          <span class="bar" />
          <span class="bar" />
        </div>
        <div class="sound-label">{{ item.name }}</div>
      </div>
    </div>

    <div class="meta">
      <div class="name">{{ item.name }}</div>
      <div class="price">
        <span class="coin" aria-hidden="true">💰</span>
        <span class="amount">{{ item.price }}</span>
        <span class="unit">CyberCredits</span>
      </div>
    </div>
  </button>
</template>

<style scoped>
.card {
  width: 100%;
  border: 0;
  padding: 12px;
  border-radius: 22px;
  cursor: pointer;

  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.18);

  display: grid;
  grid-template-rows: 1fr auto;
  gap: 10px;

  transform: translateZ(0);
  transition: transform 180ms ease, box-shadow 180ms ease, filter 180ms ease;
}

.card:hover {
  transform: translateY(-6px) rotate(-0.3deg);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.22);
  filter: saturate(1.05);
}

.card.selected {
  outline: 4px solid rgba(80, 227, 194, 0.95);
  box-shadow: 0 22px 46px rgba(80, 227, 194, 0.22);
  transform: translateY(-8px) scale(1.02);
}

.media {
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.25), rgba(240, 147, 251, 0.22));
  border: 2px solid rgba(0, 0, 0, 0.08);
  display: grid;
  place-items: center;
  min-height: 150px;
  overflow: hidden;
  position: relative;
}

.pet-img {
  width: 90%;
  height: auto;
  max-height: none;
  object-fit: contain;
  filter: drop-shadow(0 10px 14px rgba(0, 0, 0, 0.25));
  animation: slideVertical 8s cubic-bezier(0.4, 0.0, 0.2, 1) infinite;
}

@keyframes slideVertical {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-30%);
  }
}

@keyframes floaty {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.meta {
  display: grid;
  gap: 6px;
}

.name {
  font-weight: 900;
  color: #141414;
  text-align: center;
  font-size: 1.05rem;
  line-height: 1.1;
}

.price {
  display: flex;
  justify-content: center;
  align-items: baseline;
  gap: 6px;

  background: rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 999px;
  padding: 8px 10px;
}

.coin {
  font-size: 1.1rem;
}

.amount {
  font-weight: 1000;
  font-size: 1.1rem;
  color: #111;
}

.unit {
  font-size: 0.9rem;
  color: rgba(0, 0, 0, 0.65);
  font-weight: 700;
}

/* Sound visual */
.media.is-sound {
  background: radial-gradient(circle at 20% 20%, rgba(255, 228, 64, 0.7), rgba(255, 107, 107, 0.18)),
    radial-gradient(circle at 90% 40%, rgba(46, 134, 222, 0.25), transparent 60%),
    radial-gradient(circle at 40% 90%, rgba(80, 227, 194, 0.28), transparent 60%);
}

.sound-visual {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  gap: 10px;
}

.bars {
  display: flex;
  gap: 7px;
  align-items: flex-end;
}

.bar {
  width: 10px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.75);
  height: 20px;
  animation: eq 900ms ease-in-out infinite;
}

.bar:nth-child(2) { animation-delay: 100ms; }
.bar:nth-child(3) { animation-delay: 200ms; }
.bar:nth-child(4) { animation-delay: 300ms; }
.bar:nth-child(5) { animation-delay: 400ms; }

@keyframes eq {
  0%, 100% { height: 16px; opacity: 0.75; }
  50% { height: 44px; opacity: 1; }
}

.sound-label {
  font-weight: 1000;
  font-size: 1.05rem;
  color: rgba(0, 0, 0, 0.82);
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.5);
}

/* Per-theme accents */
.card.sound-normal .bar { background: rgba(0, 0, 0, 0.75); }
.card.sound-fun .bar { background: rgba(255, 107, 107, 0.92); }
.card.sound-retro .bar { background: rgba(46, 134, 222, 0.92); }
.card.sound-epic .bar { background: rgba(142, 68, 173, 0.92); }
</style>
