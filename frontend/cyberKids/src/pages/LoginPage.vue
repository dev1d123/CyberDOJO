<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

const goBack = () => {
  router.push('/');
};
</script>

<template>
  <div class="login-page">
    <div class="login-container">
      <button class="back-button" @click="goBack">
        ← Volver al Inicio
      </button>
      
      <div class="login-card">
        <h1 class="login-title">Próximamente...</h1>
        <p class="login-subtitle">La página de inicio de sesión estará disponible pronto</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
}

.login-container {
  width: 100%;
  max-width: 600px;
  position: relative;
}

.back-button {
  background: rgba(255, 255, 255, 0.9);
  color: #667eea;
  border: none;
  padding: 0.8rem 1.5rem;
  border-radius: 20px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  margin-bottom: 1.5rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.back-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
  background: white;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 30px;
  padding: 4rem 3rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border: 5px solid #ff6b6b;
  backdrop-filter: blur(10px);
  text-align: center;
}

.login-title {
  font-size: 3rem;
  color: #ff6b6b;
  margin: 0 0 1rem 0;
  text-shadow: 2px 2px 4px rgba(255, 107, 107, 0.3);
}

.login-subtitle {
  font-size: 1.4rem;
  color: #666;
  margin: 0;
  font-weight: 600;
}
</style>
