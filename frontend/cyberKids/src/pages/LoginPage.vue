<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { AuthService } from '../services/auth.service';
import type { LoginDto, ValidationErrors } from '../dto/auth.dto';

const router = useRouter();

const formData = ref<LoginDto>({
  email: '',
  password: '',
});

const errors = ref<ValidationErrors>({});
const isLoading = ref(false);
const successMessage = ref('');

const handleLogin = async () => {
  errors.value = {};
  successMessage.value = '';
  
  // Validación básica del lado del cliente
  let hasErrors = false;
  
  if (!formData.value.email.trim()) {
    errors.value.email = ['El correo electrónico es obligatorio'];
    hasErrors = true;
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.value.email)) {
    errors.value.email = ['Por favor ingresa un correo electrónico válido'];
    hasErrors = true;
  }
  
  if (!formData.value.password) {
    errors.value.password = ['La contraseña es obligatoria'];
    hasErrors = true;
  }
  
  if (hasErrors) {
    return;
  }
  
  isLoading.value = true;
  
  try {
    const response = await AuthService.login(formData.value);
    successMessage.value = '¡Inicio de sesión exitoso! Redirigiendo...';
    
    // Guardar el token si viene en la respuesta
    if (response.tokens?.access) {
      localStorage.setItem('access_token', response.tokens.access);
      localStorage.setItem('refresh_token', response.tokens.refresh);
    }
    
    setTimeout(() => {
      router.push('/'); // O redirigir al dashboard
    }, 2000);
  } catch (error: any) {
    if (error && typeof error === 'object') {
      // Traducir mensajes del backend si es necesario
      const translatedErrors: ValidationErrors = {};
      
      if (error.error) {
        translatedErrors.non_field_errors = [
          error.error === 'Credenciales inválidas' 
            ? 'Credenciales inválidas' 
            : 'Error de autenticación'
        ];
      }
      
      for (const [key, value] of Object.entries(error)) {
        if (Array.isArray(value)) {
          translatedErrors[key as keyof ValidationErrors] = value.map((msg: string) => {
            // Traducir mensajes comunes del backend
            if (msg.includes('This field is required') || msg.includes('required')) {
              return 'Este campo es obligatorio';
            }
            if (msg.includes('Invalid credentials') || msg.includes('invalid')) {
              return 'Credenciales inválidas';
            }
            return msg;
          });
        }
      }
      
      errors.value = translatedErrors;
    } else {
      errors.value = { non_field_errors: ['Error al iniciar sesión. Intenta de nuevo.'] };
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
  <div class="login-page">
    <div class="login-container">
      <button class="back-button" @click="goBack">
        ← Volver al Inicio
      </button>
      
      <div class="login-card">
        <h1 class="login-title">¡Bienvenido de Vuelta!</h1>
        <p class="login-subtitle">Inicia sesión en tu cuenta ninja</p>
        
        <form @submit.prevent="handleLogin" class="login-form" novalidate>
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
              placeholder="Ingresa tu contraseña"
            />
            <span v-if="errors.password" class="error-message">
              {{ errors.password[0] }}
            </span>
          </div>

          <!-- General Error Message -->
          <div v-if="errors.non_field_errors" class="general-error">
            {{ errors.non_field_errors[0] }}
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
            <span v-if="!isLoading">🔐 ¡Iniciar Sesión!</span>
            <span v-else>⏳ Iniciando sesión...</span>
          </button>
        </form>

        <div class="register-link">
          <p>¿No tienes una cuenta?</p>
          <router-link to="/register" class="link-button">
            Regístrate Aquí
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 50%, #ff8e53 100%);
  overflow: hidden;
}

.login-container {
  width: 100%;
  max-width: 650px;
  position: relative;
  max-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.back-button {
  background: rgba(255, 255, 255, 0.9);
  color: #ff6b6b;
  border: none;
  padding: 1rem 2rem;
  border-radius: 25px;
  font-size: 1.3rem;
  font-weight: bold;
  cursor: pointer;
  margin-bottom: 1rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
}

.back-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
  background: white;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 30px;
  padding: 2rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border: 5px solid #ff6b6b;
  backdrop-filter: blur(10px);
  overflow-y: auto;
  max-height: calc(100vh - 100px);
}

.login-title {
  font-size: 3.5rem;
  color: #ff6b6b;
  text-align: center;
  margin: 0 0 0.5rem 0;
  text-shadow: 2px 2px 4px rgba(255, 107, 107, 0.3);
}

.login-subtitle {
  font-size: 1.6rem;
  color: #666;
  text-align: center;
  margin: 0 0 2rem 0;
  font-weight: 600;
}

.login-form {
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
  font-size: 1.5rem;
  color: #2c3e50;
  font-weight: bold;
}

.form-input {
  padding: 1.2rem 1.5rem;
  border: 3px solid #e0e0e0;
  border-radius: 18px;
  font-size: 1.4rem;
  font-family: 'CyberKids', 'Comic Sans MS', Arial, sans-serif;
  transition: all 0.3s ease;
  background: white;
}

.form-input:focus {
  outline: none;
  border-color: #ff6b6b;
  box-shadow: 0 0 0 3px rgba(255, 107, 107, 0.2);
  transform: translateY(-2px);
}

.form-input.input-error {
  border-color: #ff6b6b;
  background: #fff5f5;
}

.error-message {
  color: #ff6b6b;
  font-size: 1.2rem;
  font-weight: bold;
  margin-top: 0.3rem;
  animation: shake 0.3s ease;
}

.general-error {
  background: linear-gradient(135deg, #ff6b6b, #ee5a6f);
  color: white;
  padding: 1.2rem;
  border-radius: 18px;
  text-align: center;
  font-size: 1.3rem;
  font-weight: bold;
  animation: shake 0.5s ease;
}

.success-message {
  background: linear-gradient(135deg, #00f5a0, #00d9f5);
  color: white;
  padding: 1.2rem;
  border-radius: 18px;
  text-align: center;
  font-size: 1.4rem;
  font-weight: bold;
  animation: slideIn 0.5s ease;
}

.submit-button {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  color: white;
  border: none;
  padding: 1.5rem 2rem;
  border-radius: 30px;
  font-size: 1.8rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  box-shadow: 0 10px 30px rgba(255, 107, 107, 0.4);
  margin-top: 0.5rem;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-5px) scale(1.05);
  box-shadow: 0 15px 40px rgba(255, 107, 107, 0.6);
}

.submit-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.register-link {
  text-align: center;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 2px solid #e0e0e0;
}

.register-link p {
  font-size: 1.4rem;
  color: #666;
  margin: 0 0 0.8rem 0;
}

.link-button {
  color: #667eea;
  font-size: 1.5rem;
  font-weight: bold;
  text-decoration: none;
  transition: all 0.3s ease;
}

.link-button:hover {
  color: #764ba2;
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
@media (max-height: 800px) {
  .login-title {
    font-size: 3rem;
  }
  
  .login-subtitle {
    font-size: 1.4rem;
    margin-bottom: 1.5rem;
  }
  
  .form-label {
    font-size: 1.3rem;
  }
  
  .form-input {
    font-size: 1.2rem;
    padding: 1rem 1.2rem;
  }
  
  .submit-button {
    font-size: 1.6rem;
    padding: 1.2rem 1.8rem;
  }
  
  .login-card {
    padding: 1.5rem;
  }
  
  .login-form {
    gap: 1.2rem;
  }
}

@media (max-width: 768px) {
  .login-title {
    font-size: 2.5rem;
  }
  
  .login-subtitle {
    font-size: 1.3rem;
  }
  
  .form-label {
    font-size: 1.2rem;
  }
  
  .form-input {
    font-size: 1.1rem;
    padding: 0.9rem 1.2rem;
  }
  
  .submit-button {
    font-size: 1.4rem;
    padding: 1.1rem 1.5rem;
  }
  
  .back-button {
    font-size: 1.1rem;
    padding: 0.8rem 1.5rem;
  }
}
</style>
