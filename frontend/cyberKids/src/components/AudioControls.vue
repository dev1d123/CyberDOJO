<template>
  <div class="audio-controls">
    <!-- Botón principal de audio -->
    <button 
      class="audio-toggle-btn" 
      @click.stop="togglePanel"
      :title="isMuted ? 'Audio silenciado' : 'Controles de audio'"
    >
      <svg v-if="!isMuted" class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
        <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
        <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
      </svg>
      <svg v-else class="icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
        <line x1="23" y1="9" x2="17" y2="15"></line>
        <line x1="17" y1="9" x2="23" y2="15"></line>
      </svg>
    </button>

    <!-- Panel de controles -->
    <Transition name="slide-up">
      <div v-if="showPanel" class="audio-panel">
        <div class="panel-header">
          <h3>Controles de Audio</h3>
          <button class="close-btn" @click="togglePanel">×</button>
        </div>
        
        <div class="controls-section">
          <!-- Control de mute general -->
          <div class="control-item">
            <label class="control-label">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
              </svg>
              <span>Silenciar Todo</span>
            </label>
            <button 
              class="mute-btn"
              :class="{ active: isMuted }"
              @click="toggleMute"
            >
              {{ isMuted ? 'Silenciado' : 'Activo' }}
            </button>
          </div>

          <!-- Control de volumen de música de fondo -->
          <div class="control-item">
            <label class="control-label">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 18V5l12-2v13"></path>
                <circle cx="6" cy="18" r="3"></circle>
                <circle cx="18" cy="16" r="3"></circle>
              </svg>
              <span>Música de Fondo</span>
            </label>
            <div class="volume-control">
              <input 
                type="range" 
                min="0" 
                max="100" 
                v-model="backgroundVolume"
                @input="updateBackgroundVolume"
                :disabled="isMuted"
                class="volume-slider"
              />
              <span class="volume-value">{{ backgroundVolume }}%</span>
            </div>
          </div>

          <!-- Control de volumen de efectos de sonido -->
          <div class="control-item">
            <label class="control-label">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path>
              </svg>
              <span>Efectos de Sonido</span>
            </label>
            <div class="volume-control">
              <input 
                type="range" 
                min="0" 
                max="100" 
                v-model="sfxVolume"
                @input="updateSFXVolume"
                :disabled="isMuted"
                class="volume-slider"
              />
              <span class="volume-value">{{ sfxVolume }}%</span>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { AudioService } from '../services/audio.service';

const showPanel = ref(false);
const isMuted = ref(false);
const backgroundVolume = ref(30);
const sfxVolume = ref(50);

const togglePanel = () => {
  showPanel.value = !showPanel.value;
};

const toggleMute = () => {
  isMuted.value = !isMuted.value;
  AudioService.toggleMute();
};

const updateBackgroundVolume = () => {
  AudioService.setBackgroundVolume(backgroundVolume.value / 100);
};

const updateSFXVolume = () => {
  AudioService.setSFXVolume(sfxVolume.value / 100);
};

// Cerrar panel al hacer click fuera
onMounted(() => {
  document.addEventListener('click', (e) => {
    const target = e.target as HTMLElement;
    const audioControls = document.querySelector('.audio-controls');
    if (audioControls && !audioControls.contains(target)) {
      showPanel.value = false;
    }
  });
});
</script>

<style scoped>
.audio-controls {
  position: fixed;
  bottom: 20px;
  left: 20px;
  z-index: 9999;
}

.audio-toggle-btn {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
  padding: 0;
}

.audio-toggle-btn .icon {
  width: 28px;
  height: 28px;
  color: white;
  stroke: white;
}

.audio-toggle-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.audio-toggle-btn:active {
  transform: translateY(0);
}

.audio-panel {
  position: absolute;
  bottom: 70px;
  left: 0;
  width: 320px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.panel-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 28px;
  cursor: pointer;
  padding: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.controls-section {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.control-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.control-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.control-label svg {
  color: #667eea;
}

.mute-btn {
  padding: 8px 16px;
  border-radius: 8px;
  border: 2px solid #667eea;
  background: white;
  color: #667eea;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.mute-btn:hover {
  background: #667eea;
  color: white;
}

.mute-btn.active {
  background: #dc3545;
  border-color: #dc3545;
  color: white;
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 12px;
}

.volume-slider {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: #e0e0e0;
  outline: none;
  -webkit-appearance: none;
}

.volume-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.volume-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.volume-slider:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.volume-value {
  min-width: 40px;
  text-align: right;
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

/* Animaciones */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
