<script setup lang="ts">
import type { ShopItem } from './shop.types';
import ShopItemCard from './ShopItemCard.vue';

const props = defineProps<{
  items: ShopItem[];
  selectedId?: string;
  ownedPetIds?: number[];
  ownedCosmeticIds?: number[];
}>();

defineEmits<{
  (e: 'select', value: ShopItem): void;
}>();

const isOwned = (item: ShopItem): boolean => {
  if (item.category === 'pets') {
    const petId = (item as any).petId;
    return petId ? (props.ownedPetIds || []).includes(petId) : false;
  } else if (item.category === 'sounds') {
    const itemId = (item as any).itemId;
    return itemId ? (props.ownedCosmeticIds || []).includes(itemId) : false;
  }
  return false;
};
</script>

<template>
  <section class="grid-wrap" aria-label="Artículos en venta">
    <div class="grid" role="list">
      <ShopItemCard
        v-for="item in items"
        :key="item.id"
        :item="item"
        :selected="item.id === selectedId"
        :owned="isOwned(item)"
        role="listitem"
        @select="$emit('select', $event)"
      />
    </div>
  </section>
</template>

<style scoped>
.grid-wrap {
  height: 100%;
  border-radius: 22px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.14);
  border: 2px solid rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(8px);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.22);
  overflow: auto;
  min-height: 0;
}

.grid {
  height: 100%;
  min-height: 0;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  grid-auto-rows: minmax(220px, 1fr);
  gap: 14px;
  overflow: visible;
}

@media (max-width: 1200px) {
  .grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 820px) {
  .grid {
    grid-template-columns: 1fr;
    grid-auto-rows: minmax(200px, 1fr);
  }
}
</style>
