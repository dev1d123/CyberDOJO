import { ref } from 'vue';

export const hasPetEquipped = ref(false);
export const currentPetId = ref<number | null>(null);

export function setPetEquipped(petId: number | null) {
  currentPetId.value = petId;
  hasPetEquipped.value = petId !== null;
}
