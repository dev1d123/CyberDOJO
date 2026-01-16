<template>
  <div class="preview" :class="`preview--${type}`">
    <template v-if="type === 'trust'">
      <div class="notif">
        <div class="notif-badge">🔔</div>
        <div class="notif-text">
          <div class="notif-title">"¡Gané un premio!"</div>
          <div class="notif-sub">Toca el link para reclamarlo…</div>
        </div>
      </div>

      <div class="slider">
        <span class="slider-label slider-label--safe">Seguro</span>
        <div class="slider-track">
          <div class="slider-dot"></div>
        </div>
        <span class="slider-label slider-label--danger">Peligroso</span>
      </div>
    </template>

    <template v-else-if="type === 'chat'">
      <div class="bubbles">
        <div class="bubble bubble--npc">Hola 👋 ¿me pasas tu contraseña para ayudarte?</div>
        <div class="bubble bubble--me">¿Ehh… por qué la necesitas?</div>
      </div>
      <div class="choices">
        <span class="chip">Responder</span>
        <span class="chip chip--warn">Reportar</span>
      </div>
    </template>

    <template v-else>
      <div class="post">
        <div class="post-title">Publicación</div>
        <div class="post-line">"Envíame tu código"</div>
        <div class="post-line post-line--danger">"Es urgente, no se lo digas a nadie"</div>
      </div>
      <div class="timer">
        <div class="timer-bar"></div>
        <span class="timer-text">¡Rápido!</span>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
type PreviewType = 'trust' | 'chat' | 'hunt';

defineProps<{ type: PreviewType }>();
</script>

<style scoped>
.preview {
  width: 100%;
  border-radius: 16px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.92);
  border: 2px solid rgba(255, 255, 255, 0.55);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.14);
  display: flex;
  flex-direction: column;
  gap: 10px;
  transform: translateZ(0);
}

.notif {
  display: flex;
  gap: 10px;
  align-items: center;
}

.notif-badge {
  width: 34px;
  height: 34px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #48c6ef 0%, #6f86d6 100%);
  box-shadow: 0 10px 22px rgba(72, 198, 239, 0.25);
}

.notif-title {
  font-weight: 900;
  color: #1f2d3d;
  font-size: 0.95rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.notif-sub {
  color: #506070;
  font-weight: 700;
  font-size: 0.8rem;
  opacity: 0.9;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.slider {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 10px;
}

.slider-label {
  font-size: 0.85rem;
  font-weight: 900;
}

.slider-label--safe {
  color: #16a34a;
}

.slider-label--danger {
  color: #ef4444;
}

.slider-track {
  position: relative;
  height: 12px;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(22, 163, 74, 0.25) 0%, rgba(245, 158, 11, 0.25) 55%, rgba(239, 68, 68, 0.28) 100%);
  overflow: hidden;
}

.slider-dot {
  position: absolute;
  top: 50%;
  left: 18%;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: white;
  border: 3px solid rgba(72, 198, 239, 0.85);
  transform: translateY(-50%);
  animation: dotBounce 1.4s ease-in-out infinite;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

@keyframes dotBounce {
  0%, 100% {
    transform: translateY(-50%) translateX(0);
  }
  50% {
    transform: translateY(-64%) translateX(12px);
  }
}

.bubbles {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.bubble {
  padding: 10px 12px;
  border-radius: 14px;
  font-weight: 800;
  font-size: 0.88rem;
  line-height: 1.15;
}

.bubble--npc {
  background: rgba(102, 126, 234, 0.18);
  border: 2px solid rgba(102, 126, 234, 0.22);
  color: #2c3e50;
}

.bubble--me {
  background: rgba(16, 185, 129, 0.16);
  border: 2px solid rgba(16, 185, 129, 0.2);
  color: #14532d;
  align-self: flex-end;
}

.choices {
  display: flex;
  gap: 8px;
}

.chip {
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 900;
  background: rgba(255, 255, 255, 0.85);
  border: 2px solid rgba(99, 102, 241, 0.22);
  color: #4338ca;
}

.chip--warn {
  border-color: rgba(239, 68, 68, 0.22);
  color: #b91c1c;
}

.post {
  border-radius: 14px;
  padding: 10px 12px;
  border: 2px dashed rgba(124, 58, 237, 0.35);
  background: rgba(124, 58, 237, 0.07);
}

.post-title {
  font-weight: 900;
  color: #4c1d95;
  font-size: 0.8rem;
  margin-bottom: 6px;
}

.post-line {
  font-weight: 800;
  color: #334155;
  font-size: 0.9rem;
}

.post-line--danger {
  margin-top: 6px;
  color: #b91c1c;
  background: rgba(239, 68, 68, 0.14);
  padding: 6px 10px;
  border-radius: 12px;
  animation: pulseDanger 1.3s ease-in-out infinite;
}

@keyframes pulseDanger {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
}

.timer {
  display: flex;
  align-items: center;
  gap: 10px;
}

.timer-bar {
  height: 10px;
  flex: 1;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(34, 197, 94, 0.35) 0%, rgba(234, 179, 8, 0.35) 55%, rgba(239, 68, 68, 0.35) 100%);
  position: relative;
  overflow: hidden;
}

.timer-bar::after {
  content: '';
  position: absolute;
  inset: 0;
  width: 55%;
  background: rgba(255, 255, 255, 0.55);
  border-radius: 999px;
  animation: timerMove 1.6s ease-in-out infinite;
}

@keyframes timerMove {
  0%, 100% {
    transform: translateX(-10%);
  }
  50% {
    transform: translateX(80%);
  }
}

.timer-text {
  font-weight: 1000;
  color: #b91c1c;
  font-size: 0.85rem;
}
</style>
