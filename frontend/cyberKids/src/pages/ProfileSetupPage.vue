<template>
  <div class="profile-setup-page">
    <div class="setup-container">
      <!-- Progress indicator -->
      <div class="progress-header">
        <div class="progress-dots">
          <div class="dot active"></div>
          <div class="dot-line"></div>
          <div class="dot"></div>
        </div>
        <p class="step-text">Paso 1 de 2</p>
      </div>

      <div class="content-box">
        <h1 class="setup-title">¡Hola! 👋</h1>
        <p class="setup-subtitle">Cuéntanos un poco sobre ti</p>

        <!-- Avatar Selection -->
        <div class="avatar-section">
          <label class="form-label">Elige tu avatar</label>
          <div class="avatar-grid">
            <div 
              v-for="avatar in avatarOptions" 
              :key="avatar"
              class="avatar-option"
              :class="{ selected: formData.avatar === avatar }"
              @click="selectAvatar(avatar)"
            >
              <img :src="avatar" :alt="`Avatar ${avatar}`" />
            </div>

            <div
              class="avatar-option upload-option"
              :class="{ selected: isUploadedAvatarSelected }"
              @click="triggerAvatarUpload"
            >
              <img
                v-if="uploadedAvatarPreviewUrl"
                :src="uploadedAvatarPreviewUrl"
                alt="Avatar subido"
              />
              <div v-else class="upload-placeholder">
                <div class="upload-icon">📸</div>
                <div class="upload-text">Subir foto</div>
              </div>
            </div>
          </div>

          <input
            ref="avatarFileInput"
            class="hidden-file"
            type="file"
            accept="image/*"
            @change="onAvatarFileChange"
          />

          <p v-if="errors.avatar" class="error-text">{{ errors.avatar }}</p>
        </div>

        <!-- Username Field -->
        <div class="form-group">
          <label class="form-label">Nombre de usuario</label>
          <input
            v-model="formData.username"
            type="text"
            class="form-input"
            placeholder="Escribe tu nombre de usuario"
            maxlength="30"
          />
          <p v-if="errors.username" class="error-text">{{ errors.username }}</p>
        </div>

        <!-- Country Selection -->
        <div class="form-group">
          <label class="form-label">¿De dónde eres?</label>
          <select v-model="formData.country" class="form-select">
            <option value="">Selecciona tu país</option>
            <option 
              v-for="country in countries" 
              :key="country.country_id" 
              :value="country.country_id"
            >
              {{ country.name }}
            </option>
          </select>
          <p v-if="errors.country" class="error-text">{{ errors.country }}</p>
        </div>

        <!-- Submit Button -->
        <button 
          @click="handleSubmit" 
          class="submit-button"
          :disabled="isLoading"
        >
          {{ isLoading ? 'Guardando...' : 'Continuar →' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { UserService } from '../services/user.service';
import { CountryService } from '../services/country.service';
import type { ProfileSetupDto } from '../dto/user.dto';
import type { CountryDto } from '../dto/country.dto';

const router = useRouter();

const formData = ref<ProfileSetupDto>({
  username: '',
  country: '',
  avatar: '',
});

const errors = ref<{ username?: string; country?: string; avatar?: string }>({});
const isLoading = ref(false);

const avatarFileInput = ref<HTMLInputElement | null>(null);
const uploadedAvatarFile = ref<File | null>(null);
const uploadedAvatarPreviewUrl = ref<string>('');
const originalAvatarUrl = ref<string>('');

const isUploadedAvatarSelected = computed(() => !!uploadedAvatarFile.value);

// Opciones de avatares
const avatarOptions = ref([
  // Usar PNG (no SVG) para que el backend (ImageField/Pillow) lo acepte como imagen
  'https://api.dicebear.com/7.x/adventurer/png?seed=Felix',
  'https://api.dicebear.com/7.x/adventurer/png?seed=Luna',
  'https://api.dicebear.com/7.x/adventurer/png?seed=Max',
  'https://api.dicebear.com/7.x/adventurer/png?seed=Sophie',
  'https://api.dicebear.com/7.x/adventurer/png?seed=Leo',
  'https://api.dicebear.com/7.x/adventurer/png?seed=Mia',
  'https://api.dicebear.com/7.x/adventurer/png?seed=Oliver',
  'https://api.dicebear.com/7.x/adventurer/png?seed=Emma',
]);

// Lista de países desde el backend
const countries = ref<CountryDto[]>([]);

const decodeJwtPayload = (token: string): any | null => {
  try {
    const payloadPart = token.split('.')[1];
    if (!payloadPart) return null;

    const base64 = payloadPart.replace(/-/g, '+').replace(/_/g, '/');
    const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '=');
    return JSON.parse(atob(padded));
  } catch (e) {
    console.error('❌ Error decodificando JWT:', e);
    return null;
  }
};

const downloadImageAsFile = async (url: string): Promise<File> => {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`No se pudo descargar el avatar (status ${response.status})`);
  }

  const blob = await response.blob();
  const contentType = blob.type || 'image/png';
  const extension = contentType.includes('png') ? 'png' : contentType.includes('jpeg') ? 'jpg' : 'img';
  return new File([blob], `avatar.${extension}`, { type: contentType });
};

onMounted(async () => {
  console.log('🚀 ProfileSetupPage mounted');
  
  // Cargar países
  try {
    countries.value = await CountryService.getAllCountries();
    console.log('📋 Países cargados:', countries.value);
  } catch (error) {
    console.error('❌ Error cargando países:', error);
  }
  
  // Cargar el usuario autenticado
  try {
    const me = await UserService.getCurrentUser();
    console.log('👤 Usuario autenticado cargado (/auth/me/):', me);

    if (me?.user_id) {
      localStorage.setItem('user_id', String(me.user_id));
    }

    if (me?.username) {
      formData.value.username = me.username;
    }

    if (me?.country) {
      formData.value.country = me.country;
    }

    if (me?.avatar) {
      formData.value.avatar = me.avatar;
      originalAvatarUrl.value = me.avatar;
    }
  } catch (error) {
    console.error('❌ Error loading user data:', error);
  }

  // Seleccionar el primer avatar por defecto si no hay ninguno
  if (!formData.value.avatar) {
    formData.value.avatar = avatarOptions.value[0];
    console.log('🎨 Avatar por defecto seleccionado:', formData.value.avatar);
  }
});

onBeforeUnmount(() => {
  if (uploadedAvatarPreviewUrl.value) {
    URL.revokeObjectURL(uploadedAvatarPreviewUrl.value);
  }
});

const clearUploadedAvatar = () => {
  if (uploadedAvatarPreviewUrl.value) {
    URL.revokeObjectURL(uploadedAvatarPreviewUrl.value);
  }
  uploadedAvatarPreviewUrl.value = '';
  uploadedAvatarFile.value = null;
  if (avatarFileInput.value) {
    avatarFileInput.value.value = '';
  }
};

const selectAvatar = (avatar: string) => {
  clearUploadedAvatar();
  formData.value.avatar = avatar;
  console.log('🎭 Avatar seleccionado (URL):', avatar);
};

const triggerAvatarUpload = () => {
  errors.value.avatar = undefined;
  avatarFileInput.value?.click();
};

const onAvatarFileChange = (e: Event) => {
  const input = e.target as HTMLInputElement;
  const file = input.files?.[0] ?? null;
  if (!file) return;

  if (!file.type.startsWith('image/')) {
    errors.value.avatar = 'Por favor selecciona un archivo de imagen válido';
    console.error('❌ Archivo inválido:', { type: file.type, name: file.name });
    return;
  }

  clearUploadedAvatar();
  uploadedAvatarFile.value = file;
  uploadedAvatarPreviewUrl.value = URL.createObjectURL(file);
  formData.value.avatar = uploadedAvatarPreviewUrl.value;

  console.log('📷 Avatar file seleccionado:', {
    name: file.name,
    type: file.type,
    size: file.size,
  });
};

const validateForm = (): boolean => {
  console.log('🔍 Validando formulario...');
  errors.value = {};
  let isValid = true;

  if (!formData.value.username.trim()) {
    errors.value.username = 'El nombre de usuario es obligatorio';
    isValid = false;
  } else if (formData.value.username.length < 3) {
    errors.value.username = 'El nombre debe tener al menos 3 caracteres';
    isValid = false;
  }

  if (formData.value.country === '' || formData.value.country == null) {
    errors.value.country = 'Por favor selecciona tu país';
    isValid = false;
  }

  if (!formData.value.avatar) {
    errors.value.avatar = 'Por favor selecciona un avatar';
    isValid = false;
  }

  console.log('✅ Validación resultado:', isValid, formData.value);
  return isValid;
};

const handleSubmit = async () => {
  console.log('🚀 Iniciando submit...');
  
  if (!validateForm()) {
    console.log('❌ Formulario inválido');
    return;
  }

  isLoading.value = true;

  try {
    const countryId = typeof formData.value.country === 'string'
      ? Number(formData.value.country)
      : formData.value.country;

    if (!countryId || Number.isNaN(countryId)) {
      errors.value.country = 'Por favor selecciona tu país';
      throw new Error('country_id inválido');
    }

    console.log('📤 Datos a enviar:', {
      username: formData.value.username,
      country: countryId,
      avatar: formData.value.avatar,
      avatarFile: uploadedAvatarFile.value
        ? { name: uploadedAvatarFile.value.name, type: uploadedAvatarFile.value.type, size: uploadedAvatarFile.value.size }
        : null,
    });

    // Siempre usar multipart: backend espera ImageField para avatar
    let avatarFileToUpload: File | undefined;
    if (uploadedAvatarFile.value) {
      avatarFileToUpload = uploadedAvatarFile.value;
    } else {
      const selected = formData.value.avatar;
      const isPreset = !!selected && avatarOptions.value.includes(selected);
      const changedFromOriginal = !!selected && selected !== originalAvatarUrl.value;
      if (isPreset && changedFromOriginal) {
        try {
          console.log('🧩 Descargando avatar preset para subirlo como archivo...');
          avatarFileToUpload = await downloadImageAsFile(selected);
          console.log('✅ Avatar preset convertido a File:', {
            name: avatarFileToUpload.name,
            type: avatarFileToUpload.type,
            size: avatarFileToUpload.size,
          });
        } catch (e) {
          console.error('❌ No se pudo descargar el avatar preset:', e);
          errors.value.avatar = 'No se pudo descargar el avatar seleccionado. Intenta con otro o sube una foto.';
          throw e;
        }
      }
    }

    console.log('🧩 Enviando update multipart (/auth/me/update/) ...');
    const response = await UserService.updateMeMultipart({
      username: formData.value.username,
      country: countryId,
      avatarFile: avatarFileToUpload,
    });

    console.log('✅ Respuesta del servidor:', response);

    if (response?.tokens?.access && response?.tokens?.refresh) {
      localStorage.setItem('access_token', response.tokens.access);
      localStorage.setItem('refresh_token', response.tokens.refresh);

      const payload = decodeJwtPayload(response.tokens.access);
      if (payload?.user_id) {
        localStorage.setItem('user_id', String(payload.user_id));
      }
    }

    // Ir a la página de onboarding
    console.log('➡️ Redirigiendo a onboarding...');
    router.push('/onboarding');
  } catch (error: any) {
    console.error('❌ Error updating profile:', error);
    console.error('📋 Detalles del error:', error.response?.data || error);
    
    if (error.username) {
      errors.value.username = Array.isArray(error.username) ? error.username[0] : error.username;
    }
    if (error.country) {
      errors.value.country = Array.isArray(error.country) ? error.country[0] : error.country;
    }
    if (error.avatar) {
      errors.value.avatar = Array.isArray(error.avatar) ? error.avatar[0] : error.avatar;
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}

@keyframes bounce {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.profile-setup-page {
  height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  overflow: hidden;
  position: fixed;
  top: 0;
  left: 0;
}

.setup-container {
  max-width: 700px;
  width: 100%;
  max-height: 95vh;
  overflow-y: auto;
  animation: fadeInUp 0.6s ease;
}

.setup-container::-webkit-scrollbar {
  width: 8px;
}

.setup-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.setup-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.5);
  border-radius: 10px;
}

.progress-header {
  text-align: center;
  margin-bottom: 1.5rem;
  animation: fadeInUp 0.6s ease 0.2s both;
}

.progress-dots {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.dot.active {
  background: white;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
  animation: pulse 2s ease-in-out infinite;
}

.dot-line {
  width: 40px;
  height: 3px;
  background: rgba(255, 255, 255, 0.3);
}

.step-text {
  color: white;
  font-size: 1rem;
  font-weight: bold;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.content-box {
  background: white;
  border-radius: 30px;
  padding: 2.5rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: fadeInUp 0.6s ease 0.4s both;
}

.setup-title {
  font-size: 2.5rem;
  color: #667eea;
  text-align: center;
  margin-bottom: 0.5rem;
  animation: bounce 2s ease-in-out infinite;
}

.setup-subtitle {
  font-size: 1.2rem;
  color: #666;
  text-align: center;
  margin-bottom: 2rem;
}

.avatar-section {
  margin-bottom: 1.5rem;
}

.avatar-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.8rem;
  margin-top: 1rem;
}

.avatar-option {
  aspect-ratio: 1;
  border: 3px solid transparent;
  border-radius: 15px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #f5f5f5;
  animation: fadeInUp 0.4s ease backwards;
  opacity: 1 !important; /* Siempre visible */
}

.avatar-option:nth-child(1) { animation-delay: 0.5s; }
.avatar-option:nth-child(2) { animation-delay: 0.55s; }
.avatar-option:nth-child(3) { animation-delay: 0.6s; }
.avatar-option:nth-child(4) { animation-delay: 0.65s; }
.avatar-option:nth-child(5) { animation-delay: 0.7s; }
.avatar-option:nth-child(6) { animation-delay: 0.75s; }
.avatar-option:nth-child(7) { animation-delay: 0.8s; }
.avatar-option:nth-child(8) { animation-delay: 0.85s; }

.avatar-option:hover {
  transform: scale(1.1) rotate(5deg);
  border-color: #667eea;
}

.avatar-option.selected {
  border-color: #667eea;
  box-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
  transform: scale(1.08);
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
}

.avatar-option img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-option {
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, rgba(254, 228, 64, 0.35) 0%, rgba(255, 107, 107, 0.15) 60%, rgba(102, 126, 234, 0.18) 100%);
}

.upload-placeholder {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  gap: 6px;
  padding: 10px;
  text-align: center;
}

.upload-icon {
  font-size: 1.8rem;
  animation: pulse 1.6s ease-in-out infinite;
}

.upload-text {
  font-weight: 900;
  color: #334155;
  font-size: 0.95rem;
}

.hidden-file {
  display: none;
}

.form-group {
  margin-bottom: 1.2rem;
}

.form-label {
  display: block;
  font-size: 1.1rem;
  color: #333;
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.form-input,
.form-select {
  width: 100%;
  padding: 0.9rem 1.2rem;
  border: 3px solid #e0e0e0;
  border-radius: 15px;
  font-size: 1rem;
  font-family: inherit;
  transition: all 0.3s ease;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 10px rgba(102, 126, 234, 0.2);
  transform: scale(1.02);
}

.form-select {
  cursor: pointer;
  background: white;
}

.error-text {
  color: #ff6b6b;
  font-size: 0.9rem;
  margin-top: 0.5rem;
  animation: fadeInUp 0.3s ease;
}

.submit-button {
  width: 100%;
  padding: 1.1rem;
  font-size: 1.2rem;
  margin-top: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 15px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.submit-button::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.submit-button:hover:not(:disabled)::before {
  width: 300px;
  height: 300px;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 15px 40px rgba(102, 126, 234, 0.5);
}

.submit-button:active:not(:disabled) {
  transform: translateY(-1px);
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .content-box {
    padding: 2rem;
  }

  .setup-title {
    font-size: 2rem;
  }

  .avatar-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 480px) {
  .content-box {
    padding: 1.5rem;
  }

  .setup-title {
    font-size: 1.8rem;
  }

  .avatar-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
