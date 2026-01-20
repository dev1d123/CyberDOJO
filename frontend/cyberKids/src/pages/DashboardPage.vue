<template>
  <div class="dashboard-page">
    <!-- Debug Menu -->
    <DebugMenu />
    
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Cargando...</p>
    </div>

    <div v-else-if="error" class="error-container">
      <p class="error-text">{{ error }}</p>
      <button @click="loadUserData" class="retry-button">Reintentar</button>
    </div>

    <div v-else class="dashboard-container">
      <!-- Header with Avatar and Welcome -->
      <div class="header-section">
        <div class="avatar-container">
          <img 
            :src="user.avatar || placeholderAvatar" 
            alt="Avatar" 
            class="avatar-image"
          />
        </div>
        <h1 class="welcome-text">¡Bienvenido, <span class="username">{{ user.username }}</span>!</h1>
        <div class="credits-badge">
          <span class="coin-icon">💰</span>
          <span class="credits-amount">{{ user.cybercreds || 0 }} CyberCredits</span>
        </div>
      </div>

      <!-- Menu Grid -->
      <div class="menu-grid">
        <!-- Modo Historia -->
        <div
          class="menu-card"
          v-pet-hint="{ behavior: 'hover_module', vars: { target: 'Modo Historia' }, click: { behavior: 'open_page', vars: { target: 'Modo Historia' }, ttlMs: 1600, priority: 1 } }"
          @click="goToStoryMode"
        >
          <div class="card-gif-container">
            <img src="/src/assets/gif/historyGif.gif" alt="Modo Historia" class="card-gif" />
          </div>
          <h2 class="card-title">Modo Historia</h2>
          <p class="card-description">Vive aventuras y aprende</p>
        </div>

        <!-- Desafíos -->
        <div
          class="menu-card"
          v-pet-hint="{ behavior: 'hover_module', vars: { target: 'Desafíos' }, click: { behavior: 'open_page', vars: { target: 'Desafíos' }, ttlMs: 1600, priority: 1 } }"
          @click="goToChallenges"
        >
          <div class="card-gif-container">
            <img src="/src/assets/gif/challengeGif.gif" alt="Desafíos" class="card-gif" />
          </div>
          <h2 class="card-title">Desafíos</h2>
          <p class="card-description">Pon a prueba tus habilidades</p>
        </div>

        <!-- Tienda -->
        <div
          class="menu-card"
          v-pet-hint="{ behavior: 'hover_module', vars: { target: 'Tienda' }, click: { behavior: 'open_page', vars: { target: 'Tienda' }, ttlMs: 1600, priority: 1 } }"
          @click="goToShop"
        >
          <div class="card-gif-container">
            <img src="/src/assets/gif/shopGif.gif" alt="Tienda" class="card-gif" />
          </div>
          <h2 class="card-title">Tienda</h2>
          <p class="card-description">Compra accesorios geniales</p>
        </div>

        <!-- Perfil -->
        <div
          class="menu-card"
          v-pet-hint="{ behavior: 'hover_module', vars: { target: 'Perfil' }, click: { behavior: 'open_page', vars: { target: 'Perfil' }, ttlMs: 1600, priority: 1 } }"
          @click="goToProfile"
        >
          <div class="card-gif-container">
            <img src="/src/assets/gif/settingGif.gif" alt="Perfil" class="card-gif" />
          </div>
          <h2 class="card-title">Perfil</h2>
          <p class="card-description">Personaliza tu cuenta</p>
        </div>
      </div>

      <!-- Logout Button -->
      <button
        data-logout-btn
        v-pet-hint="{ behavior: 'hover_button', vars: { target: 'cerrar sesión' } }"
        @click="handleLogout"
        class="logout-button"
      >
        Cerrar Sesión
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import type { UserDto } from '../dto/user.dto';
import { UserService } from '../services/user.service';
import { AudioService } from '../services/audio.service';
import DebugMenu from '../components/DebugMenu.vue';

const router = useRouter();

const user = ref<UserDto>({
  user_id: 0,
  username: '',
  email: '',
  avatar: '',
  cybercreds: 0,
});

const loading = ref(true);
const error = ref<string | null>(null);

const placeholderAvatar = 'https://api.dicebear.com/7.x/adventurer/png?seed=Default';

onMounted(async () => {
  await loadUserData();
});

const loadUserData = async () => {
  loading.value = true;
  error.value = null;

  try {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }

    const me = await UserService.getCurrentUser();
    console.log('👤 Dashboard /auth/me/ response:', me);
    user.value = {
      ...user.value,
      ...me,
    };

    if (me?.user_id) {
      localStorage.setItem('user_id', String(me.user_id));
    }
  } catch (err: any) {
    console.error('Error loading user data:', err);
    error.value = 'No se pudo cargar tu información. Por favor, intenta de nuevo.';
  } finally {
    loading.value = false;
  }
};

const goToStoryMode = () => {
  router.push('/history');
};

const goToChallenges = () => {
  router.push('/challenges');
};

const goToShop = () => {
  router.push('/shop');
};

const goToProfile = () => {
  router.push('/profile');
};

const handleLogout = () => {
  AudioService.cleanup();
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user_id');
  router.push('/');
};
</script>

<style scoped>
.dashboard-page {
  height: 100vh;
  width: 100vw;
  box-sizing: border-box;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 200% 200%;
  animation: gradientMove 12s ease-in-out infinite;
  padding: clamp(12px, 2.5vh, 24px);
  overflow: hidden;
  display: flex;
  justify-content: center;
}

@keyframes gradientMove {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: white;
}

.spinner {
  width: 60px;
  height: 60px;
  border: 6px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-text {
  font-size: 1.2rem;
  margin-bottom: 1rem;
}

.retry-button {
  padding: 1rem 2rem;
  font-size: 1.1rem;
}

.dashboard-container {
  max-width: 1200px;
  width: 100%;
  height: 100%;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: clamp(8px, 1.4vh, 14px);
  min-height: 0;
}

.header-section {
  text-align: center;
  flex: 0 0 auto;
  margin-bottom: 0;
}

.avatar-container {
  display: inline-block;
  margin-bottom: clamp(8px, 1.6vh, 14px);
}

.avatar-image {
  width: clamp(72px, 14vh, 120px);
  height: clamp(72px, 14vh, 120px);
  border-radius: 50%;
  border: 4px solid white;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  background: white;
  object-fit: cover;
}

.welcome-text {
  font-size: clamp(1.4rem, 3.2vw, 2.4rem);
  color: white;
  text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.3);
  margin-bottom: clamp(6px, 1.2vh, 12px);
}

.username {
  color: #ffd700;
  text-shadow: 
    2px 2px 0px #ff6b6b,
    4px 4px 6px rgba(0, 0, 0, 0.3);
}

.credits-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: white;
  padding: clamp(8px, 1.4vh, 12px) clamp(12px, 2.2vh, 18px);
  border-radius: 50px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.coin-icon {
  font-size: 1.5rem;
}

.credits-amount {
  font-size: clamp(0.95rem, 1.4vw, 1.1rem);
  font-weight: bold;
  color: #667eea;
}

.menu-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: clamp(10px, 2vh, 18px);
  flex: 1 1 auto;
  min-height: 0;
  align-content: stretch;
  grid-auto-rows: 1fr;
}

.menu-card {
  background: white;
  border-radius: 22px;
  padding: clamp(12px, 2vh, 18px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  border: 4px solid transparent;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: clamp(8px, 1.3vh, 12px);
  min-height: 0;
}

.menu-card:hover {
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
  border-color: #ffd700;
}

.card-gif-container {
  width: 100%;
  flex: 1 1 auto;
  min-height: clamp(80px, 16vh, 160px);
  margin-bottom: 0;
  border-radius: 15px;
  overflow: hidden;
  background: #f5f5f5;
}

.card-gif {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-title {
  font-size: clamp(1.25rem, 2.2vw, 1.75rem);
  color: #667eea;
  margin-bottom: 0;
}

.card-description {
  font-size: clamp(0.9rem, 1.3vw, 1rem);
  color: #666;
}

.logout-button {
  display: block;
  margin: 0 auto;
  flex: 0 0 auto;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid white;
  backdrop-filter: blur(10px);
  padding: clamp(10px, 1.8vh, 14px) clamp(16px, 3vh, 22px);
  border-radius: 14px;
}

.logout-button:hover {
  background: rgba(255, 255, 255, 0.3);
}

@media (max-width: 768px) {
  .welcome-text {
    font-size: clamp(1.25rem, 5vw, 1.8rem);
  }

  .card-title {
    font-size: clamp(1.15rem, 4.2vw, 1.55rem);
  }
}

@media (max-width: 480px) {
  .dashboard-page {
    padding: 12px;
  }

  .menu-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .menu-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
</style>
