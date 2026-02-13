<template>
  <div class="mascot-widget">
    <div class="avatar-bg">
      <img :src="src" alt="mascot" />
    </div>
    <DialogPanel>
      <div class="mascot-text">
        <h2 class="mascot-title">{{ title }}</h2>
        <p class="mascot-sub">{{ subtitle }}</p>
      </div>
    </DialogPanel>
  </div>
</template>

<script setup lang="ts">
import DialogPanel from './DialogPanel.vue'

const props = defineProps<{ src: string; title: string; subtitle?: string }>();
</script>

<style scoped>
@keyframes slideInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.mascot-widget { 
  display: flex; 
  gap: 16px; 
  align-items: flex-start;
  animation: slideInDown 0.8s ease-out 0.85s both;
}

.avatar-bg { 
  width: 96px; 
  height: 96px; 
  border-radius: 999px; 
  background: white; 
  padding: 6px; 
  display: grid; 
  place-items: center; 
  box-shadow: 0 18px 40px rgba(0,0,0,0.12);
  animation: slideInDown 0.8s ease-out 0.9s both;
}

.avatar-bg img { 
  width: 100%; 
  height: 100%; 
  object-fit: cover;
}

.mascot-text { 
  margin: 0;
  animation: slideInDown 0.8s ease-out 0.95s both;
}

.mascot-title { 
  margin: 0; 
  font-weight: 900; 
  color: #1E4B66; 
  font-size: 1.25rem;
}

.mascot-sub { 
  margin: 6px 0 0 0; 
  color: rgba(30,75,102,0.75); 
  font-weight: 700;
}

@media (min-width: 768px) {
  .mascot-widget { align-items: center; }
}
</style>
