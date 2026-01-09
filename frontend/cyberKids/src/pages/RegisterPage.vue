<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { AuthService } from '../services/auth.service';
import type { RegisterDto, ValidationErrors } from '../dto/auth.dto';

const router = useRouter();

const formData = ref<RegisterDto>({
  username: '',
  email: '',
  password: '',
  password_confirm: '',
});

const errors = ref<ValidationErrors>({});
const isLoading = ref(false);
const successMessage = ref('');

const handleRegister = async () => {
  errors.value = {};
  successMessage.value = '';
  
  // Validación básica del lado del cliente
  if (formData.value.password !== formData.value.password_confirm) {
    errors.value.password_confirm = ['Las contraseñas no coinciden'];
    return;
  }
  
  isLoading.value = true;
  
  try {
    const response = await AuthService.register(formData.value);
    successMessage.value = '¡Cuenta creada exitosamente! Redirigiendo...';
    
    setTimeout(() => {
      router.push('/login');
    }, 2000);
  } catch (error: any) {
    if (error && typeof error === 'object') {
      errors.value = error;
    } else {
      errors.value = { username: ['Error al registrar. Intenta de nuevo.'] };
    }
  } finally {
    isLoading.value = false;
  }
};

const goBack = () => {
  router.push('/');
};
</script>

<template>
  <div class="register-page">
    <div class="register-container">
      <button class="back-button" @click="goBack">
        ← Volver al Inicio
      </button>
      
      <div class="register-card">
        <h1 class="register-title">¡Únete a CyberDojo!</h1>
        <p class="register-subtitle">Crea tu cuenta de cyber ninja</p>
        
        <form @submit.prevent="handleRegister" class="register-form">
          <!-- Username Field -->
          <div class="form-group">
            <label for="username" class="form-label">
              👤 Nombre de Usuario
            </label>
            <input
              id="username"
              v-model="formData.username"
              type="text"
              class="form-input"
              :class="{ 'input-error': errors.username }"
              placeholder="Elige un nombre genial"
              required
            />
            <span v-if="errors.username" class="error-message">
              {{ errors.username[0] }}
            </span>
          </div>

          <!-- Email Field -->
          <div class="form-group">
            <label for="email" class="form-label">
              📧 Correo Electrónico
            </label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
              class="form-input"
              :class="{ 'input-error': errors.email }"
              placeholder="tu-email@ejemplo.com"
              required
            />
            <span v-if="errors.email" class="error-message">
              {{ errors.email[0] }}
            </span>
          </div>

          <!-- Password Field -->
          <div class="form-group">
            <label for="password" class="form-label">
              🔒 Contraseña
            </label>
            <input
              id="password"
              v-model="formData.password"
              type="password"
              class="form-input"
              :class="{ 'input-error': errors.password }"
              placeholder="Crea una contraseña segura"
              required
            />
            <span v-if="errors.password" class="error-message">
              {{ errors.password[0] }}
            </span>
          </div>

          <!-- Confirm Password Field -->
          <div class="form-group">
            <label for="password_confirm" class="form-label">
              🔐 Confirmar Contraseña
            </label>
            <input
              id="password_confirm"
              v-model="formData.password_confirm"
              type="password"
              class="form-input"
              :class="{ 'input-error': errors.password_confirm }"
              placeholder="Repite tu contraseña"
              required
            />
            <span v-if="errors.password_confirm" class="error-message">
              {{ errors.password_confirm[0] }}
            </span>
          </div>

          <!-- Success Message -->
          <div v-if="successMessage" class="success-message">
            {{ successMessage }}
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            class="submit-button"
            :disabled="isLoading"
          >
            <span v-if="!isLoading">🚀 ¡Crear Mi Cuenta!</span>
            <span v-else>⏳ Creando cuenta...</span>
          </button>
        </form>

        <div class="login-link">
          <p>¿Ya tienes una cuenta?</p>
          <router-link to="/login" class="link-button">
            Inicia Sesión Aquí
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
}

.register-container {
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

.register-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 30px;
  padding: 3rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border: 5px solid #667eea;
  backdrop-filter: blur(10px);
}

.register-title {
  font-size: 3rem;
  color: #667eea;
  text-align: center;
  margin: 0 0 0.5rem 0;
  text-shadow: 2px 2px 4px rgba(102, 126, 234, 0.3);
}

.register-subtitle {
  font-size: 1.4rem;
  color: #666;
  text-align: center;
  margin: 0 0 2rem 0;
  font-weight: 600;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 1.3rem;
  color: #2c3e50;
  font-weight: bold;
}

.form-input {
  padding: 1rem 1.5rem;
  border: 3px solid #e0e0e0;
  border-radius: 15px;
  font-size: 1.2rem;
  font-family: 'CyberKids', 'Comic Sans MS', Arial, sans-serif;
  transition: all 0.3s ease;
  background: white;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
  transform: translateY(-2px);
}

.form-input.input-error {
  border-color: #ff6b6b;
  background: #fff5f5;
}

.error-message {
  color: #ff6b6b;
  font-size: 1rem;
  font-weight: bold;
  margin-top: 0.3rem;
  animation: shake 0.3s ease;
}

.success-message {
  background: linear-gradient(135deg, #00f5a0, #00d9f5);
  color: white;
  padding: 1rem;
  border-radius: 15px;
  text-align: center;
  font-size: 1.2rem;
  font-weight: bold;
  animation: slideIn 0.5s ease;
}

.submit-button {
  background: linear-gradient(135deg, #48c6ef 0%, #6f86d6 100%);
  color: white;
  border: none;
  padding: 1.3rem 2rem;
  border-radius: 25px;
  font-size: 1.6rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  box-shadow: 0 10px 30px rgba(72, 198, 239, 0.4);
  margin-top: 1rem;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-5px) scale(1.05);
  box-shadow: 0 15px 40px rgba(72, 198, 239, 0.6);
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.login-link {
  text-align: center;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 2px solid #e0e0e0;
}

.login-link p {
  font-size: 1.2rem;
  color: #666;
  margin: 0 0 0.8rem 0;
}

.link-button {
  color: #ff6b6b;
  font-size: 1.3rem;
  font-weight: bold;
  text-decoration: none;
  transition: all 0.3s ease;
}

.link-button:hover {
  color: #ee5a6f;
  text-decoration: underline;
}

/* Animations */
@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .register-card {
    padding: 2rem;
  }
  
  .register-title {
    font-size: 2.5rem;
  }
  
  .register-subtitle {
    font-size: 1.2rem;
  }
  
  .form-label {
    font-size: 1.1rem;
  }
  
  .form-input {
    font-size: 1rem;
    padding: 0.8rem 1.2rem;
  }
  
  .submit-button {
    font-size: 1.3rem;
    padding: 1rem 1.5rem;
  }
}
</style>
