<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue';
import confetti from 'canvas-confetti';
import BackToDashboardButton from '../components/BackToDashboardButton.vue';
import ShopCategoryMenu from '../components/shop/ShopCategoryMenu.vue';
import ShopItemGrid from '../components/shop/ShopItemGrid.vue';
import ShopItemDetails from '../components/shop/ShopItemDetails.vue';
import type { ShopCategory, ShopItem } from '../components/shop/shop.types';
import { PetService } from '../services/pet.service';
import { UserService } from '../services/user.service';
import petsData from '../data/pets.json';

import pet1Img from '@/assets/images/pet1.png';
import pet2Img from '@/assets/images/pet2.png';
import pet3Img from '@/assets/images/pet3.png';
import pet4Img from '@/assets/images/pet4.png';
import pet5Img from '@/assets/images/pet5.png';

const activeCategory = ref<ShopCategory>('pets');
const userPetIds = ref<number[]>([]);
const currentCybercreds = ref<number>(0);
const loading = ref(true);
const toastMessage = ref<string>('');
const toastVisible = ref(false);

const petImageMap: Record<number, string> = {
  7: pet1Img,
  8: pet2Img,
  9: pet3Img,
  10: pet4Img,
  11: pet5Img,
};

const pets: ShopItem[] = petsData.map((pet) => ({
  id: `pet${pet.pet_id}`,
  petId: pet.pet_id,
  category: 'pets',
  name: pet.name,
  description: pet.description,
  price: pet.cybercreds_cost,
  imageSrc: petImageMap[pet.pet_id] || pet1Img,
  alt: `${pet.name}`,
  isDefault: pet.is_default,
}));

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

const showToast = (message: string) => {
  toastMessage.value = message;
  toastVisible.value = true;
  setTimeout(() => {
    toastVisible.value = false;
  }, 3000);
};

const triggerConfetti = () => {
  const duration = 3 * 1000;
  const animationEnd = Date.now() + duration;
  const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 9999 };

  const randomInRange = (min: number, max: number) => Math.random() * (max - min) + min;

  const interval = window.setInterval(() => {
    const timeLeft = animationEnd - Date.now();

    if (timeLeft <= 0) {
      return clearInterval(interval);
    }

    const particleCount = 50 * (timeLeft / duration);
    confetti({
      ...defaults,
      particleCount,
      origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 },
    });
    confetti({
      ...defaults,
      particleCount,
      origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 },
    });
  }, 250);
};

const handleBuy = async (item: ShopItem) => {
  if (item.category !== 'pets') {
    alert('Solo se pueden comprar pets por ahora');
    return;
  }

  const petItem = item as any;
  if (!petItem.petId) {
    alert('Error: No se puede comprar este item');
    return;
  }

  // Verificar si ya lo tiene
  if (userPetIds.value.includes(petItem.petId)) {
    showToast('¡Ya tienes esta mascota!');
    return;
  }

  // Verificar si tiene suficientes cybercreds
  if (currentCybercreds.value < item.price) {
    showToast('No tienes suficientes CyberCredits');
    return;
  }

  try {
    console.log('💳 [ShopPage] Intentando comprar pet_id:', petItem.petId);
    const response = await PetService.buyPet(petItem.petId);
    console.log('✅ [ShopPage] Respuesta de compra:', response);
    
    userPetIds.value.push(petItem.petId);
    // El backend devuelve 'remaining_cybercreds', no 'cybercreds'
    currentCybercreds.value = response.remaining_cybercreds || response.cybercreds || currentCybercreds.value;
    
    // Mostrar confeti y toast
    triggerConfetti();
    showToast(`¡Compraste ${item.name}! 🎉`);
  } catch (error: any) {
    console.error('❌ [ShopPage] Error comprando pet:', error);
    showToast(error?.error || 'Error al comprar la mascota');
  }
};

const loadUserData = async () => {
  loading.value = true;
  try {
    console.log('🔄 [ShopPage] Cargando datos del usuario...');
    const user = await UserService.getCurrentUser();
    console.log('👤 [ShopPage] Usuario actual:', user);
    console.log('💰 [ShopPage] CyberCredits:', user.cybercreds);
    currentCybercreds.value = user.cybercreds || 0;
    
    console.log('🐾 [ShopPage] Obteniendo mascotas del usuario con user_id:', user.user_id);
    const response = await PetService.getUserPets(user.user_id);
    console.log('✅ [ShopPage] Respuesta de mascotas del backend:', response);
    
    // El backend devuelve una respuesta paginada con structure: { count, next, previous, results }
    const userPets = Array.isArray(response) ? response : (response.results || []);
    console.log('📊 [ShopPage] Mascotas extraídas:', userPets);
    console.log('📊 [ShopPage] Cantidad de mascotas:', userPets.length);
    
    userPetIds.value = userPets.map((up) => up.pet);
    console.log('🆔 [ShopPage] IDs de mascotas extraídos:', userPetIds.value);
  } catch (error) {
    console.error('❌ [ShopPage] Error cargando datos del usuario:', error);
    userPetIds.value = [];
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadUserData();
});

const isPetOwned = (item: ShopItem): boolean => {
  if (item.category !== 'pets') return false;
  const petId = (item as any).petId;
  return petId ? userPetIds.value.includes(petId) : false;
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
        <span class="text">{{ currentCybercreds }} CyberCredits</span>
      </div>
    </header>

    <main v-if="!loading" class="layout">
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
        :owned-pet-ids="userPetIds"
        @select="handleSelect"
      />

      <ShopItemDetails 
        class="right" 
        :item="selectedItem" 
        :is-owned="selectedItem ? isPetOwned(selectedItem) : false"
        @buy="handleBuy" 
      />
    </main>

    <div v-else class="loading">
      <p>Cargando tienda...</p>
    </div>

    <!-- Toast Notification -->
    <Transition name="toast">
      <div v-if="toastVisible" class="toast">
        {{ toastMessage }}
      </div>
    </Transition>

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

.loading {
  flex: 1;
  display: grid;
  place-items: center;
  color: white;
  font-size: 1.4rem;
  font-weight: 700;
}

/* Toast notification styles */
.toast {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10000;
  padding: 16px 32px;
  background: rgba(15, 15, 25, 0.95);
  color: white;
  border-radius: 12px;
  border: 2px solid rgba(80, 227, 194, 0.8);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  font-weight: 700;
  font-size: 1.1rem;
  backdrop-filter: blur(10px);
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

</style>
