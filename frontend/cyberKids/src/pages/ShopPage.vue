<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import ShopCategoryMenu from '../components/shop/ShopCategoryMenu.vue';
import ShopItemGrid from '../components/shop/ShopItemGrid.vue';
import ShopItemDetails from '../components/shop/ShopItemDetails.vue';
import type { ShopCategory, ShopItem } from '../components/shop/shop.types';

import pet1Img from '@/assets/images/pet1.png';
import pet2Img from '@/assets/images/pet2.png';
import pet3Img from '@/assets/images/pet3.png';
import pet4Img from '@/assets/images/pet4.png';
import pet5Img from '@/assets/images/pet5.png';

const router = useRouter();

const activeCategory = ref<ShopCategory>('pets');

const pets: ShopItem[] = [
  {
    id: 'pet1',
    category: 'pets',
    name: 'Perrito Guardián',
    description: 'Un perrito súper fiel que te acompaña en tus misiones. ¡Da puntos extra de ternura!',
    price: 120,
    imageSrc: pet1Img,
    alt: 'Pet1: un perrito',
  },
  {
    id: 'pet2',
    category: 'pets',
    name: 'Gata Ninja',
    description: 'Silenciosa, curiosa y rápida. Ideal para explorar secretos del ciber-dojo sin hacer ruido.',
    price: 110,
    imageSrc: pet2Img,
    alt: 'Pet2: una gata',
  },
  {
    id: 'pet3',
    category: 'pets',
    name: 'Sapo Saltarín',
    description: '¡Boing! Un sapo divertido que salta de alegría cuando aprendes algo nuevo.',
    price: 90,
    imageSrc: pet3Img,
    alt: 'Pet3: un sapo',
  },
  {
    id: 'pet4',
    category: 'pets',
    name: 'Pingüino Explorador',
    description: 'Un pingüino con espíritu aventurero. Perfecto para viajes helados y retos épicos.',
    price: 130,
    imageSrc: pet4Img,
    alt: 'Pet4: un pingüino',
  },
  {
    id: 'pet5',
    category: 'pets',
    name: 'Zorro Astuto',
    description: 'Rápido de mente y de patas. Un compañero brillante para estrategias y desafíos.',
    price: 150,
    imageSrc: pet5Img,
    alt: 'Pet5: un zorro',
  },
];

const sounds: ShopItem[] = [
  {
    id: 'sound-normal',
    category: 'sounds',
    theme: 'normal',
    name: 'Normal',
    description: 'Sonidos suaves y claros para jugar tranqui. Ideal para concentrarte.',
    price: 40,
  },
  {
    id: 'sound-fun',
    category: 'sounds',
    theme: 'fun',
    name: 'Divertidos',
    description: 'Efectos graciosos y chispeantes. ¡Perfecto para reírte mientras aprendes!',
    price: 75,
  },
  {
    id: 'sound-retro',
    category: 'sounds',
    theme: 'retro',
    name: 'Retro',
    description: 'Bips y bloops estilo arcade. Convierte el dojo en un juego clásico.',
    price: 90,
  },
  {
    id: 'sound-epic',
    category: 'sounds',
    theme: 'epic',
    name: 'Épico',
    description: 'Golpes, fanfarrias y vibes heroicas. ¡Cada victoria se siente legendaria!',
    price: 120,
  },
];

const itemsForCategory = computed(() => (activeCategory.value === 'pets' ? pets : sounds));

const selectedItemId = ref<string | undefined>(itemsForCategory.value[0]?.id);
const selectedItem = computed<ShopItem | null>(() => {
  const id = selectedItemId.value;
  if (!id) return null;
  return [...pets, ...sounds].find((x) => x.id === id) ?? null;
});

watch(
  () => activeCategory.value,
  () => {
    selectedItemId.value = itemsForCategory.value[0]?.id;
  }
);

const handleSelect = (item: ShopItem) => {
  selectedItemId.value = item.id;
};

const handleBuy = (item: ShopItem) => {
  alert(`Compra (demo): ${item.name} por ${item.price} CyberCredits`);
};

const goBack = () => {
  router.push('/dashboard');
};
</script>

<template>
  <div class="shop-page">
    <header class="topbar">
      <button class="back" type="button" @click="goBack">⟵ Volver</button>
      <div class="title-wrap">
        <h1 class="title">Tienda</h1>
        <p class="subtitle">Pets y Sonidos para personalizar tu aventura</p>
      </div>
      <div class="credits-chip" aria-label="Moneda">
        <span class="coin" aria-hidden="true">💰</span>
        <span class="text">CyberCredits</span>
      </div>
    </header>

    <main class="layout">
      <ShopCategoryMenu
        class="left"
        :active-category="activeCategory"
        :pets-count="pets.length"
        :sounds-count="sounds.length"
        @update:active-category="activeCategory = $event"
      />

      <ShopItemGrid
        class="center"
        :items="itemsForCategory"
        :selected-id="selectedItemId"
        @select="handleSelect"
      />

      <ShopItemDetails class="right" :item="selectedItem" @buy="handleBuy" />
    </main>

    <div class="bubbles" aria-hidden="true">
      <span class="b b1" />
      <span class="b b2" />
      <span class="b b3" />
      <span class="b b4" />
    </div>
  </div>
</template>

<style scoped>
.shop-page {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  box-sizing: border-box;

  padding: clamp(12px, 2.2vh, 22px);

  background-image:
    linear-gradient(135deg, rgba(0, 0, 0, 0.18), rgba(0, 0, 0, 0.12)),
    url('@/assets/images/shopBackground.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;

  position: relative;
  display: flex;
  flex-direction: column;
  gap: clamp(10px, 1.6vh, 14px);
}

.topbar {
  flex: 0 0 auto;
  display: grid;
  grid-template-columns: 160px 1fr 170px;
  align-items: center;
  gap: 12px;

  padding: 12px 14px;
  border-radius: 22px;
  background: rgba(15, 15, 25, 0.72);
  border: 2px solid rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(10px);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
}

.back {
  justify-self: start;
  border: 0;
  border-radius: 16px;
  padding: 12px 14px;
  cursor: pointer;
  font-weight: 1000;
  color: #111;
  background: #fee440;
  box-shadow: 0 14px 26px rgba(254, 228, 64, 0.22);
  transition: transform 160ms ease, filter 160ms ease;
}

.back:hover {
  transform: translateY(-3px);
  filter: saturate(1.05);
}

.title-wrap {
  text-align: center;
  color: #fff;
  line-height: 1.1;
}

.title {
  margin: 0;
  font-size: clamp(1.6rem, 3.3vh, 2.3rem);
  font-weight: 1000;
  text-shadow: 0 3px 0 rgba(0, 0, 0, 0.35);
}

.subtitle {
  margin: 6px 0 0;
  opacity: 0.92;
  font-weight: 800;
}

.credits-chip {
  justify-self: end;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.18);
  color: rgba(255, 255, 255, 0.92);
  font-weight: 1000;
}

.credits-chip .coin {
  animation: coinSpin 2.8s linear infinite;
}

@keyframes coinSpin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.layout {
  flex: 1 1 auto;
  min-height: 0;

  display: grid;
  grid-template-columns: 270px 1fr 330px;
  gap: 16px;
}

.left,
.center,
.right {
  min-height: 0;
}

/* playful floating bubbles */
.bubbles {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}

.b {
  position: absolute;
  width: 120px;
  height: 120px;
  border-radius: 999px;
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.55), rgba(255, 255, 255, 0.05));
  border: 1px solid rgba(255, 255, 255, 0.12);
  filter: blur(0.2px);
  opacity: 0.6;
  animation: bubble 10s ease-in-out infinite;
}

.b1 { left: 4%; top: 65%; animation-delay: 0s; transform: scale(0.85); }
.b2 { left: 18%; top: 15%; animation-delay: 1.4s; transform: scale(0.65); }
.b3 { right: 12%; top: 18%; animation-delay: 2.2s; transform: scale(0.75); }
.b4 { right: 5%; top: 70%; animation-delay: 3.1s; transform: scale(0.9); }

@keyframes bubble {
  0%, 100% { transform: translateY(0) scale(0.85); }
  50% { transform: translateY(-18px) scale(0.9); }
}

@media (max-width: 1200px) {
  .layout {
    grid-template-columns: 250px 1fr 310px;
  }
}

@media (max-width: 980px) {
  .topbar {
    grid-template-columns: 140px 1fr;
    grid-template-rows: auto auto;
  }

  .credits-chip {
    justify-self: end;
    grid-column: 2;
    grid-row: 1;
  }

  .layout {
    grid-template-columns: 240px 1fr;
    grid-template-rows: 1fr 1fr;
  }

  .right {
    grid-column: 1 / -1;
  }
}
</style>
