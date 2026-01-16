<script setup lang="ts">
import type { ShopCategory } from './shop.types';

defineProps<{
  activeCategory: ShopCategory;
  petsCount: number;
  soundsCount: number;
}>();

defineEmits<{
  (e: 'update:activeCategory', value: ShopCategory): void;
}>();
</script>

<template>
  <aside class="menu" aria-label="Categorías de tienda">
    <h2 class="menu-title">Categorías</h2>

    <button
      class="tab"
      :class="{ active: activeCategory === 'pets' }"
      type="button"
      @click="$emit('update:activeCategory', 'pets')"
    >
      <span class="tab-emoji" aria-hidden="true">🐾</span>
      <span class="tab-label">Pets</span>
      <span class="tab-count">{{ petsCount }}</span>
    </button>

    <button
      class="tab"
      :class="{ active: activeCategory === 'sounds' }"
      type="button"
      @click="$emit('update:activeCategory', 'sounds')"
    >
      <span class="tab-emoji" aria-hidden="true">🎵</span>
      <span class="tab-label">Sonidos</span>
      <span class="tab-count">{{ soundsCount }}</span>
    </button>

    <div class="tip">
      <div class="tip-badge">Tip</div>
      <p class="tip-text">Selecciona un item y mira los detalles a la derecha.</p>
    </div>
  </aside>
</template>

<style scoped>
.menu {
  height: 100%;
  border-radius: 22px;
  padding: 18px;
  background: rgba(15, 15, 25, 0.72);
  border: 2px solid rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(10px);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow: hidden;
}

.menu-title {
  margin: 0;
  color: #fff;
  font-size: 1.2rem;
  letter-spacing: 0.5px;
  text-shadow: 0 2px 0 rgba(0, 0, 0, 0.35);
}

.tab {
  display: grid;
  grid-template-columns: 44px 1fr auto;
  align-items: center;
  gap: 10px;

  width: 100%;
  border: 0;
  padding: 14px 14px;
  border-radius: 18px;
  cursor: pointer;

  color: #fff;
  background: linear-gradient(135deg, rgba(255, 107, 107, 0.85), rgba(255, 142, 83, 0.85));
  box-shadow: 0 10px 22px rgba(255, 107, 107, 0.25);

  transition: transform 180ms ease, box-shadow 180ms ease, filter 180ms ease;
}

.tab:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 14px 28px rgba(255, 107, 107, 0.35);
  filter: saturate(1.15);
}

.tab.active {
  outline: 3px solid rgba(255, 255, 255, 0.28);
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.35);
  background: linear-gradient(135deg, rgba(80, 227, 194, 0.9), rgba(46, 134, 222, 0.9));
}

.tab-emoji {
  font-size: 1.55rem;
  width: 44px;
  height: 44px;
  display: grid;
  place-items: center;
  background: rgba(0, 0, 0, 0.22);
  border-radius: 14px;
}

.tab-label {
  font-weight: 900;
  font-size: 1.08rem;
}

.tab-count {
  font-weight: 900;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.14);
}

.tip {
  margin-top: auto;
  border-radius: 18px;
  padding: 14px;
  background: rgba(255, 255, 255, 0.12);
  border: 1px dashed rgba(255, 255, 255, 0.22);
}

.tip-badge {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  font-weight: 900;
  font-size: 0.9rem;
  color: #111;
  background: #fee440;
  box-shadow: 0 8px 18px rgba(254, 228, 64, 0.25);
}

.tip-text {
  margin: 10px 0 0;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.2;
  font-size: 0.98rem;
}
</style>
