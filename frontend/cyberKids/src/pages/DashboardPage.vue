<template>
  <div class="dashboard-page">
    <!-- Debug Menu -->
    <DebugMenu />
    
    <!-- Vue Tour -->
    <v-tour name="dashboardTour" :steps="tourSteps" :options="tourOptions" :callbacks="tourCallbacks">
      <template #default="tour">
        <transition name="fade">
          <v-step
            v-if="tour.currentStep !== -1"
            :key="tour.currentStep"
            :step="tour.steps[tour.currentStep]"
            :previous-step="tour.previousStep"
            :next-step="tour.nextStep"
            :stop="tour.stop"
            :is-first="tour.isFirst"
            :is-last="tour.isLast"
            :labels="tour.labels"
          >
            <template #actions>
              <div class="tour-actions">
                <button v-if="!tour.isFirst" @click="tour.previousStep" class="tour-btn tour-btn-secondary">
                  Anterior
                </button>
                <button v-if="!tour.isLast" @click="tour.nextStep" class="tour-btn tour-btn-primary">
                  Siguiente
                </button>
                <button v-if="tour.isLast" @click="tour.stop" class="tour-btn tour-btn-success">
                  ¡Entendido!
                </button>
              </div>
            </template>
          </v-step>
        </transition>
      </template>
    </v-tour>
    
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
      <div class="header-section" data-tour-step="welcome">
        <div class="avatar-container">
          <img 
            :src="user.avatar || placeholderAvatar" 
            alt="Avatar" 
            class="avatar-image"
          />
        </div>
        <h1 class="welcome-text">¡Bienvenido, <span class="username">{{ user.username }}</span>!</h1>
        <div class="credits-badge" data-tour-step="credits">
          <span class="coin-icon">💰</span>
          <span class="credits-amount">{{ user.cybercreds || 0 }} CyberCredits</span>
        </div>
      </div>

      <!-- Menu Grid -->
      <div class="menu-grid">
        <!-- Modo Historia -->
        <div
          class="menu-card"
          data-tour-step="history"
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
          data-tour-step="challenges"
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
          data-tour-step="shop"
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
          data-tour-step="profile"
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
import { ref, onMounted, getCurrentInstance } from 'vue';
import { useRouter } from 'vue-router';
import type { UserDto } from '../dto/user.dto';
import { UserService } from '../services/user.service';
import { AudioService } from '../services/audio.service';
import DebugMenu from '../components/DebugMenu.vue';

const router = useRouter();
const instance = getCurrentInstance();

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

// Tour configuration
const tourSteps = ref([
  {
    target: '[data-tour-step="welcome"]',
    header: {
      title: '¡Bienvenido a CyberDOJO! 🎉',
    },
    content: 'Este es tu <strong>Dashboard</strong>, tu punto central para acceder a todas las funcionalidades. Aquí puedes ver tu avatar y tu información personal.',
    placement: 'bottom',
  },
  {
    target: '[data-tour-step="credits"]',
    header: {
      title: 'CyberCredits 💰',
    },
    content: 'Estos son tus <strong>CyberCredits</strong>, la moneda virtual de la aplicación. Gánalos completando misiones y úsalos para comprar mascotas y temas de audio en la tienda.',
    placement: 'bottom',
  },
  {
    target: '[data-tour-step="history"]',
    header: {
      title: 'Modo Historia 🏝️',
    },
    content: '<strong>Modo Historia</strong> te lleva a vivir aventuras en 6 escenarios diferentes de ciberseguridad. Aquí enfrentarás conversaciones con antagonistas virtuales y aprenderás a detectar señales de alerta. ¡Gana puntos y CyberCredits por cada misión completada!',
    placement: 'right',
  },
  {
    target: '[data-tour-step="challenges"]',
    header: {
      title: 'Desafíos ⚡',
    },
    content: '<strong>Desafíos</strong> te permite poner a prueba tus habilidades con retos específicos. Ideal para practicar y perfeccionar lo que has aprendido.',
    placement: 'right',
  },
  {
    target: '[data-tour-step="shop"]',
    header: {
      title: 'Tienda 🛒',
    },
    content: 'En la <strong>Tienda</strong> puedes gastar tus CyberCredits en:<br>🐾 <strong>Mascotas</strong> - Compañeros virtuales que te acompañan en tu aventura<br>🎵 <strong>Temas de Audio</strong> - Personaliza los sonidos de la aplicación',
    placement: 'left',
  },
  {
    target: '[data-tour-step="profile"]',
    header: {
      title: 'Perfil 👤',
    },
    content: 'En tu <strong>Perfil</strong> puedes:<br>• Ver tu progreso y estadísticas<br>• Cambiar tu avatar<br>• Equipar mascotas y temas de audio<br>• Personalizar tu experiencia',
    placement: 'left',
  },
  {
    target: '.audio-controls',
    header: {
      title: 'Controles de Audio 🎵',
    },
    content: 'Este botón en la esquina inferior izquierda te permite:<br>• Controlar el volumen de la música<br>• Ajustar efectos de sonido<br>• Silenciar todo si lo necesitas<br>¡Personaliza tu experiencia auditiva!',
    placement: 'top',
  },
  {
    target: '.pet-viewer',
    header: {
      title: 'Tu Mascota 🐾',
    },
    content: 'Esta es tu <strong>mascota virtual</strong>. Te acompañará en todas las páginas de la aplicación. Puedes comprar más mascotas en la tienda y cambiarlas desde tu perfil. ¡Colecciónalas todas!',
    placement: 'left',
  },
]);

const tourOptions = ref({
  useKeyboardNavigation: true,
  labels: {
    buttonSkip: 'Saltar tour',
    buttonPrevious: 'Anterior',
    buttonNext: 'Siguiente',
    buttonStop: '¡Entendido!',
  },
});

const tourCallbacks = ref({
  onStop: () => {
    // Marcar que el usuario ya vio el tour
    localStorage.setItem('dashboard_tour_completed', 'true');
  },
  onSkip: () => {
    localStorage.setItem('dashboard_tour_completed', 'true');
  },
});

onMounted(async () => {
  await loadUserData();
  
  // Iniciar el tour si es la primera vez
  setTimeout(() => {
    const tourCompleted = localStorage.getItem('dashboard_tour_completed');
    const justCompletedOnboarding = localStorage.getItem('just_completed_onboarding');
    
    if (justCompletedOnboarding === 'true' || !tourCompleted) {
      instance?.proxy?.$tours?.['dashboardTour']?.start?.();
      localStorage.removeItem('just_completed_onboarding');
    }
  }, 1500);
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
  overflow-y: auto;
  overflow-x: hidden;
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

/* Tour Styles */
:deep(.v-tour__target--highlighted) {
  box-shadow: 0 0 0 99999px rgba(0, 0, 0, 0.6) !important;
  z-index: 10000 !important;
}

:deep(.v-step) {
  background: white !important;
  border-radius: 12px !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25) !important;
  padding: 0 !important;
  max-width: 400px !important;
  z-index: 10001 !important;
}

:deep(.v-step__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  color: white !important;
  padding: 20px !important;
  border-radius: 12px 12px 0 0 !important;
  font-size: 18px !important;
  font-weight: 600 !important;
}

:deep(.v-step__content) {
  padding: 20px !important;
  color: #333 !important;
  font-size: 15px !important;
  line-height: 1.6 !important;
}

:deep(.v-step__content strong) {
  color: #667eea !important;
  font-weight: 600 !important;
}

:deep(.v-step__arrow) {
  border-color: white !important;
  z-index: 10002 !important;
}

:deep(.v-step__arrow::before) {
  border-color: white !important;
}

.tour-actions {
  display: flex;
  gap: 10px;
  padding: 15px 20px;
  border-top: 1px solid #e0e0e0;
  justify-content: flex-end;
  background: white;
  border-radius: 0 0 12px 12px;
}

.tour-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.tour-btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.tour-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.tour-btn-secondary {
  background: #f0f0f0;
  color: #666;
}

.tour-btn-secondary:hover {
  background: #e0e0e0;
}

.tour-btn-success {
  background: #28a745;
  color: white;
}

.tour-btn-success:hover {
  background: #218838;
  transform: translateY(-2px);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
