import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../pages/HomePage.vue';
import RegisterPage from '../pages/RegisterPage.vue';
import OnboardingPage from '../pages/OnboardingPage.vue';
import ResultsPage from '../pages/ResultsPage.vue';
import ProfileSetupPage from '../pages/ProfileSetupPage.vue';
import DashboardPage from '../pages/DashboardPage.vue';
import HistoryModePage from '../pages/HistoryModePage.vue';
import SimulationPage from '../pages/SimulationPage.vue';
import { UserService } from '../services/user.service';
import ShopPage from '../pages/ShopPage.vue';
import ProfilePage from '../pages/ProfilePage.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterPage,
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../pages/LoginPage.vue'),
  },
  {
    path: '/profile-setup',
    name: 'ProfileSetup',
    component: ProfileSetupPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/onboarding',
    name: 'Onboarding',
    component: OnboardingPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/results',
    name: 'Results',
    component: ResultsPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/challenges',
    name: 'Challenges',
    component: () => import('../pages/ChallengesPage.vue'),
  },
  {
    path: '/history',
    name: 'History',
    component: HistoryModePage,
  },
  {
    path: '/simulation/:scenarioId',
    name: 'Simulation',
    component: SimulationPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/shop',
    name: 'Shop',
    component: ShopPage,
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfilePage,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation guard para manejar autenticación y flujo
router.beforeEach(async (to, _from, next) => {
  const token = localStorage.getItem('access_token');

  // Si la ruta requiere autenticación
  if (to.meta.requiresAuth && !token) {
    next('/login');
    return;
  }

  // Si está autenticado y trata de ir a login o register, redirigir al dashboard
  if ((to.name === 'Login' || to.name === 'Register') && token) {
    // En vez de redirigir silenciosamente, mostramos una alerta bloqueante en Home.
    // Home lee el query y muestra el modal.
    const target = to.name === 'Login' ? 'login' : 'register';
    next({ path: '/', query: { sessionOpen: '1', target } });
    return;
  }

  // Verificar el estado del usuario cuando navega a rutas autenticadas
  if (to.meta.requiresAuth && token) {
    try {
      const user = await UserService.getCurrentUser();
      if (user?.user_id) {
        localStorage.setItem('user_id', String(user.user_id));
      }
      
      // Si no tiene país o username, necesita completar el perfil
      const needsProfileSetup = !user.country || !user.username || user.username.length < 3;
      
      // Verificar estado del onboarding
      const onboardingStatus = user?.user_id
        ? await UserService.checkOnboardingStatus(user.user_id)
        : { completed: false, has_responses: false };
      
      // Flujo de navegación:
      // 1. Si necesita setup de perfil y no está yendo ahí, redirigir
      if (needsProfileSetup && to.name !== 'ProfileSetup') {
        next('/profile-setup');
        return;
      }
      
      // 2. Si no necesita setup pero no ha completado onboarding y no está yendo ahí, redirigir
      if (!needsProfileSetup && !onboardingStatus.completed && to.name !== 'Onboarding' && to.name !== 'Results') {
        next('/onboarding');
        return;
      }
      
      // 3. Si está en onboarding pero ya lo completó, ir al dashboard
      if (onboardingStatus.completed && (to.name === 'Onboarding' || to.name === 'ProfileSetup')) {
        next('/dashboard');
        return;
      }
    } catch (error) {
      console.error('Error checking user status:', error);
      // En caso de error, dejar continuar
    }
  }

  next();
});

export default router;
