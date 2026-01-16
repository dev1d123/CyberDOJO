<script setup lang="ts">
import { computed } from 'vue';
import type { ShopItem } from './shop.types';

const props = defineProps<{
  item: ShopItem | null;
}>();

defineEmits<{
  (e: 'buy', value: ShopItem): void;
}>();

const isEmpty = computed(() => !props.item);
</script>

<template>
  <aside class="panel" aria-label="Detalles del artículo">
    <div v-if="isEmpty" class="empty">
      <div class="empty-icon" aria-hidden="true">🛍️</div>
      <h2 class="empty-title">¡Elige algo!</h2>
      <p class="empty-text">Haz click en una tarjeta para ver su descripción y comprar.</p>
    </div>

    <div v-else class="content">
      <div class="preview" :class="{ 'is-sound': item!.category === 'sounds' }">
        <img
          v-if="item!.category === 'pets'"
          class="preview-img"
          :src="item!.imageSrc"
          :alt="item!.alt"
          draggable="false"
        />

        <div v-else class="preview-sound" aria-hidden="true">
          <div class="sparkles">✨</div>
          <div class="speaker">🔊</div>
          <div class="wave">
            <span />
            <span />
            <span />
          </div>
        </div>
      </div>

      <div class="info">
        <div class="title-row">
          <h2 class="title">{{ item!.name }}</h2>
          <span class="tag">{{ item!.category === 'pets' ? 'Pets' : 'Sonidos' }}</span>
        </div>

        <p class="desc">{{ item!.description }}</p>

        <div class="price">
          <span class="coin" aria-hidden="true">💰</span>
          <span class="amount">{{ item!.price }}</span>
          <span class="unit">CyberCredits</span>
        </div>
      </div>

      <button class="buy" type="button" @click="$emit('buy', item!)">
        Comprar
      </button>

      <p class="legal">* Demo: por ahora solo muestra un alert.</p>
    </div>
  </aside>
</template>

<style scoped>
.panel {
  height: 100%;
  border-radius: 22px;
  padding: 18px;
  background: rgba(15, 15, 25, 0.72);
  border: 2px solid rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(10px);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.empty {
  height: 100%;
  display: grid;
  place-items: center;
  text-align: center;
  gap: 10px;
  color: rgba(255, 255, 255, 0.92);
}

.empty-icon {
  width: 88px;
  height: 88px;
  border-radius: 24px;
  display: grid;
  place-items: center;
  font-size: 2.2rem;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.18);
  animation: bob 2.4s ease-in-out infinite;
}

@keyframes bob {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.empty-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 1000;
}

.empty-text {
  margin: 0;
  max-width: 30ch;
  opacity: 0.92;
}

.content {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: 0;
}

.preview {
  flex: 0 0 auto;
  height: 220px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.18);
  display: grid;
  place-items: center;
  overflow: hidden;
}

.preview-img {
  width: min(240px, 90%);
  height: auto;
  object-fit: contain;
  filter: drop-shadow(0 12px 16px rgba(0, 0, 0, 0.35));
  animation: floaty 2.8s ease-in-out infinite;
}

@keyframes floaty {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.preview.is-sound {
  background: radial-gradient(circle at 20% 20%, rgba(255, 228, 64, 0.65), rgba(255, 107, 107, 0.18)),
    radial-gradient(circle at 90% 40%, rgba(46, 134, 222, 0.25), transparent 60%),
    radial-gradient(circle at 40% 90%, rgba(80, 227, 194, 0.28), transparent 60%);
}

.preview-sound {
  display: grid;
  place-items: center;
  gap: 10px;
  color: rgba(0, 0, 0, 0.78);
  font-weight: 1000;
}

.speaker {
  font-size: 3rem;
  animation: thump 900ms ease-in-out infinite;
}

@keyframes thump {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.08); }
}

.wave {
  display: flex;
  gap: 8px;
}

.wave span {
  width: 10px;
  height: 18px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.75);
  animation: eq 900ms ease-in-out infinite;
}

.wave span:nth-child(2) { animation-delay: 140ms; }
.wave span:nth-child(3) { animation-delay: 280ms; }

@keyframes eq {
  0%, 100% { height: 14px; opacity: 0.72; }
  50% { height: 40px; opacity: 1; }
}

.sparkles {
  position: absolute;
  margin-top: -160px;
  animation: sparkle 1.6s ease-in-out infinite;
}

@keyframes sparkle {
  0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.8; }
  50% { transform: translateY(-8px) rotate(8deg); opacity: 1; }
}

.info {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.title {
  margin: 0;
  color: #fff;
  font-weight: 1000;
  font-size: 1.35rem;
  line-height: 1.1;
}

.tag {
  flex: 0 0 auto;
  padding: 7px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.18);
  color: rgba(255, 255, 255, 0.92);
  font-weight: 900;
}

.desc {
  margin: 0;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.25;
  font-size: 1rem;

  display: -webkit-box;
  -webkit-line-clamp: 6;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.price {
  display: inline-flex;
  align-items: baseline;
  gap: 6px;
  align-self: flex-start;
  padding: 10px 12px;
  border-radius: 16px;
  background: rgba(254, 228, 64, 0.9);
  color: #111;
  font-weight: 1000;
  box-shadow: 0 14px 28px rgba(254, 228, 64, 0.22);
}

.amount {
  font-size: 1.3rem;
}

.unit {
  font-size: 0.95rem;
  opacity: 0.85;
}

.buy {
  border: 0;
  border-radius: 18px;
  padding: 14px 14px;
  cursor: pointer;
  font-weight: 1000;
  font-size: 1.15rem;
  color: #fff;
  background: linear-gradient(135deg, #ff6b6b, #ff8e53);
  box-shadow: 0 16px 34px rgba(255, 107, 107, 0.35);
  transition: transform 160ms ease, filter 160ms ease, box-shadow 160ms ease;
}

.buy:hover {
  transform: translateY(-4px) scale(1.02);
  filter: saturate(1.1);
  box-shadow: 0 20px 44px rgba(255, 107, 107, 0.42);
}

.buy:active {
  transform: translateY(-1px) scale(0.99);
}

.legal {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.72);
}
</style>
