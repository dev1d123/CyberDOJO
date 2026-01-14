import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../pages/HomePage.vue';
import RegisterPage from '../pages/RegisterPage.vue';
import OnboardingPage from '../pages/OnboardingPage.vue';
import ResultsPage from '../pages/ResultsPage.vue';
import ProfileSetupPage from '../pages/ProfileSetupPage.vue';
import DashboardPage from '../pages/DashboardPage.vue';
import HistoryModePage from '../pages/HistoryModePage.vue';
import { UserService } from '../services/user.service';

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
  },
  {
    path: '/history',
    name: 'History',
    component: HistoryModePage,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation guard para manejar autenticación y flujo
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('access_token');
  const userId = localStorage.getItem('user_id');

  // Si la ruta requiere autenticación
  if (to.meta.requiresAuth && !token) {
    next('/login');
    return;
  }

  // Si está autenticado y trata de ir a login o register, redirigir al dashboard
  if ((to.name === 'Login' || to.name === 'Register') && token) {
    next('/dashboard');
    return;
  }

  // Verificar el estado del usuario cuando navega a rutas autenticadas
  if (to.meta.requiresAuth && token && userId) {
    try {
      const user = await UserService.getUserById(parseInt(userId));
      
      // Si no tiene país o username, necesita completar el perfil
      const needsProfileSetup = !user.country || !user.username || user.username.length < 3;
      
      // Verificar estado del onboarding
      const onboardingStatus = await UserService.checkOnboardingStatus(parseInt(userId));
      
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
