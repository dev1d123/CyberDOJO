<template>
  <div class="modal-overlay">
    <div class="decor-background">
      <div class="floating-cloud cloud-1"></div>
      <div class="floating-cloud cloud-2"></div>
      <div class="floating-cloud cloud-3"></div>
      <div class="floating-cloud cloud-4"></div>
    </div>

    <main class="modal-content">
      <div class="results-card">
        <div class="blur-circle top-left"></div>
        <div class="blur-circle bottom-right"></div>

        <div class="results-body">
          <div class="reward-header">
            <div class="reward-container">
              <div class="avatar-circle">
                <img :src="userAvatar" alt="Avatar de usuario" />
              </div>
              <div class="trophy-wrapper">
                <div class="trophy-glow"></div>
                <span class="material-icon trophy-icon">emoji_events</span>
                <span class="material-icon star-sparkle">stars</span>
              </div>
            </div>
          </div>

          <h1 class="congrats-title">¡Misión Cumplida!</h1>
          <p class="congrats-subtitle">
            Has completado el entrenamiento básico con éxito.
          </p>

          <div class="stats-grid">
            <div class="stat-box points">
              <span class="stat-label">Puntos Totales</span>
              <div class="stat-value">{{ totalPoints }}</div>
            </div>
            <div class="stat-box accuracy">
              <span class="stat-label">Aciertos</span>
              <div class="stat-value">
                {{ correctAnswers }}<span class="stat-total">/{{ totalQuestions }}</span>
              </div>
            </div>
          </div>

          <div class="actions-group">
            <button class="btn btn-primary" @click="$emit('onRestart')">
              <span class="material-icon">replay</span>
              Volver a Jugar
            </button>
            <button class="btn btn-secondary" @click="$emit('onGoToDashboard')">
              <span class="material-icon">dashboard</span>
              Ver otros Quizzes
            </button>
          </div>
        </div>
      </div>
      
      <div class="mascot-side-footer">
        <img :src="mascotUrl" alt="Mascota saludando" class="mascot-img" />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
/**
 * PROPS: Configuración de resultados y recursos
 */
interface Props {
  totalPoints?: number;
  correctAnswers?: number;
  totalQuestions?: number;
  userAvatar?: string;
  mascotUrl?: string;
}

withDefaults(defineProps<Props>(), {
  totalPoints: 0,
  correctAnswers: 0,
  totalQuestions: 10,
  userAvatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCucjZBT2oZoN5rGKrDGU5Q9yq3f9tkghZGt5pjgZLPnrwZPlzx51O5syvPmrxMw9uR7djGOJodI2-z0YPaCfHQMw8Ptu-RD5shLTsY9mm4lR7j1f0ylbyId7-YVTjGo_C00NHByKcMLcxMhQZqC7cqy3Qlvk6uMEpeyHCm4fD222J3HgreRPI4Eyoy5VCcht_IBGGT3vlzJtXKNwqYmc0LV9CFCGOkMfrKcUg7HYnu6DL_JlavvApLhf_4xDZMGi-E0UmCJOuZ_gZ5',
  mascotUrl: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCucjZBT2oZoN5rGKrDGU5Q9yq3f9tkghZGt5pjgZLPnrwZPlzx51O5syvPmrxMw9uR7djGOJodI2-z0YPaCfHQMw8Ptu-RD5shLTsY9mm4lR7j1f0ylbyId7-YVTjGo_C00NHByKcMLcxMhQZqC7cqy3Qlvk6uMEpeyHCm4fD222J3HgreRPI4Eyoy5VCcht_IBGGT3vlzJtXKNwqYmc0LV9CFCGOkMfrKcUg7HYnu6DL_JlavvApLhf_4xDZMGi-E0UmCJOuZ_gZ5'
});

/**
 * EMITS: Acciones del usuario
 */
defineEmits<{
  (e: 'onRestart'): void;
  (e: 'onGoToDashboard'): void;
}>();
</script>

<style scoped>
/* --- VARIABLES DE DISEÑO --- */
:host {
  --primary: #ffd166;
  --deep-sea: #1e4b66;
  --mint: #7be8c3;
  --coral: #ff7a7a;
  --purple: #8b7cff;
  --sky-blue: #6ecff5;
  --white-bg: rgba(255, 255, 255, 0.95);
  --font-fredoka: 'Fredoka', sans-serif;
}

/* --- ESTRUCTURA MODAL --- */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 999;
  background: linear-gradient(135deg, var(--sky-blue) 0%, var(--purple) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  overflow: hidden;
}

.modal-content {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 600px;
  animation: popIn 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.results-card {
  background: var(--white-bg);
  border-radius: 2.5rem;
  padding: 3rem 2rem;
  border: 4px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
  text-align: center;
}

/* --- DECORACIONES --- */
.blur-circle {
  position: absolute;
  width: 250px;
  height: 250px;
  border-radius: 50%;
  filter: blur(60px);
  z-index: 0;
}
.top-left { top: -100px; left: -100px; background: rgba(255, 209, 102, 0.2); }
.bottom-right { bottom: -100px; right: -100px; background: rgba(123, 232, 195, 0.2); }

.results-body { position: relative; z-index: 1; }

/* --- REWARD HEADER (Avatar + Trofeo) --- */
.reward-header {
  height: 140px;
  display: flex;
  justify-content: center;
  align-items: flex-end;
  margin-bottom: 2rem;
}

.reward-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid white;
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
  transform: translateX(-20px) translateY(10px);
}

.avatar-circle img { width: 100%; height: 100%; object-fit: cover; }

.trophy-wrapper {
  position: relative;
  transform: translateX(20px) translateY(-10px);
}

.trophy-icon {
  font-size: 6rem;
  color: #fbbf24; /* Yellow 400 */
  filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
  transform: rotate(-5deg);
}

.trophy-glow {
  position: absolute;
  inset: 0;
  background: #fbbf24;
  border-radius: 50%;
  filter: blur(25px);
  opacity: 0.3;
  animation: pulse 2s infinite;
}

.star-sparkle {
  position: absolute;
  top: -10px;
  right: -10px;
  color: #fde047;
  font-size: 2.5rem;
  animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;
}

/* --- TEXTOS --- */
.congrats-title {
  font-family: var(--font-fredoka);
  font-size: 3rem;
  color: var(--deep-sea);
  margin: 0;
}

.congrats-subtitle {
  color: rgba(30, 75, 102, 0.6);
  font-weight: 600;
  font-size: 1.25rem;
  margin: 0.5rem 0 2rem 0;
}

/* --- ESTADÍSTICAS --- */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 2.5rem;
}

.stat-box {
  padding: 1.5rem;
  border-radius: 1.5rem;
  border: 1px solid rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
}

.points { background: linear-gradient(to bottom right, #f5f3ff, #ffffff); border-color: #ddd6fe; }
.accuracy { background: linear-gradient(to bottom right, #f0fdf4, #ffffff); border-color: #bbf7d0; }

.stat-label {
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  color: rgba(30, 75, 102, 0.5);
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-family: var(--font-fredoka);
  font-size: 2.5rem;
  font-weight: 700;
}

.points .stat-value { color: var(--purple); }
.accuracy .stat-value { color: var(--mint); }
.stat-total { font-size: 1.25rem; color: #94a3b8; }

/* --- BOTONES --- */
.actions-group {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.btn {
  width: 100%;
  padding: 1.25rem;
  border-radius: 1.25rem;
  font-family: var(--font-fredoka);
  font-size: 1.25rem;
  font-weight: 700;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  transition: all 0.2s;
  position: relative;
}

.btn-primary {
  background: var(--primary);
  color: var(--deep-sea);
  box-shadow: 0 5px 0px #eab308;
}

.btn-secondary {
  background: var(--deep-sea);
  color: white;
  box-shadow: 0 5px 0px #0f172a;
}

.btn:active {
  transform: translateY(4px);
  box-shadow: none;
}

.material-icon {
  font-family: 'Material Icons Round';
  font-size: 1.5rem;
}

/* --- NUBES Y MASCOTA --- */
.decor-background {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.floating-cloud {
  position: absolute;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 999px;
  filter: blur(8px);
}

.cloud-1 { top: 10%; left: 5%; width: 200px; height: 80px; animation: floatAnim 20s infinite linear; }
.cloud-2 { top: 25%; right: 10%; width: 150px; height: 60px; animation: floatAnim 25s infinite linear reverse; }
.cloud-3 { bottom: 10%; left: 15%; width: 280px; height: 90px; animation: floatAnim 30s infinite linear; }

.mascot-side-footer {
  position: absolute;
  bottom: -40px;
  left: -80px;
  width: 180px;
  pointer-events: none;
  z-index: 20;
}

.mascot-img { width: 100%; filter: drop-shadow(0 10px 15px rgba(0,0,0,0.2)); }

/* --- ANIMACIONES --- */
@keyframes floatAnim {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(30px); }
}

@keyframes popIn {
  from { opacity: 0; transform: scale(0.8) translateY(20px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

@keyframes pulse {
  0% { transform: scale(0.95); opacity: 0.3; }
  50% { transform: scale(1.1); opacity: 0.5; }
  100% { transform: scale(0.95); opacity: 0.3; }
}

@keyframes ping {
  75%, 100% { transform: scale(2); opacity: 0; }
}

/* --- RESPONSIVIDAD --- */
@media (max-width: 640px) {
  .congrats-title { font-size: 2.25rem; }
  .stat-value { font-size: 1.75rem; }
  .modal-content { max-width: 100%; }
  .mascot-side-footer { left: 0; width: 120px; bottom: -20px; }
}
</style>