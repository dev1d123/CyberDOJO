<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps<{
  label?: string;
  fixed?: boolean;
}>();

const router = useRouter();

const isFixed = computed(() => props.fixed !== false);

const goDashboard = () => {
  router.push('/dashboard');
};
</script>

<template>
  <button
    class="back-btn"
    :class="{ fixed: isFixed }"
    type="button"
    aria-label="Volver al dashboard"
    @click="goDashboard"
  >
    <span class="icon" aria-hidden="true">⬅</span>
    <span class="text">{{ label ?? 'Dashboard' }}</span>
  </button>
</template>

<style scoped>
.back-btn {
  border: none;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 999px;
  font-weight: 1000;
  color: white;

  background: rgba(255, 255, 255, 0.18);
  border: 2px solid rgba(255, 255, 255, 0.22);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);

  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.25);
  transition: transform 0.18s ease, background 0.18s ease, box-shadow 0.18s ease;
}

.back-btn:hover {
  transform: translateY(-2px) scale(1.02);
  background: rgba(255, 255, 255, 0.24);
  box-shadow: 0 22px 58px rgba(0, 0, 0, 0.32);
}

.back-btn:active {
  transform: translateY(0px);
}

.back-btn:focus,
.back-btn:focus-visible {
  outline: 4px solid #ffd700;
  outline-offset: 2px;
}

.fixed {
  position: fixed;
  top: 1.25rem;
  left: 1.25rem;
  z-index: 2500;
}

.icon {
  display: inline-block;
  animation: wiggle 1.6s ease-in-out infinite;
}

@keyframes wiggle {
  0%, 100% {
    transform: rotate(0deg);
  }
  50% {
    transform: rotate(-10deg);
  }
}

.text {
  font-size: 1rem;
}

@media (max-width: 768px) {
  .fixed {
    top: 0.9rem;
    left: 0.9rem;
  }

  .back-btn {
    padding: 10px 14px;
  }

  .text {
    font-size: 0.95rem;
  }
}
</style>
