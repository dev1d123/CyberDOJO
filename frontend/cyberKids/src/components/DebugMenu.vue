<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';

const isOpen = ref(false);
const loading = ref(false);
const message = ref('');

// User data
const userId = ref<number | null>(null);
const equippedPetId = ref<number | null>(null);
const ownedPets = ref<any[]>([]);
const currentCybercreds = ref(0);

// Form inputs
const selectedPetToEquip = ref<number | null>(null);
const creditsToAdd = ref(100);

const API_BASE_URL = 'https://juliojc.pythonanywhere.com/api';

onMounted(async () => {
  await loadDebugData();
});

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
    await loadDebugData();
  } catch (error: any) {
    console.error('Error equipping pet:', error);
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
    const response = await axios.post(
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
  font-size: 14px;
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
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  color: #00ff00;
  font-size: 24px;
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
  font-size: 14px;
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
  font-size: 12px;
  font-weight: bold;
}

.value {
  color: #fff;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.empty-state {
  color: rgba(255, 255, 255, 0.5);
  font-style: italic;
  font-size: 12px;
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
  font-size: 12px;
}

.pet-name {
  color: #fff;
  flex: 1;
}

.pet-id {
  color: rgba(0, 255, 0, 0.7);
  font-family: 'Courier New', monospace;
  font-size: 11px;
}

.equipped-badge {
  color: #00ff00;
  font-weight: bold;
  font-size: 11px;
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
  font-size: 12px;
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
  font-size: 12px;
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
  font-size: 12px;
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
  font-size: 13px;
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
