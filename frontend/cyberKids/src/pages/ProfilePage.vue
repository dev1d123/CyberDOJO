<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import BackToDashboardButton from '../components/BackToDashboardButton.vue';
import type { CountryDto } from '../dto/country.dto';
import type { UserDto, UserPreferencesDto } from '../dto/user.dto';
import type { UserPet } from '../dto/pet.dto';
import { CountryService } from '../services/country.service';
import { UserService } from '../services/user.service';
import { PetService } from '../services/pet.service';
import petsData from '../data/pets.json';

import pet1Img from '@/assets/images/pet1.png';
import pet2Img from '@/assets/images/pet2.png';
import pet3Img from '@/assets/images/pet3.png';
import pet4Img from '@/assets/images/pet4.png';
import pet5Img from '@/assets/images/pet5.png';

const loading = ref(true);
const saving = ref(false);
const error = ref<string | null>(null);
const success = ref<string | null>(null);

const user = ref<UserDto | null>(null);
const countries = ref<CountryDto[]>([]);
const userPets = ref<UserPet[]>([]);

const prefs = ref<UserPreferencesDto | null>(null);

const formUsername = ref('');
const formEmail = ref('');
const formCountry = ref<number | ''>('');
const avatarFile = ref<File | null>(null);

const receiveNewsletters = ref(false);
const darkMode = ref(false);
const age = ref<number | ''>('');

const passwordCurrent = ref('');
const passwordNew = ref('');
const passwordNewConfirm = ref('');

const petImageMap: Record<number, string> = {
  7: pet1Img,
  8: pet2Img,
  9: pet3Img,
  10: pet4Img,
  11: pet5Img,
};

const countryName = computed(() => {
  if (!user.value?.country) return '—';
  const c = countries.value.find((x) => x.country_id === user.value?.country);
  return c?.name ?? `ID ${user.value.country}`;
});

const avatarPreviewUrl = computed(() => {
  if (avatarFile.value) return URL.createObjectURL(avatarFile.value);
  return user.value?.avatar || null;
});

const clearMessages = () => {
  error.value = null;
  success.value = null;
};

const loadAll = async () => {
  loading.value = true;
  clearMessages();

  try {
    const [me, countryList] = await Promise.all([
      UserService.getCurrentUser(),
      CountryService.getAllCountries(),
    ]);

    user.value = me;
    countries.value = countryList;

    formUsername.value = me.username ?? '';
    formEmail.value = me.email ?? '';
    formCountry.value = (me.country ?? '') as any;

    // Preferencias vienen por endpoint aparte
    const p = (await UserService.getPreferences()) as any;
    prefs.value = {
      preference_id: p?.preference_id,
      receive_newsletters: Boolean(p?.receive_newsletters),
      dark_mode: Boolean(p?.dark_mode),
      base_content: p?.base_content ?? null,
      tone_instructions: p?.tone_instructions ?? null,
      age: p?.age ?? null,
    };

    receiveNewsletters.value = Boolean(prefs.value.receive_newsletters);
    darkMode.value = Boolean(prefs.value.dark_mode);
    age.value = prefs.value.age ?? '';

    // Cargar mascotas del usuario
    console.log('🐾 [ProfilePage] Obteniendo mascotas del usuario con user_id:', me.user_id);
    const response = await PetService.getUserPets(me.user_id);
    console.log('✅ [ProfilePage] Respuesta de mascotas del backend:', response);
    
    // El backend devuelve una respuesta paginada con structure: { count, next, previous, results }
    const pets = Array.isArray(response) ? response : (response.results || []);
    console.log('📊 [ProfilePage] Mascotas extraídas:', pets);
    console.log('📊 [ProfilePage] Cantidad de mascotas:', pets.length);
    console.log('🔍 [ProfilePage] Detalles de cada mascota:', pets.map(p => ({
      user_pet_id: p.user_pet_id,
      pet_id: p.pet,
      is_equipped: p.is_equipped
    })));
    userPets.value = pets;
    console.log('💾 [ProfilePage] userPets.value actualizado:', userPets.value);
  } catch (e: any) {
    console.error('❌ [ProfilePage] Error:', e);
    error.value = 'No se pudo cargar tu perfil. Intenta de nuevo.';
  } finally {
    loading.value = false;
  }
};

const ownedPetsWithImages = computed(() => {
  if (!Array.isArray(userPets.value)) return [];
  return userPets.value.map((userPet) => {
    const petData = petsData.find(p => p.pet_id === userPet.pet);
    return {
      ...userPet,
      name: petData?.name || `Pet ${userPet.pet}`,
      image: petImageMap[userPet.pet] || pet1Img,
    };
  });
});

const equipPet = async (petId: number) => {
  saving.value = true;
  clearMessages();

  try {
    await PetService.equipPet(petId);
    
    // Actualizar estado local
    userPets.value = userPets.value.map(p => ({
      ...p,
      is_equipped: p.pet === petId,
    }));
    
    success.value = '¡Mascota equipada!';
  } catch (e: any) {
    console.error(e);
    error.value = 'No se pudo equipar la mascota.';
  } finally {
    saving.value = false;
  }
};

onMounted(async () => {
  await loadAll();
});

const onPickAvatar = (ev: Event) => {
  const input = ev.target as HTMLInputElement;
  if (!input.files || input.files.length === 0) return;
  avatarFile.value = input.files[0] ?? null;
};

const saveProfile = async () => {
  if (!user.value) return;

  saving.value = true;
  clearMessages();

  try {
    // Perfil (username/country/avatar)
    const update = {
      username: formUsername.value.trim() || undefined,
      country: formCountry.value === '' ? undefined : Number(formCountry.value),
      avatarFile: avatarFile.value ?? undefined,
    };

    const res = await UserService.updateMeMultipart(update);

    // Guardar tokens nuevos
    if (res?.tokens?.access) localStorage.setItem('access_token', res.tokens.access);
    if (res?.tokens?.refresh) localStorage.setItem('refresh_token', res.tokens.refresh);

    user.value = res.user;
    formUsername.value = res.user.username ?? '';
    formEmail.value = res.user.email ?? '';
    formCountry.value = (res.user.country ?? '') as any;
    avatarFile.value = null;

    success.value = 'Perfil actualizado exitosamente.';
  } catch (e: any) {
    console.error(e);
    error.value = typeof e === 'string' ? e : 'No se pudo actualizar el perfil.';
  } finally {
    saving.value = false;
  }
};

const savePreferences = async () => {
  saving.value = true;
  clearMessages();

  try {
    const res = await UserService.updatePreferences({
      receive_newsletters: receiveNewsletters.value,
      dark_mode: darkMode.value,
      age: age.value === '' ? null : Number(age.value),
    });

    if ((res as any)?.tokens?.access) localStorage.setItem('access_token', (res as any).tokens.access);
    if ((res as any)?.tokens?.refresh) localStorage.setItem('refresh_token', (res as any).tokens.refresh);

    success.value = 'Preferencias guardadas.';
  } catch (e: any) {
    console.error(e);
    error.value = 'No se pudieron guardar tus preferencias.';
  } finally {
    saving.value = false;
  }
};

const changePassword = async () => {
  saving.value = true;
  clearMessages();

  try {
    if (!passwordCurrent.value || !passwordNew.value || !passwordNewConfirm.value) {
      error.value = 'Completa todos los campos de contraseña.';
      return;
    }
    if (passwordNew.value !== passwordNewConfirm.value) {
      error.value = 'La nueva contraseña no coincide.';
      return;
    }
    if (passwordNew.value.length < 6) {
      error.value = 'La nueva contraseña debe tener al menos 6 caracteres.';
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) {
      error.value = 'No hay sesión activa.';
      return;
    }

    const response = await fetch('https://juliojc.pythonanywhere.com/api/users/auth/me/change-password/', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        current_password: passwordCurrent.value,
        new_password: passwordNew.value,
        new_password_confirm: passwordNewConfirm.value,
      }),
    });

    const contentType = response.headers.get('content-type') || '';
    const body = contentType.includes('application/json') ? await response.json() : await response.text();

    if (!response.ok) {
      console.error(body);
      error.value = (body as any)?.error ?? 'No se pudo cambiar la contraseña.';
      return;
    }

    if ((body as any)?.tokens?.access) localStorage.setItem('access_token', (body as any).tokens.access);
    if ((body as any)?.tokens?.refresh) localStorage.setItem('refresh_token', (body as any).tokens.refresh);

    passwordCurrent.value = '';
    passwordNew.value = '';
    passwordNewConfirm.value = '';

    success.value = 'Contraseña actualizada.';
  } finally {
    saving.value = false;
  }
};
</script>

<template>
  <div class="profile-page">
    <BackToDashboardButton />

    <div class="container">
      <header class="header">
        <h1 class="title">Perfil</h1>
        <p class="subtitle">Personaliza tu cuenta y tus preferencias</p>
      </header>

      <div v-if="loading" class="state">Cargando perfil…</div>
      <div v-else>
        <div v-if="error" class="alert alert-error">{{ error }}</div>
        <div v-if="success" class="alert alert-success">{{ success }}</div>

        <section class="grid">
          <!-- Card: Información -->
          <div class="card">
            <div class="card-header">
              <h2 class="card-title">Tu información</h2>
              <span class="pill">CyberCredits: {{ user?.cybercreds ?? 0 }}</span>
            </div>

            <div class="avatar-row">
              <div class="avatar-wrap">
                <img v-if="avatarPreviewUrl" :src="avatarPreviewUrl" class="avatar" alt="Avatar" />
                <div v-else class="avatar placeholder">👤</div>
              </div>

              <label class="file-btn" for="avatarUpload">
                <input id="avatarUpload" class="file-input" type="file" accept="image/*" @change="onPickAvatar" />
                Cambiar avatar
              </label>

              <div class="small">País actual: <b>{{ countryName }}</b></div>
            </div>

            <div class="form">
              <label class="field">
                <span class="label">Usuario</span>
                <input v-model="formUsername" class="input" type="text" placeholder="Tu nombre" />
              </label>

              <label class="field">
                <span class="label">Email</span>
                <input v-model="formEmail" class="input" type="email" placeholder="Tu email" disabled />
                <span class="hint">Por ahora el email no se edita desde aquí.</span>
              </label>

              <label class="field">
                <span class="label">País</span>
                <select v-model="formCountry" class="input">
                  <option value="">Selecciona un país</option>
                  <option v-for="c in countries" :key="c.country_id" :value="c.country_id">
                    {{ c.name }}
                  </option>
                </select>
              </label>

              <button class="primary" type="button" :disabled="saving" @click="saveProfile">
                {{ saving ? 'Guardando…' : 'Guardar perfil' }}
              </button>
            </div>
          </div>

          <!-- Card: Preferencias -->
          <div class="card">
            <div class="card-header">
              <h2 class="card-title">Preferencias</h2>
            </div>

            <div class="prefs">
              <label class="toggle">
                <input v-model="receiveNewsletters" type="checkbox" />
                <span class="toggle-ui" aria-hidden="true"></span>
                <span class="toggle-text">Recibir newsletters</span>
              </label>

              <label class="toggle">
                <input v-model="darkMode" type="checkbox" />
                <span class="toggle-ui" aria-hidden="true"></span>
                <span class="toggle-text">Modo oscuro</span>
              </label>

              <label class="field">
                <span class="label">Edad</span>
                <input v-model="age" class="input" type="number" min="1" max="120" placeholder="(opcional)" />
              </label>

              <button class="primary" type="button" :disabled="saving" @click="savePreferences">
                {{ saving ? 'Guardando…' : 'Guardar preferencias' }}
              </button>
            </div>
          </div>

          <!-- Card: Contraseña -->
          <div class="card card-wide">
            <div class="card-header">
              <h2 class="card-title">Seguridad</h2>
              <span class="hint">Cambia tu contraseña cuando lo necesites.</span>
            </div>

            <div class="form three">
              <label class="field">
                <span class="label">Contraseña actual</span>
                <input v-model="passwordCurrent" class="input" type="password" autocomplete="current-password" />
              </label>

              <label class="field">
                <span class="label">Nueva contraseña</span>
                <input v-model="passwordNew" class="input" type="password" autocomplete="new-password" />
              </label>

              <label class="field">
                <span class="label">Confirmar nueva</span>
                <input v-model="passwordNewConfirm" class="input" type="password" autocomplete="new-password" />
              </label>

              <button class="danger" type="button" :disabled="saving" @click="changePassword">
                {{ saving ? 'Actualizando…' : 'Actualizar contraseña' }}
              </button>
            </div>
          </div>

          <!-- Card: Mascotas -->
          <div class="card card-wide">
            <div class="card-header">
              <h2 class="card-title">🐾 Mis Mascotas</h2>
              <span class="hint">Equipa tu mascota favorita</span>
            </div>

            <div v-if="ownedPetsWithImages.length === 0" class="empty-pets">
              <p>No tienes mascotas aún. ¡Visita la tienda para comprar algunas!</p>
            </div>

            <div v-else class="pets-grid">
              <div
                v-for="pet in ownedPetsWithImages"
                :key="pet.user_pet_id"
                class="pet-card"
                :class="{ equipped: pet.is_equipped }"
              >
                <div class="pet-image-wrapper">
                  <img :src="pet.image" :alt="pet.name" class="pet-image" />
                  <div v-if="pet.is_equipped" class="equipped-badge">✓ EQUIPADO</div>
                </div>
                <div class="pet-info">
                  <h3 class="pet-name">{{ pet.name }}</h3>
                  <button
                    v-if="!pet.is_equipped"
                    class="equip-btn"
                    type="button"
                    :disabled="saving"
                    @click="equipPet(pet.pet)"
                  >
                    Equipar
                  </button>
                  <span v-else class="equipped-text">Actualmente equipado</span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-page {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  box-sizing: border-box;
  padding: clamp(12px, 2.5vh, 24px);

  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 200% 200%;
  animation: gradientMove 12s ease-in-out infinite;
}

@keyframes gradientMove {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.header {
  text-align: center;
  color: white;
}

.title {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3rem);
  text-shadow: 4px 4px 12px rgba(0, 0, 0, 0.25);
}

.subtitle {
  margin: 6px 0 0;
  font-weight: 900;
  opacity: 0.92;
}

.state {
  text-align: center;
  color: white;
  font-weight: 900;
}

.alert {
  padding: 12px 14px;
  border-radius: 18px;
  font-weight: 900;
  border: 2px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
}

.alert-error {
  background: rgba(255, 107, 107, 0.22);
  color: white;
}

.alert-success {
  background: rgba(72, 198, 239, 0.22);
  color: white;
}

.grid {
  flex: 1 1 auto;
  min-height: 0;
  display: grid;
  gap: 16px;
  grid-template-columns: 1fr 1fr;
  grid-auto-rows: min-content;
  overflow: auto;
  padding-bottom: 8px;
}

.card {
  border-radius: 26px;
  background: rgba(15, 15, 25, 0.72);
  border: 2px solid rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(10px);
  box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
  padding: 16px;
  color: white;
}

.card-wide {
  grid-column: 1 / -1;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.card-title {
  margin: 0;
  font-size: 1.6rem;
}

.pill {
  padding: 8px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.18);
  font-weight: 1000;
}

.avatar-row {
  display: grid;
  grid-template-columns: 110px 1fr;
  gap: 14px;
  align-items: center;
  margin-bottom: 14px;
}

.avatar-wrap {
  width: 110px;
  height: 110px;
  border-radius: 26px;
  background: rgba(255, 255, 255, 0.14);
  border: 2px solid rgba(255, 255, 255, 0.18);
  display: grid;
  place-items: center;
  overflow: hidden;
  box-shadow: 0 16px 34px rgba(0, 0, 0, 0.25);
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar.placeholder {
  font-size: 3rem;
}

.file-input {
  position: absolute;
  opacity: 0;
  width: 1px;
  height: 1px;
  pointer-events: none;
}

.file-btn {
  justify-self: start;
  width: fit-content;
  border-radius: 18px;
  padding: 12px 14px;
  cursor: pointer;
  font-weight: 1000;
  color: #111;
  background: #fee440;
  box-shadow: 0 14px 26px rgba(254, 228, 64, 0.22);
  transition: transform 160ms ease, filter 160ms ease;
}

.file-btn:hover {
  transform: translateY(-3px);
  filter: saturate(1.05);
}

.small {
  grid-column: 2;
  opacity: 0.9;
}

.form {
  display: grid;
  gap: 12px;
}

.form.three {
  grid-template-columns: 1fr 1fr 1fr;
  align-items: end;
}

.field {
  display: grid;
  gap: 6px;
}

.label {
  font-weight: 1000;
  opacity: 0.95;
}

.input {
  width: 100%;
  border-radius: 16px;
  border: 2px solid rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.1);
  color: white;
  padding: 12px 12px;
  font-weight: 900;
  outline: none;
}

.input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.input:focus {
  border-color: rgba(72, 198, 239, 0.75);
  box-shadow: 0 0 0 4px rgba(72, 198, 239, 0.18);
}

.hint {
  font-size: 0.95rem;
  opacity: 0.82;
}

.primary,
.danger {
  border: none;
  padding: 12px 14px;
  border-radius: 18px;
  font-weight: 1000;
  cursor: pointer;
  transition: transform 160ms ease, filter 160ms ease;
}

.primary {
  background: linear-gradient(135deg, #48c6ef 0%, #6f86d6 100%);
  color: white;
  box-shadow: 0 16px 34px rgba(72, 198, 239, 0.35);
}

.primary:hover {
  transform: translateY(-3px);
  filter: saturate(1.05);
}

.primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.danger {
  background: linear-gradient(135deg, #ff6b6b, #ff8e53);
  color: white;
  box-shadow: 0 16px 34px rgba(255, 107, 107, 0.35);
}

.danger:hover {
  transform: translateY(-3px);
  filter: saturate(1.05);
}

.prefs {
  display: grid;
  gap: 12px;
}

.toggle {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-weight: 1000;
}

.toggle input {
  position: absolute;
  opacity: 0;
}

.toggle-ui {
  width: 56px;
  height: 32px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.16);
  border: 2px solid rgba(255, 255, 255, 0.18);
  position: relative;
  box-shadow: inset 0 0 0 2px rgba(0, 0, 0, 0.08);
  transition: all 0.18s ease;
}

.toggle-ui::after {
  content: '';
  width: 26px;
  height: 26px;
  border-radius: 999px;
  position: absolute;
  top: 50%;
  left: 3px;
  transform: translateY(-50%);
  background: white;
  box-shadow: 0 10px 22px rgba(0, 0, 0, 0.25);
  transition: all 0.18s ease;
}

.toggle input:checked + .toggle-ui {
  background: rgba(72, 198, 239, 0.35);
  border-color: rgba(72, 198, 239, 0.6);
}

.toggle input:checked + .toggle-ui::after {
  left: 25px;
}

@media (max-width: 980px) {
  .grid {
    grid-template-columns: 1fr;
  }

  .form.three {
    grid-template-columns: 1fr;
  }
}

/* Pet styles */
.empty-pets {
  text-align: center;
  padding: 40px 20px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 700;
}

.pets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.pet-card {
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.18);
  border-radius: 18px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  transition: all 0.3s ease;
}

.pet-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

.pet-card.equipped {
  border-color: rgba(80, 227, 194, 0.8);
  background: rgba(80, 227, 194, 0.15);
}

.pet-image-wrapper {
  position: relative;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 140px;
}

.pet-image {
  max-width: 120px;
  height: auto;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.3));
  animation: petFloat 3s ease-in-out infinite;
}

@keyframes petFloat {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.equipped-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: rgba(80, 227, 194, 0.95);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 900;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.5px;
}

.pet-info {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.pet-name {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 900;
  text-align: center;
  color: white;
}

.equip-btn {
  width: 100%;
  border: none;
  padding: 8px 16px;
  border-radius: 12px;
  font-weight: 900;
  cursor: pointer;
  background: linear-gradient(135deg, #48c6ef 0%, #6f86d6 100%);
  color: white;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(72, 198, 239, 0.3);
}

.equip-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(72, 198, 239, 0.4);
}

.equip-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.equipped-text {
  color: rgba(80, 227, 194, 0.95);
  font-weight: 900;
  font-size: 0.9rem;
  text-align: center;
}
</style>
