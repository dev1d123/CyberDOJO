<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import BackToDashboardButton from '../components/BackToDashboardButton.vue';
import ShopCategoryMenu from '../components/shop/ShopCategoryMenu.vue';
import ShopItemGrid from '../components/shop/ShopItemGrid.vue';
import ShopItemDetails from '../components/shop/ShopItemDetails.vue';
import type { ShopCategory, ShopItem } from '../components/shop/shop.types';

import pet1Img from '@/assets/images/pet1.png';
import pet2Img from '@/assets/images/pet2.png';
import pet3Img from '@/assets/images/pet3.png';
import pet4Img from '@/assets/images/pet4.png';
import pet5Img from '@/assets/images/pet5.png';

const activeCategory = ref<ShopCategory>('pets');

const pets: ShopItem[] = [
  {
    id: 'pet1',
    category: 'pets',
    name: 'Espada del Titán',
    description: 'Acero contra acero. Un guerrero valiente que te acompaña en cada batalla. ¡Enfrenta cada desafío con honor y valentía!',
    price: 150,
    imageSrc: pet1Img,
    alt: 'Pet1: Guerrero',
  },
  {
    id: 'pet2',
    category: 'pets',
    name: 'Marcha Victoriosa',
    description: 'Pasos firmes y disciplina de hierro. Un soldado leal que nunca falla. ¡El deber te llama!',
    price: 140,
    imageSrc: pet2Img,
    alt: 'Pet2: Soldado',
  },
  {
    id: 'pet3',
    category: 'pets',
    name: 'Grimorio Místico',
    description: 'Hechizos ancestrales y energía arcana. Un mago sabio que canaliza el poder del conocimiento. ¡Domina las artes místicas!',
    price: 180,
    imageSrc: pet3Img,
    alt: 'Pet3: Mago',
  },
  {
    id: 'pet4',
    category: 'pets',
    name: 'Sombra Furtiva',
    description: 'Sigiloso y astuto. Un bandido maestro de las sombras que nunca deja rastro. ¡Nadie te verá venir!',
    price: 130,
    imageSrc: pet4Img,
    alt: 'Pet4: Bandido',
  },
  {
    id: 'pet5',
    category: 'pets',
    name: 'Flecha Precisa',
    description: 'Arco tensado, objetivo fijo. Un arquero legendario con puntería perfecta. ¡Nunca falles tu blanco!',
    price: 160,
    imageSrc: pet5Img,
    alt: 'Pet5: Arquero',
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

</script>

<template>
  <div class="shop-page">
    <BackToDashboardButton />
    <header class="topbar">
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
  background-size: auto 100%;
  background-position: 0% center;
  background-repeat: repeat-x;
  animation: scrollBackground 30s cubic-bezier(0.4, 0.0, 0.2, 1) infinite;

  position: relative;
  display: flex;
  flex-direction: column;
  gap: clamp(10px, 1.6vh, 14px);
}

@keyframes scrollBackground {
  0% {
    background-position: 0% center;
  }
  100% {
    background-position: 100% center;
  }
}

.topbar {
  flex: 0 0 auto;
  display: grid;
  grid-template-columns: 1fr 170px;
  align-items: center;
  gap: 12px;

  padding: 12px 14px;
  border-radius: 22px;
  background: rgba(15, 15, 25, 0.72);
  border: 2px solid rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(10px);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
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
    grid-template-columns: 1fr;
    grid-template-rows: auto auto;
  }

  .credits-chip {
    justify-self: end;
    grid-column: 1;
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
