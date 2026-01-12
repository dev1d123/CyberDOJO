import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../pages/HomePage.vue';
import RegisterPage from '../pages/RegisterPage.vue';
import OnboardingPage from '../pages/OnboardingPage.vue';
import ResultsPage from '../pages/ResultsPage.vue';

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
    path: '/onboarding',
    name: 'Onboarding',
    component: OnboardingPage,
  },
  {
    path: '/results',
    name: 'Results',
    component: ResultsPage,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
