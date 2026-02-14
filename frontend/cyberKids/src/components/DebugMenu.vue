<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { AudioService } from '../services/audio.service';
import { TTSService } from '../services/tts.service';
import { setPetEquipped } from '@/stores/petState.store';

const isOpen = ref(false);
const loading = ref(false);
const message = ref('');

// User data
const userId = ref<number | null>(null);
const equippedPetId = ref<number | null>(null);
const ownedPets = ref<any[]>([]);
const ownedAudios = ref<any[]>([]);
const equippedAudioName = ref<string>('Ninguno');
const currentCybercreds = ref(0);

// Form inputs
const selectedPetToEquip = ref<number | null>(null);
const selectedAudioToEquip = ref<number | null>(null);
const creditsToAdd = ref(100);

// TTS (client-side)
type VoiceOption = { label: string; voiceURI: string; lang: string };
const ttsSupported = ref<boolean>(TTSService.isSupported());
const ttsText = ref<string>('Hola, esto es una prueba de voz desde el navegador.');
const ttsLang = ref<string>('es-ES');
const ttsRate = ref<number>(1);
const ttsPitch = ref<number>(1);
const ttsVolume = ref<number>(1);
const ttsVoices = ref<VoiceOption[]>([]);
const ttsSelectedVoiceURI = ref<string>('');
const ttsStatus = ref<string>('');

import { API_CONFIG } from '../config/api.config';

const API_BASE_URL = API_CONFIG.BASE_URL;

onMounted(async () => {
  await loadDebugData();

  if (ttsSupported.value) {
    await refreshTtsVoices();
  }
});

const refreshTtsVoices = async () => {
  try {
    const voices = await TTSService.getVoices();
    ttsVoices.value = voices.map(v => ({
      label: `${v.name} (${v.lang})${v.default ? ' • default' : ''}`,
      voiceURI: v.voiceURI,
      lang: v.lang,
    }));

    // Preferir una voz española si existe
    const preferred = voices.find(v => v.lang?.toLowerCase().startsWith('es')) || voices[0];
    if (preferred && !ttsSelectedVoiceURI.value) {
      ttsSelectedVoiceURI.value = preferred.voiceURI;
      ttsLang.value = preferred.lang || ttsLang.value;
    }
  } catch (e: any) {
    ttsStatus.value = `✗ TTS: ${e?.message || 'No se pudieron cargar voces'}`;
  }
};

const handleSpeakTts = async () => {
  ttsStatus.value = '';
  try {
    await TTSService.speak({
      text: ttsText.value,
      voiceURI: ttsSelectedVoiceURI.value || undefined,
      lang: ttsLang.value,
      rate: ttsRate.value,
      pitch: ttsPitch.value,
      volume: ttsVolume.value,
    });
    ttsStatus.value = '✓ TTS reproducido';
  } catch (e: any) {
    ttsStatus.value = `✗ TTS: ${e?.message || 'Error generando voz'}`;
  }
};

const handleStopTts = () => {
  TTSService.stop();
  ttsStatus.value = '⏹️ TTS detenido';
};

const loadDebugData = async () => {
  loading.value = true;
  try {
    const token = localStorage.getItem('access_token');
    const storedUserId = localStorage.getItem('user_id');
    
    if (!token || !storedUserId) {
      message.value = 'No hay sesión activa';
      return;
    }

    userId.value = parseInt(storedUserId);

    // Get current user data
    const userResponse = await axios.get(`${API_BASE_URL}/users/auth/me/`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    
    equippedPetId.value = userResponse.data.pet_id;
    currentCybercreds.value = userResponse.data.cybercreds;

    // Get user's pets
    const petsResponse = await axios.get(`${API_BASE_URL}/progression/shop/my-purchases/`, {
      headers: { Authorization: `Bearer ${token}` }
    });

    console.log('🐾 [DebugMenu] Respuesta my-purchases:', petsResponse.data);
    ownedPets.value = petsResponse.data.pets || [];
    console.log('🐾 [DebugMenu] Mascotas extraídas:', ownedPets.value);
    
    if (ownedPets.value.length > 0 && !selectedPetToEquip.value) {
      selectedPetToEquip.value = ownedPets.value[0].pet;
    }

    // Get user's cosmetics (audios)
    const cosmetics = petsResponse.data.cosmetics || [];
    console.log('🎵 [DebugMenu] Cosméticos obtenidos:', cosmetics);
    
    // Obtener detalles de los cosmetics desde la tienda para tener los nombres
    const shopResponse = await axios.get(`${API_BASE_URL}/progression/cosmetics/shop/`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    const shopCosmetics = shopResponse.data;
    
    // Mapear inventario con detalles del shop
    ownedAudios.value = cosmetics
      .map((inv: any) => {
        const cosmeticDetail = shopCosmetics.find((c: any) => c.item_id === inv.item);
        return {
          ...inv,
          name: cosmeticDetail?.name || `Audio #${inv.item}`,
          type: cosmeticDetail?.type || 'effect'
        };
      })
      .filter((c: any) => c.type === 'effect'); // Solo audios
    
    console.log('🎵 [DebugMenu] Audios del usuario:', ownedAudios.value);
    
    // Encontrar audio equipado
    const equippedAudio = ownedAudios.value.find((a: any) => a.is_equipped);
    equippedAudioName.value = equippedAudio ? equippedAudio.name : 'Ninguno';
    
    if (ownedAudios.value.length > 0 && !selectedAudioToEquip.value) {
      selectedAudioToEquip.value = ownedAudios.value[0].item;
    }

  } catch (error: any) {
    console.error('Error loading debug data:', error);
    message.value = `Error: ${error.response?.data?.error || error.message}`;
  } finally {
    loading.value = false;
  }
};

const handleEquipPet = async () => {
  if (!selectedPetToEquip.value) {
    message.value = 'Selecciona una mascota primero';
    return;
  }

  loading.value = true;
  message.value = '';

  try {
    const token = localStorage.getItem('access_token');
    const response = await axios.post(
      `${API_BASE_URL}/progression/shop/equip-pet/`,
      { pet_id: selectedPetToEquip.value },
      { headers: { Authorization: `Bearer ${token}` } }
    );

    message.value = `✓ ${response.data.message}`;
    
    // ¡IMPORTANTE! Actualizar el store global de la mascota equipada
    setPetEquipped(selectedPetToEquip.value);
    console.log('🐾 [DebugMenu] Mascota equipada actualizada:', selectedPetToEquip.value);
    
    await loadDebugData();
  } catch (error: any) {
    console.error('Error equipping pet:', error);
    message.value = `✗ Error: ${error.response?.data?.error || error.message}`;
  } finally {
    loading.value = false;
  }
};

const handleEquipAudio = async () => {
  if (!selectedAudioToEquip.value) {
    message.value = 'Selecciona un audio primero';
    return;
  }

  loading.value = true;
  message.value = '';

  try {
    const token = localStorage.getItem('access_token');
    const response = await axios.post(
      `${API_BASE_URL}/progression/shop/equip-cosmetic/`,
      { item_id: selectedAudioToEquip.value },
      { headers: { Authorization: `Bearer ${token}` } }
    );

    message.value = `✓ ${response.data.message}`;
    
    // Recargar tema de audio con fade in/out
    await AudioService.reloadTheme();
    
    await loadDebugData();
  } catch (error: any) {
    console.error('Error equipping audio:', error);
    message.value = `✗ Error: ${error.response?.data?.error || error.message}`;
  } finally {
    loading.value = false;
  }
};

const handleAddCredits = async () => {
  if (!creditsToAdd.value || creditsToAdd.value <= 0) {
    message.value = 'Ingresa una cantidad válida';
    return;
  }

  loading.value = true;
  message.value = '';

  try {
    const token = localStorage.getItem('access_token');
    
    // Usar el endpoint correcto de add_cybercreds
    await axios.post(
      `${API_BASE_URL}/users/${userId.value}/add_cybercreds/`,
      { amount: creditsToAdd.value },
      { headers: { Authorization: `Bearer ${token}` } }
    );

    message.value = `✓ Agregados ${creditsToAdd.value} CyberCredits`;
    await loadDebugData();
  } catch (error: any) {
    console.error('Error adding credits:', error);
    message.value = `✗ Error: ${error.response?.data?.error || error.message}`;
  } finally {
    loading.value = false;
  }
};

const toggleMenu = () => {
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    loadDebugData();
  }
};

const ownedPetIds = computed(() => ownedPets.value.map(up => up.pet).join(', '));
const ownedAudioIds = computed(() => ownedAudios.value.map(a => a.item).join(', '));
</script>

<template>
  <div class="debug-menu">
    <button class="debug-toggle" @click="toggleMenu" :class="{ active: isOpen }">
      🐛 Debug
    </button>

    <div v-if="isOpen" class="debug-panel">
      <div class="debug-header">
        <h3>🛠️ Debug Menu</h3>
        <button class="close-btn" @click="isOpen = false">✕</button>
      </div>

      <div v-if="loading" class="debug-loading">
        Cargando datos...
      </div>

      <div v-else class="debug-content">
        <!-- User Info Section -->
        <div class="debug-section">
          <h4>👤 Usuario</h4>
          <div class="info-row">
            <span class="label">ID:</span>
            <span class="value">{{ userId }}</span>
          </div>
          <div class="info-row">
            <span class="label">CyberCredits:</span>
            <span class="value">{{ currentCybercreds }}</span>
          </div>
        </div>

        <!-- Equipped Pet Section -->
        <div class="debug-section">
          <h4>🐾 Mascota Equipada</h4>
          <div class="info-row">
            <span class="label">Pet ID:</span>
            <span class="value">{{ equippedPetId || 'Ninguna' }}</span>
          </div>
        </div>

        <!-- Equipped Audio Section -->
        <div class="debug-section">
          <h4>🎵 Audio Equipado</h4>
          <div class="info-row">
            <span class="label">Audio:</span>
            <span class="value">{{ equippedAudioName }}</span>
          </div>
        </div>

        <!-- Owned Pets Section -->
        <div class="debug-section">
          <h4>🎒 Mascotas Adquiridas</h4>
          <div v-if="ownedPets.length === 0" class="empty-state">
            No tienes mascotas
          </div>
          <div v-else>
            <div class="info-row">
              <span class="label">IDs:</span>
              <span class="value">{{ ownedPetIds }}</span>
            </div>
            <div class="pets-list">
              <div v-for="userPet in ownedPets" :key="userPet.user_pet_id" class="pet-item">
                <span class="pet-name">{{ userPet.pet_name }}</span>
                <span class="pet-id">#{{ userPet.pet }}</span>
                <span v-if="userPet.is_equipped" class="equipped-badge">✓ Equipada</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Owned Audios Section -->
        <div class="debug-section">
          <h4>🎵 Audios Adquiridos</h4>
          <div v-if="ownedAudios.length === 0" class="empty-state">
            No tienes audios
          </div>
          <div v-else>
            <div class="info-row">
              <span class="label">IDs:</span>
              <span class="value">{{ ownedAudioIds }}</span>
            </div>
            <div class="pets-list">
              <div v-for="audio in ownedAudios" :key="audio.inventory_id" class="pet-item">
                <span class="pet-name">{{ audio.name }}</span>
                <span class="pet-id">#{{ audio.item }}</span>
                <span v-if="audio.is_equipped" class="equipped-badge">✓ Equipado</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Equip Pet Section -->
        <div class="debug-section">
          <h4>⚙️ Equipar Mascota</h4>
          <div v-if="ownedPets.length === 0" class="empty-state">
            Compra mascotas en la tienda primero
          </div>
          <div v-else class="action-group">
            <select v-model="selectedPetToEquip" class="debug-select">
              <option v-for="userPet in ownedPets" :key="userPet.pet" :value="userPet.pet">
                {{ userPet.pet_name }} (#{{ userPet.pet }})
              </option>
            </select>
            <button @click="handleEquipPet" class="action-btn equip-btn" :disabled="loading">
              Equipar
            </button>
          </div>
        </div>

        <!-- Equip Audio Section -->
        <div class="debug-section">
          <h4>🎵 Equipar Audio</h4>
          <div v-if="ownedAudios.length === 0" class="empty-state">
            Compra audios en la tienda primero
          </div>
          <div v-else class="action-group">
            <select v-model="selectedAudioToEquip" class="debug-select">
              <option v-for="audio in ownedAudios" :key="audio.item" :value="audio.item">
                {{ audio.name }} (#{{ audio.item }})
              </option>
            </select>
            <button @click="handleEquipAudio" class="action-btn equip-btn" :disabled="loading">
              Equipar
            </button>
          </div>
        </div>

        <!-- Add Credits Section -->
        <div class="debug-section">
          <h4>💰 Añadir CyberCredits</h4>
          <div class="action-group">
            <input 
              v-model.number="creditsToAdd" 
              type="number" 
              min="1" 
              step="10"
              class="debug-input"
              placeholder="Cantidad"
            />
            <button @click="handleAddCredits" class="action-btn credits-btn" :disabled="loading">
              + Añadir
            </button>
          </div>
        </div>

        <!-- TTS Section (Client-side) -->
        <div class="debug-section">
          <h4>🗣️ Voz (TTS)</h4>
          <div v-if="!ttsSupported" class="empty-state">
            Tu navegador no soporta TTS (speechSynthesis).
          </div>

          <div v-else>
            <div class="empty-state" style="text-align:left;">
              Nota: Qwen3-TTS (0.6B) no puede ejecutarse 100% en navegador sin backend.
              Esta prueba usa la voz del sistema del navegador.
            </div>

            <div class="action-group" style="margin-top:8px;">
              <select v-model="ttsSelectedVoiceURI" class="debug-select">
                <option v-for="v in ttsVoices" :key="v.voiceURI" :value="v.voiceURI">
                  {{ v.label }}
                </option>
              </select>
              <button @click="refreshTtsVoices" class="action-btn equip-btn" :disabled="loading">
                Recargar
              </button>
            </div>

            <div class="action-group" style="margin-top:8px;">
              <input v-model="ttsLang" class="debug-input" placeholder="Idioma (ej: es-ES)" />
            </div>

            <div class="action-group" style="margin-top:8px;">
              <input v-model.number="ttsRate" type="number" min="0.5" max="2" step="0.1" class="debug-input" placeholder="Rate" />
              <input v-model.number="ttsPitch" type="number" min="0" max="2" step="0.1" class="debug-input" placeholder="Pitch" />
              <input v-model.number="ttsVolume" type="number" min="0" max="1" step="0.1" class="debug-input" placeholder="Vol" />
            </div>

            <div class="action-group" style="margin-top:8px;">
              <textarea v-model="ttsText" class="debug-input" rows="3" placeholder="Texto a hablar" style="resize:vertical;"></textarea>
            </div>

            <div class="action-group" style="margin-top:8px;">
              <button @click="handleSpeakTts" class="action-btn equip-btn" :disabled="loading">
                ▶ Hablar
              </button>
              <button @click="handleStopTts" class="action-btn credits-btn" :disabled="loading">
                ⏹ Detener
              </button>
            </div>

            <div v-if="ttsStatus" class="debug-message" :class="{ error: ttsStatus.includes('✗') }">
              {{ ttsStatus }}
            </div>
          </div>
        </div>

        <!-- Message Display -->
        <div v-if="message" class="debug-message" :class="{ error: message.includes('✗') }">
          {{ message }}
        </div>

        <!-- Refresh Button -->
        <button @click="loadDebugData" class="refresh-btn" :disabled="loading">
          🔄 Recargar Datos
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.debug-menu {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
}

.debug-toggle {
  padding: 12px 18px;
  background: rgba(0, 0, 0, 0.85);
  color: #00ff00;
  border: 2px solid #00ff00;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  font-size: 0.85rem;
  box-shadow: 0 4px 12px rgba(0, 255, 0, 0.3);
  transition: all 0.2s ease;
}

.debug-toggle:hover {
  background: rgba(0, 255, 0, 0.1);
  transform: scale(1.05);
}

.debug-toggle.active {
  background: #00ff00;
  color: black;
}

.debug-panel {
  position: absolute;
  top: 60px;
  right: 0;
  width: 400px;
  max-height: 80vh;
  background: rgba(20, 20, 30, 0.98);
  border: 2px solid #00ff00;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.debug-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: rgba(0, 255, 0, 0.1);
  border-bottom: 1px solid #00ff00;
}

.debug-header h3 {
  margin: 0;
  color: #00ff00;
  font-size: 1.05rem;
}

.close-btn {
  background: none;
  border: none;
  color: #00ff00;
  font-size: 1.4rem;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}

.close-btn:hover {
  transform: scale(1.2);
}

.debug-loading {
  padding: 40px;
  text-align: center;
  color: #00ff00;
  font-style: italic;
}

.debug-content {
  padding: 16px;
  overflow-y: auto;
  max-height: calc(80vh - 60px);
}

.debug-section {
  margin-bottom: 20px;
  padding: 12px;
  background: rgba(0, 255, 0, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(0, 255, 0, 0.2);
}

.debug-section h4 {
  margin: 0 0 12px 0;
  color: #00ff00;
  font-size: 0.85rem;
  text-transform: uppercase;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid rgba(0, 255, 0, 0.1);
}

.info-row:last-child {
  border-bottom: none;
}

.label {
  color: rgba(0, 255, 0, 0.7);
  font-size: 0.75rem;
  font-weight: bold;
}

.value {
  color: #fff;
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
}

.empty-state {
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
  font-size: 0.75rem;
  padding: 8px;
  text-align: center;
}

.pets-list {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.pet-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  font-size: 0.75rem;
}

.pet-name {
  color: #fff;
  flex: 1;
}

.pet-id {
  color: rgba(0, 255, 0, 0.7);
  font-family: 'Courier New', monospace;
  font-size: 0.7rem;
}

.equipped-badge {
  color: #00ff00;
  font-weight: bold;
  font-size: 0.7rem;
}

.action-group {
  display: flex;
  gap: 8px;
  align-items: center;
}

.debug-select,
.debug-input {
  flex: 1;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(0, 255, 0, 0.3);
  border-radius: 6px;
  color: #fff;
  font-size: 0.75rem;
}

.debug-select:focus,
.debug-input:focus {
  outline: none;
  border-color: #00ff00;
}

.action-btn {
  padding: 8px 16px;
  border: 1px solid #00ff00;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  font-size: 0.75rem;
  transition: all 0.2s;
  white-space: nowrap;
}

.action-btn:hover:not(:disabled) {
  transform: scale(1.05);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.equip-btn {
  background: rgba(0, 100, 255, 0.2);
  color: #00bfff;
  border-color: #00bfff;
}

.equip-btn:hover:not(:disabled) {
  background: rgba(0, 100, 255, 0.4);
}

.credits-btn {
  background: rgba(255, 215, 0, 0.2);
  color: #ffd700;
  border-color: #ffd700;
}

.credits-btn:hover:not(:disabled) {
  background: rgba(255, 215, 0, 0.4);
}

.debug-message {
  margin-top: 12px;
  padding: 10px;
  background: rgba(0, 255, 0, 0.15);
  border: 1px solid #00ff00;
  border-radius: 6px;
  color: #00ff00;
  font-size: 0.75rem;
  text-align: center;
}

.debug-message.error {
  background: rgba(255, 0, 0, 0.15);
  border-color: #ff0000;
  color: #ff6b6b;
}

.refresh-btn {
  width: 100%;
  padding: 12px;
  margin-top: 12px;
  background: rgba(0, 255, 0, 0.1);
  border: 1px solid #00ff00;
  border-radius: 6px;
  color: #00ff00;
  cursor: pointer;
  font-weight: bold;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.refresh-btn:hover:not(:disabled) {
  background: rgba(0, 255, 0, 0.2);
  transform: scale(1.02);
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Scrollbar styling */
.debug-content::-webkit-scrollbar {
  width: 8px;
}

.debug-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
}

.debug-content::-webkit-scrollbar-thumb {
  background: rgba(0, 255, 0, 0.3);
  border-radius: 4px;
}

.debug-content::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 255, 0, 0.5);
}
</style>
