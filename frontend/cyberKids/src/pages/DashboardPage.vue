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
          class="menu-card fx-history"
          data-fx="history"
          data-tour-step="history"
          v-pet-hint="{ behavior: 'hover_module', vars: { target: 'Modo Historia' }, click: { behavior: 'open_page', vars: { target: 'Modo Historia' }, ttlMs: 1600, priority: 1 } }"
          @click="goToStoryMode"
        >
          <div class="card-gif-container">
            <img :src="historyGif" alt="Modo Historia" class="card-gif" />
          </div>
          <h2 class="card-title">Modo Historia</h2>
          <p class="card-description">Vive aventuras y aprende</p>
        </div>

        <!-- Desafíos -->
        <div
          class="menu-card fx-challenges"
          data-fx="challenges"
          data-tour-step="challenges"
          v-pet-hint="{ behavior: 'hover_module', vars: { target: 'Desafíos' }, click: { behavior: 'open_page', vars: { target: 'Desafíos' }, ttlMs: 1600, priority: 1 } }"
          @click="goToChallenges"
        >
          <div class="card-gif-container">
            <img :src="challengeGif" alt="Desafíos" class="card-gif" />
          </div>
          <h2 class="card-title">Desafíos</h2>
          <p class="card-description">Pon a prueba tus habilidades</p>
        </div>

        <!-- Tienda -->
        <div
          class="menu-card fx-shop"
          data-fx="shop"
          data-tour-step="shop"
          v-pet-hint="{ behavior: 'hover_module', vars: { target: 'Tienda' }, click: { behavior: 'open_page', vars: { target: 'Tienda' }, ttlMs: 1600, priority: 1 } }"
          @click="goToShop"
        >
          <div class="card-gif-container">
            <img :src="shopGif" alt="Tienda" class="card-gif" />
          </div>
          <h2 class="card-title">Tienda</h2>
          <p class="card-description">Compra accesorios geniales</p>
        </div>

        <!-- Perfil -->
        <div
          class="menu-card fx-profile"
          data-fx="profile"
          data-tour-step="profile"
          v-pet-hint="{ behavior: 'hover_module', vars: { target: 'Perfil' }, click: { behavior: 'open_page', vars: { target: 'Perfil' }, ttlMs: 1600, priority: 1 } }"
          @click="goToProfile"
        >
          <div class="card-gif-container">
            <img :src="settingGif" alt="Perfil" class="card-gif" />
          </div>
          <h2 class="card-title">Perfil</h2>
          <p class="card-description">Personaliza tu cuenta</p>
        </div>
      </div>

      <!-- Botón de Logros flotante -->
      <button
        class="achievements-floating-btn"
        data-tour-step="achievements"
        v-pet-hint="{ behavior: 'hover_module', vars: { target: 'Logros' }, click: { behavior: 'open_page', vars: { target: 'Logros' }, ttlMs: 1600, priority: 1 } }"
        @click="goToAchievements"
      >
        <span class="achievements-btn-icon">🏆</span>
        <span class="achievements-btn-text">Logros</span>
      </button>

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
import { ref, onMounted, onUnmounted, nextTick, watch, getCurrentInstance } from 'vue';
import { useRouter } from 'vue-router';
import type { UserDto } from '../dto/user.dto';
import { UserService } from '../services/user.service';
import { AudioService } from '../services/audio.service';
import DebugMenu from '../components/DebugMenu.vue';
import VanillaTilt from 'vanilla-tilt';

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

const historyGif = new URL('../assets/gif/historyGif.gif', import.meta.url).href;
const challengeGif = new URL('../assets/gif/challengeGif.gif', import.meta.url).href;
const shopGif = new URL('../assets/gif/shopGif.gif', import.meta.url).href;
const settingGif = new URL('../assets/gif/settingGif.gif', import.meta.url).href;

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
    target: '[data-tour-step="achievements"]',
    header: {
      title: 'Logros 🏆',
    },
    content: 'En <strong>Logros</strong> puedes ver todas tus hazañas y recompensas:<br>• Desbloquea logros completando actividades<br>• Reclama CyberCredits y XP por tus logros<br>• ¡Compite por conseguirlos todos!',
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

const goToAchievements = () => {
  router.push('/achievements');
};

const handleLogout = () => {
  AudioService.cleanup();
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user_id');
  router.push('/');
};

let tiltEls: HTMLElement[] = [];

function destroyTilt() {
  tiltEls.forEach((el) => {
    (el as any)?.vanillaTilt?.destroy?.();
  });
  tiltEls = [];
}

async function initTilt() {
  destroyTilt();
  await nextTick();

  const els = Array.from(document.querySelectorAll<HTMLElement>('.dashboard-page .menu-card'));
  tiltEls = els;

  els.forEach((el) => {
    const fx = el.dataset.fx ?? 'default';

    const base: any = {
      speed: 700,
      glare: true,
      'max-glare': 0.28,
      gyroscope: true,
      perspective: 900,
      scale: 1.02,
    };

    const perFx: Record<string, any> = {
      history: { max: 10, easing: 'cubic-bezier(.2,.9,.2,1)' },
      challenges: { max: 14, glare: true, 'max-glare': 0.34 },
      shop: { max: 9, glare: true, 'max-glare': 0.26, perspective: 1100 },
      profile: { max: 12, glare: true, 'max-glare': 0.3, perspective: 1000 },
      default: { max: 10 },
    };

    (VanillaTilt as any).init(el, { ...base, ...(perFx[fx] ?? perFx.default) });
  });
}

watch(
  () => ({ loading: loading.value, error: error.value }),
  async ({ loading: isLoading, error: err }) => {
    if (!isLoading && !err) {
      await initTilt();
    } else {
      destroyTilt();
    }
  }
);

onUnmounted(() => {
  destroyTilt();
});
</script>

<style scoped>
.dashboard-page {
  height: 100vh;
  width: 100vw;
  box-sizing: border-box;
  position: relative;
  isolation: isolate;
  background:
    radial-gradient(60vw 55vh at 15% 10%, rgba(0, 245, 255, 0.18) 0%, transparent 60%),
    radial-gradient(55vw 50vh at 85% 15%, rgba(255, 215, 0, 0.16) 0%, transparent 62%),
    radial-gradient(60vw 55vh at 45% 95%, rgba(255, 107, 107, 0.15) 0%, transparent 65%),
    linear-gradient(135deg, #060b18 0%, #101a3a 45%, #240b3a 100%);
  padding: clamp(12px, 2.5vh, 24px);
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  justify-content: center;
}

.dashboard-page::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  opacity: 0.45;
  background:
    repeating-linear-gradient(
      90deg,
      rgba(255, 255, 255, 0.06) 0px,
      rgba(255, 255, 255, 0.06) 1px,
      transparent 1px,
      transparent 72px
    ),
    repeating-linear-gradient(
      0deg,
      rgba(255, 255, 255, 0.045) 0px,
      rgba(255, 255, 255, 0.045) 1px,
      transparent 1px,
      transparent 72px
    );
  transform: translate3d(0, 0, 0);
  animation: gridDrift 18s linear infinite;
  mask-image: radial-gradient(circle at 50% 18%, black 0%, black 55%, transparent 75%);
}

.dashboard-page::after {
  content: '';
  position: fixed;
  inset: -20vh -10vw;
  pointer-events: none;
  z-index: 0;
  background:
    radial-gradient(closest-side at 30% 35%, rgba(0, 245, 255, 0.22), transparent 60%),
    radial-gradient(closest-side at 70% 30%, rgba(255, 215, 0, 0.18), transparent 62%),
    radial-gradient(closest-side at 55% 70%, rgba(155, 89, 255, 0.18), transparent 65%);
  filter: blur(18px) saturate(1.25);
  opacity: 0.85;
  animation: auroraFloat 14s ease-in-out infinite;
}

@keyframes gridDrift {
  0% { transform: translate3d(0, 0, 0); }
  50% { transform: translate3d(-36px, 24px, 0); }
  100% { transform: translate3d(0, 0, 0); }
}

@keyframes auroraFloat {
  0% { transform: translate3d(0, 0, 0) rotate(0deg); }
  50% { transform: translate3d(2vw, -2vh, 0) rotate(6deg); }
  100% { transform: translate3d(0, 0, 0) rotate(0deg); }
}

@media (prefers-reduced-motion: reduce) {
  .dashboard-page::before,
  .dashboard-page::after {
    animation: none;
  }
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
  position: relative;
  z-index: 1;
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
  background: rgba(255, 255, 255, 0.92);
  padding: clamp(8px, 1.4vh, 12px) clamp(12px, 2.2vh, 18px);
  border-radius: 50px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.45);
  backdrop-filter: blur(10px);
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
  --accent: #ffd700;
  --accent2: #00f5ff;
  --accent-rgb: 255, 215, 0;
  --accent2-rgb: 0, 245, 255;

  background: rgba(255, 255, 255, 0.88);
  border-radius: 22px;
  padding: clamp(12px, 2vh, 18px);
  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.28);
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  border: 4px solid rgba(255, 255, 255, 0.18);
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: clamp(8px, 1.3vh, 12px);
  min-height: 0;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(14px);
  transform-style: preserve-3d;
}

.menu-card::before {
  content: '';
  position: absolute;
  inset: -40% -60%;
  background:
    linear-gradient(
      115deg,
      transparent 0%,
      rgba(var(--accent2-rgb), 0.0) 28%,
      rgba(var(--accent2-rgb), 0.18) 45%,
      rgba(255, 255, 255, 0.2) 52%,
      rgba(var(--accent-rgb), 0.18) 60%,
      transparent 75%
    );
  transform: translate3d(-20%, 0, 0) rotate(18deg);
  opacity: 0;
  transition: opacity 250ms ease, transform 520ms cubic-bezier(0.2, 0.9, 0.2, 1.1);
  pointer-events: none;
}

.menu-card::after {
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: 24px;
  border: 2px solid rgba(var(--accent-rgb), 0.0);
  box-shadow:
    0 0 0 0 rgba(var(--accent-rgb), 0.0),
    0 0 0 0 rgba(var(--accent2-rgb), 0.0),
    0 20px 60px rgba(0, 0, 0, 0.15);
  opacity: 0;
  transform: scale(0.985);
  transition: opacity 220ms ease, transform 240ms ease, border-color 220ms ease, box-shadow 260ms ease;
  pointer-events: none;
}

.menu-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 18px 52px rgba(0, 0, 0, 0.35);
  border-color: rgba(var(--accent-rgb), 0.95);
}

.menu-card:hover::before {
  opacity: 1;
  transform: translate3d(14%, 0, 0) rotate(18deg);
}

.menu-card:hover::after {
  opacity: 1;
  transform: scale(1.02);
  border-color: rgba(var(--accent-rgb), 0.75);
  box-shadow:
    0 0 0 8px rgba(var(--accent-rgb), 0.12),
    0 0 38px rgba(var(--accent2-rgb), 0.22),
    0 18px 52px rgba(0, 0, 0, 0.22);
}

.card-gif-container {
  width: 100%;
  flex: 1 1 auto;
  min-height: clamp(80px, 16vh, 160px);
  margin-bottom: 0;
  border-radius: 15px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.04);
  position: relative;
}

.fx-history .card-gif-container::after {
  content: '';
  position: absolute;
  inset: 0;
  background:
    repeating-linear-gradient(
      0deg,
      rgba(0, 245, 255, 0.0) 0px,
      rgba(0, 245, 255, 0.0) 10px,
      rgba(0, 245, 255, 0.09) 11px,
      rgba(0, 245, 255, 0.0) 18px
    );
  opacity: 0;
  transform: translateY(-40%);
  transition: opacity 180ms ease;
  pointer-events: none;
}

.fx-history:hover .card-gif-container::after {
  opacity: 0.85;
  animation: scanLines 900ms linear infinite;
}

@keyframes scanLines {
  0% { transform: translateY(-45%); }
  100% { transform: translateY(45%); }
}

.card-gif {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-title {
  font-size: clamp(1.25rem, 2.2vw, 1.75rem);
  color: var(--accent);
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
  background: rgba(255, 255, 255, 0.18);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(10px);
  padding: clamp(10px, 1.8vh, 14px) clamp(16px, 3vh, 22px);
  border-radius: 14px;
}

.logout-button:hover {
  background: rgba(255, 255, 255, 0.26);
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.32);
}

/* Per-card accents (distinct hover vibes per button) */
.fx-history {
  --accent: #00f5ff;
  --accent2: #7c4dff;
  --accent-rgb: 0, 245, 255;
  --accent2-rgb: 124, 77, 255;
}

.fx-challenges {
  --accent: #ffd700;
  --accent2: #ff6b6b;
  --accent-rgb: 255, 215, 0;
  --accent2-rgb: 255, 107, 107;
}

.fx-shop {
  --accent: #2ecc71;
  --accent2: #00f5ff;
  --accent-rgb: 46, 204, 113;
  --accent2-rgb: 0, 245, 255;
}

.fx-profile {
  --accent: #9b59ff;
  --accent2: #ffd700;
  --accent-rgb: 155, 89, 255;
  --accent2-rgb: 255, 215, 0;
}

/* Botón flotante de Logros */
.achievements-floating-btn {
  position: fixed;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(12px);
  border: 2px solid rgba(255, 215, 0, 0.5);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 100;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
}

.achievements-floating-btn:hover {
  background: rgba(255, 215, 0, 0.25);
  border-color: rgba(255, 215, 0, 0.9);
  transform: translateY(-50%) scale(1.08);
  box-shadow: 0 8px 30px rgba(255, 215, 0, 0.35);
}

.achievements-btn-icon {
  font-size: 1.8rem;
  animation: trophyFloat 3s ease-in-out infinite;
}

.achievements-btn-text {
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.5px;
}

.achievements-floating-btn:hover .achievements-btn-icon {
  animation: trophyWiggle 0.5s ease-in-out;
}

@keyframes trophyFloat {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  25% { transform: translateY(-3px) rotate(-3deg); }
  75% { transform: translateY(-3px) rotate(3deg); }
}

@keyframes trophyWiggle {
  0%, 100% { transform: rotate(0deg) scale(1); }
  25% { transform: rotate(-10deg) scale(1.15); }
  75% { transform: rotate(10deg) scale(1.15); }
}

/* Responsive para el botón de logros */
@media (max-width: 768px) {
  .achievements-floating-btn {
    right: 10px;
    padding: 10px 12px;
  }
  
  .achievements-btn-icon {
    font-size: 1.5rem;
  }
  
  .achievements-btn-text {
    font-size: 0.65rem;
  }
}

/* Extra per-card "wow" behaviors */
.fx-challenges:hover::after {
  animation: borderPulse 1.05s ease-in-out infinite;
}

@keyframes borderPulse {
  0%, 100% {
    box-shadow:
      0 0 0 8px rgba(var(--accent-rgb), 0.12),
      0 0 34px rgba(var(--accent2-rgb), 0.18),
      0 18px 52px rgba(0, 0, 0, 0.22);
  }
  50% {
    box-shadow:
      0 0 0 10px rgba(var(--accent-rgb), 0.16),
      0 0 46px rgba(var(--accent2-rgb), 0.28),
      0 22px 62px rgba(0, 0, 0, 0.24);
  }
}

.fx-shop:hover::before {
  animation: shineSweep 1.35s ease-in-out infinite;
}

@keyframes shineSweep {
  0% { transform: translate3d(-10%, 0, 0) rotate(18deg); }
  50% { transform: translate3d(22%, 0, 0) rotate(18deg); }
  100% { transform: translate3d(-10%, 0, 0) rotate(18deg); }
}

.fx-profile:hover .card-title {
  text-shadow:
    0 0 0 rgba(0,0,0,0),
    0 0 18px rgba(var(--accent2-rgb), 0.22),
    0 0 26px rgba(var(--accent-rgb), 0.24);
}

.fx-profile:hover::before {
  filter: hue-rotate(18deg) saturate(1.15);
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
  font-size: 1.05rem !important;
  font-weight: 600 !important;
}

:deep(.v-step__content) {
  padding: 20px !important;
  color: #333 !important;
  font-size: 0.95rem !important;
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
  font-size: 0.9rem;
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
