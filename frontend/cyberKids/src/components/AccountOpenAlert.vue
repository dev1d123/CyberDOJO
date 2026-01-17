<script setup lang="ts">
import { watch, onMounted, onBeforeUnmount, ref } from 'vue';

const props = defineProps<{
  modelValue: boolean;
  message?: string;
  confirmText?: string;
  cancelText?: string;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'confirm'): void;
  (e: 'cancel'): void;
}>();

const dialogRef = ref<HTMLDivElement | null>(null);

const close = () => {
  emit('update:modelValue', false);
  emit('cancel');
};

const confirm = () => {
  emit('confirm');
};

const onKeydown = (e: KeyboardEvent) => {
  if (!props.modelValue) return;
  if (e.key === 'Escape') {
    e.preventDefault();
    close();
  }
};

const setBodyLock = (locked: boolean) => {
  // Evita scroll y acciones “accidentales” al fondo.
  document.body.style.overflow = locked ? 'hidden' : '';
};

watch(
  () => props.modelValue,
  (open) => {
    setBodyLock(open);
    if (open) {
      // Dar foco al diálogo para accesibilidad.
      requestAnimationFrame(() => dialogRef.value?.focus());
    }
  },
  { immediate: true }
);

onMounted(() => {
  window.addEventListener('keydown', onKeydown, { passive: false });
});

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKeydown);
  setBodyLock(false);
});
</script>

<template>
  <teleport to="body">
    <div v-if="modelValue" class="overlay" role="presentation" @click.self="close">
      <div
        ref="dialogRef"
        class="dialog"
        role="dialog"
        aria-modal="true"
        aria-label="Alerta"
        tabindex="-1"
      >
        <div class="icon-badge" aria-hidden="true">🔒</div>

        <h2 class="title">Sesión activa</h2>
        <p class="message">
          {{ message ?? 'Todavia hay una cuenta abierta. Cierra sesion para continuar.' }}
        </p>

        <div class="actions">
          <button class="btn btn-secondary" type="button" @click="close">
            {{ cancelText ?? 'Cancelar' }}
          </button>
          <button class="btn btn-primary" type="button" @click="confirm">
            {{ confirmText ?? 'Cerrar sesión' }}
          </button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  z-index: 5000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(10px);
}

.dialog {
  width: min(560px, 100%);
  border-radius: 28px;
  padding: 2rem 2rem 1.6rem;
  background: rgba(255, 255, 255, 0.96);
  border: 5px solid #ff6b6b;
  box-shadow: 0 22px 70px rgba(0, 0, 0, 0.45);
  position: relative;
  outline: none;
}

.icon-badge {
  width: 64px;
  height: 64px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  font-size: 2rem;
  background: linear-gradient(135deg, #ff6b6b, #ff8e53);
  box-shadow: 0 12px 30px rgba(255, 107, 107, 0.45);
  border: 4px solid rgba(255, 255, 255, 0.7);
  position: absolute;
  top: -28px;
  left: 28px;
}

.title {
  margin: 1.4rem 0 0.6rem;
  font-size: 2.2rem;
  color: #2c3e50;
  text-shadow: 2px 2px 0 rgba(255, 107, 107, 0.25);
}

.message {
  margin: 0;
  font-size: 1.35rem;
  line-height: 1.5;
  color: #2c3e50;
}

.actions {
  margin-top: 1.6rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn {
  border: none;
  padding: 1rem 1.6rem;
  border-radius: 18px;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.2);
}

.btn:focus,
.btn:focus-visible {
  outline: 4px solid #ffd700;
  outline-offset: 2px;
}

.btn-secondary {
  background: linear-gradient(135deg, #bdc3c7, #95a5a6);
  color: white;
}

.btn-secondary:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.25);
}

.btn-primary {
  background: linear-gradient(135deg, #ff6b6b, #ff8e53);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 16px 34px rgba(255, 107, 107, 0.45);
}

@media (max-width: 520px) {
  .dialog {
    padding: 1.8rem 1.4rem 1.4rem;
  }
  .title {
    font-size: 1.9rem;
  }
  .message {
    font-size: 1.2rem;
  }
  .actions {
    justify-content: center;
  }
}
</style>
