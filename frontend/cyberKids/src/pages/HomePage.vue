<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useRoute } from 'vue-router';
import AccountOpenAlert from '../components/AccountOpenAlert.vue';
import { AuthService } from '../services/auth.service';

const router = useRouter();
const route = useRoute();

const welcomeGif = new URL('../assets/gif/welcome.gif', import.meta.url).href;

type SessionState = 'checking' | 'active' | 'inactive';
const sessionState = ref<SessionState>('checking');

const isAuthenticated = computed(() => sessionState.value === 'active');

const sessionAlertOpen = ref(false);
const pendingTarget = ref<'login' | 'register' | null>(null);

const openSessionAlert = (target: 'login' | 'register' | null) => {
  pendingTarget.value = target;
  sessionAlertOpen.value = true;
};

const clearSession = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user_id');
};

const checkActiveSession = async () => {
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) {
    sessionState.value = 'inactive';
    return;
  }

  try {
    const res = await AuthService.refresh(refreshToken);
    const access = res?.tokens?.access;
    const refresh = res?.tokens?.refresh;

    if (!access || !refresh) {
      clearSession();
      sessionState.value = 'inactive';
      return;
    }

    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    sessionState.value = 'active';
  } catch {
    clearSession();
    sessionState.value = 'inactive';
  }
};

const consumeQueryAlert = () => {
  // Si el router guard redirige con query, mostramos la alerta aquí.
  const wantsAlert = route.query?.sessionOpen === '1';
  const target = route.query?.target;

  if (wantsAlert && isAuthenticated.value) {
    if (target === 'login' || target === 'register') {
      openSessionAlert(target);
    } else {
      openSessionAlert(null);
    }
  }
};

onMounted(async () => {
  await checkActiveSession();
  consumeQueryAlert();
});

watch(
  [() => route.query, () => isAuthenticated.value],
  () => {
    consumeQueryAlert();
  }
);

const closeSessionAlert = () => {
  sessionAlertOpen.value = false;
  pendingTarget.value = null;
  // Limpia el query para evitar re-abrir el modal al refrescar.
  if (route.query?.sessionOpen || route.query?.target) {
    router.replace({ path: '/', query: {} });
  }
};

const confirmCloseSession = () => {
  clearSession();

  const target = pendingTarget.value;
  closeSessionAlert();

  // Si venía de un intento de login/register, ahora sí lo llevamos.
  if (target === 'login') router.push('/login');
  if (target === 'register') router.push('/register');
};

const goToDashboard = () => {
  router.push('/dashboard');
};

const goToRegister = () => {
  if (sessionState.value === 'checking') {
    checkActiveSession().finally(() => {
      if (isAuthenticated.value) {
        openSessionAlert('register');
        return;
      }
      router.push('/register');
    });
    return;
  }

  if (isAuthenticated.value) {
    openSessionAlert('register');
    return;
  }

  router.push('/register');
};

const goToLogin = () => {
  if (sessionState.value === 'checking') {
    checkActiveSession().finally(() => {
      if (isAuthenticated.value) {
        openSessionAlert('login');
        return;
      }
      router.push('/login');
    });
    return;
  }

  if (isAuthenticated.value) {
    openSessionAlert('login');
    return;
  }

  router.push('/login');
};
</script>

<template>
  <div class="home-page">
    <AccountOpenAlert
      v-model="sessionAlertOpen"
      message="Todavia hay una cuenta abierta. Cierra sesion para continuar."
      confirm-text="Cerrar sesión"
      cancel-text="Cancelar"
      @confirm="confirmCloseSession"
      @cancel="closeSessionAlert"
    />

    <button
      v-if="isAuthenticated"
      class="floating-dashboard-btn"
      type="button"
      aria-label="Ir al dashboard"
      @click="goToDashboard"
    >
      <span class="floating-icon" aria-hidden="true">🚀</span>
      Dashboard
    </button>

    <div class="content-container">
      <!-- Hero Section with GIF -->
      <div class="hero-container">
        <h1 class="hero-title">¡Bienvenido a CyberDojo!</h1>
        <div class="welcome-gif-container">
          <img :src="welcomeGif" alt="Welcome" class="welcome-gif" />
        </div>
      </div>

      <!-- Mission Box -->
      <div class="mission-box">
        <p class="mission-text">
          La internet cambia cada día, Entrena para ser el <span class="highlight">Guardián</span> de tus datos y privacidad
        </p>
        <p class="mission-text action-text">
          <span class="animated-word practice">Practica</span>, 
          <span class="animated-word interact">Interactúa</span>, 
          <span class="animated-word play">JUEGA</span> 
          y detecta situaciones peligrosas
        </p>
      </div>

      <!-- Actions Row -->
      <div class="actions-row">
        <div class="action-card">
          <button class="cta-button primary action-button" @click="goToRegister">
            <span class="button-icon">👤</span>
            ¡Crea una cuenta!
          </button>
        </div>

        <div class="action-card">
          <button class="cta-button secondary action-button" @click="goToLogin">
            <span class="button-icon">🔐</span>
            Inicia Sesión
          </button>
        </div>

        <div class="help-box action-card">
          <span class="lightbulb-icon">💡</span>
          <p class="help-text">
            Pide ayuda a tus padres si tienes complicaciones
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(1rem, 2.5vw, 2rem);
  padding-top: clamp(1rem, 4vh, 2.5rem);
  padding-bottom: clamp(1rem, 3vh, 3rem);
  overflow: hidden;
  box-sizing: border-box;
}

.floating-dashboard-btn {
  position: fixed;
  right: 2rem;
  bottom: 2rem;
  z-index: 1200;
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  padding: 1rem 1.4rem;
  border-radius: 999px;
  border: 4px solid rgba(255, 255, 255, 0.6);
  color: white;
  font-size: 1.25rem;
  font-weight: bold;
  background: linear-gradient(135deg, #48c6ef 0%, #6f86d6 100%);
  box-shadow: 0 18px 45px rgba(72, 198, 239, 0.55);
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.floating-dashboard-btn:hover {
  transform: translateY(-6px) scale(1.06);
  box-shadow: 0 22px 60px rgba(72, 198, 239, 0.7);
  background: linear-gradient(135deg, #6f86d6 0%, #48c6ef 100%);
}

.floating-icon {
  font-size: 1.5rem;
}

.content-container {
  display: flex;
  flex-direction: column;
  gap: clamp(1.25rem, 2.5vw, 2rem);
  max-width: 1400px;
  width: 100%;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  text-align: center;
}

/* Hero Container with GIF */
.hero-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(1rem, 3vw, 2rem);
  flex-wrap: wrap;
  width: 100%;
}

/* Hero Title */
.hero-title {
  font-size: clamp(2rem, 5vw, 5rem);
  color: #fff;
  text-shadow: 
    4px 4px 0px #ff6b6b,
    8px 8px 0px rgba(0, 0, 0, 0.3);
  margin: 0;
  animation: heroFloat 3s ease-in-out infinite;
  line-height: 1.2;
  text-align: center;
}

/* Mission Box */
.mission-box {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 30px;
  padding: clamp(1.2rem, 2vw, 2.5rem);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border: 5px solid #ff6b6b;
  backdrop-filter: blur(10px);
  transform: translateZ(0);
  transition: all 0.4s ease;
  width: 100%;
  max-width: 1100px;
  box-sizing: border-box;
}

.mission-text {
  font-size: clamp(1.05rem, 2.2vw, 1.8rem);
  line-height: 1.6;
  color: #2c3e50;
  margin: 0 0 0.25rem 0;
  text-align: center;
}

.highlight {
  color: #ff6b6b;
  font-weight: bold;
  font-size: 1.15em;
  text-shadow: 2px 2px 4px rgba(255, 107, 107, 0.3);
}

.action-text {
  font-size: clamp(1rem, 2vw, 1.6rem);
  margin-top: 0.25rem;
  font-weight: 600;
}

.animated-word {
  font-weight: bold;
  display: inline-block;
  margin: 0 0.3rem;
  transition: all 0.3s ease;
}

/* Actions Row */
.actions-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(220px, 1fr));
  align-items: start;
  justify-content: center;
  gap: clamp(1.2rem, 3vw, 3rem);
  width: 100%;
  max-width: 1100px;
}

.action-card {
  width: 100%;
  min-height: auto;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cta-button {
  color: white;
  border: none;
  padding: clamp(0.65rem, 1.8vw, 1.1rem) clamp(1.25rem, 3.2vw, 2.4rem);
  border-radius: 50px;
  font-size: clamp(1.05rem, 2.2vw, 1.6rem);
  font-weight: bold;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  display: inline-flex;
  align-items: center;
  gap: 1rem;
  border: 4px solid rgba(255, 255, 255, 0.5);
  white-space: nowrap;
}

.action-button {
  width: 100%;
  height: auto;
  min-height: 0;
  justify-content: center;
  border-radius: 24px;
}

.cta-button.primary {
  background: linear-gradient(135deg, #48c6ef 0%, #6f86d6 100%);
  box-shadow: 0 15px 40px rgba(72, 198, 239, 0.5);
}

.cta-button.primary:hover {
  transform: translateY(-8px) scale(1.08);
  box-shadow: 0 20px 50px rgba(72, 198, 239, 0.7);
  background: linear-gradient(135deg, #6f86d6 0%, #48c6ef 100%);
}

.cta-button.secondary {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  box-shadow: 0 15px 40px rgba(255, 107, 107, 0.5);
}

.cta-button.secondary:hover {
  transform: translateY(-8px) scale(1.08);
  box-shadow: 0 20px 50px rgba(255, 107, 107, 0.7);
  background: linear-gradient(135deg, #ee5a6f 0%, #ff6b6b 100%);
}

.button-icon {
  font-size: clamp(1.4rem, 3vw, 2rem);
  animation: iconSpin 2s infinite;
}

/* Welcome GIF */
.welcome-gif-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: clamp(1rem, 2.5vw, 2rem);
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
  border: 5px solid #fdcb6e;
  transition: all 0.3s ease;
  flex: 1;
  min-width: 260px;
  box-sizing: border-box;
}

.welcome-gif {
  width: min(420px, 100%);
  height: auto;
  display: block;
}

.help-box {
  background: rgba(254, 202, 87, 0.95);
  border-radius: 25px;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
  border: 5px solid #fdcb6e;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-sizing: border-box;
}

.help-box:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
}

.lightbulb-icon {
  font-size: 1.5rem;
  animation: glow 2s infinite;
  flex-shrink: 0;
}

.help-text {
  font-size: clamp(0.5rem, 1.5vw, 1.5rem);
  color: #2c3e50;
  font-weight: bold;
  margin: 0;
  text-align: center;
}

/* Animations */
@keyframes heroFloat {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-15px) rotate(-2deg);
  }
}

@keyframes gifFloat {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.15);
  }
}

@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-15px);
  }
}

@keyframes wiggle {
  0%, 100% {
    transform: rotate(0deg) scale(1);
  }
  25% {
    transform: rotate(-8deg) scale(1.15);
  }
  75% {
    transform: rotate(8deg) scale(1.15);
  }
}

@keyframes glow {
  0%, 100% {
    filter: brightness(1) drop-shadow(0 0 5px rgba(254, 202, 87, 0.5));
    transform: scale(1);
  }
  50% {
    filter: brightness(1.4) drop-shadow(0 0 15px rgba(254, 202, 87, 0.8));
    transform: scale(1.15);
  }
}

@keyframes iconSpin {
  0%, 100% {
    transform: rotate(0deg);
  }
  25% {
    transform: rotate(-10deg);
  }
  75% {
    transform: rotate(10deg);
  }
}

/* Responsive Design */
@media (max-width: 1024px) {
  .hero-title {
    font-size: 3.5rem;
  }
  
  .mission-text {
    font-size: 1.5rem;
  }
  
  .action-text {
    font-size: 1.3rem;
  }
  
  .cta-button {
    font-size: 1.5rem;
    padding: 0.95rem 2.1rem;
  }
  
  .welcome-gif {
    max-height: 180px;
  }
  
  .actions-row {
    gap: 2rem;
  }
}

@media (max-width: 900px) {
  .actions-row {
    grid-template-columns: repeat(2, minmax(220px, 1fr));
    gap: 1.5rem;
  }
}

@media (max-width: 768px) {
  .home-page {
    padding-top: clamp(1rem, 5vh, 3rem);
  }

  .hero-container {
    flex-direction: column;
    gap: 1rem;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .welcome-gif {
    max-height: 150px;
  }
  
  .mission-box {
    padding: 1.5rem;
  }
  
  .mission-text {
    font-size: 1.2rem;
  }
  
  .action-text {
    font-size: 1.1rem;
  }
  
  .actions-row {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .cta-button {
    font-size: 1.2rem;
    padding: 0.85rem 1.7rem;
    width: 100%;
    justify-content: center;
  }
  
  .help-text {
    font-size: 1.2rem;
  }

  .help-box {
    width: 100%;
    justify-content: center;
  }

  .floating-dashboard-btn {
    right: 1rem;
    bottom: 1rem;
    font-size: 1.1rem;
    padding: 0.9rem 1.2rem;
  }
}

@media (max-width: 640px) {
  .hero-title {
    text-shadow:
      2px 2px 0px #ff6b6b,
      4px 4px 0px rgba(0, 0, 0, 0.25);
  }
}

@media (max-width: 480px) {
  .floating-dashboard-btn {
    right: 0.75rem;
    bottom: 0.75rem;
    font-size: 1rem;
    padding: 0.8rem 1rem;
  }

  .help-box {
    flex-direction: column;
    text-align: center;
    gap: 0.6rem;
  }

  .lightbulb-icon {
    font-size: 2.6rem;
  }
}
</style>
