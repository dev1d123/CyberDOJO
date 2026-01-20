<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { AuthService } from '../services/auth.service';
import { API_CONFIG } from '../config/api.config';
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

const decodeJwtPayload = (token: string): any | null => {
  try {
    const payloadPart = token.split('.')[1];
    if (!payloadPart) return null;

    // base64url -> base64
    const base64 = payloadPart.replace(/-/g, '+').replace(/_/g, '/');
    const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), '=');
    return JSON.parse(atob(padded));
  } catch (e) {
    console.error('❌ Error decodificando JWT:', e);
    return null;
  }
};

const handleRegister = async () => {
  errors.value = {};
  successMessage.value = '';
  
  // Validación básica del lado del cliente
  let hasErrors = false;
  
  if (!formData.value.username.trim()) {
    errors.value.username = ['El nombre de usuario es obligatorio'];
    hasErrors = true;
  }
  
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
  } else if (formData.value.password.length < 6) {
    errors.value.password = ['La contraseña debe tener al menos 6 caracteres'];
    hasErrors = true;
  }
  
  if (!formData.value.password_confirm) {
    errors.value.password_confirm = ['Debes confirmar tu contraseña'];
    hasErrors = true;
  } else if (formData.value.password !== formData.value.password_confirm) {
    errors.value.password_confirm = ['Las contraseñas no coinciden'];
    hasErrors = true;
  }
  
  if (hasErrors) {
    return;
  }
  
  isLoading.value = true;
  
  try {
    const response = await AuthService.register(formData.value);
    console.log('✅ Register response (page):', response);
    
    // Guardar tokens
    if (response.tokens) {
      localStorage.setItem('access_token', response.tokens.access);
      localStorage.setItem('refresh_token', response.tokens.refresh);
    }
    
    // Guardar información del usuario
    if (response.user) {
      localStorage.setItem('user_id', response.user.user_id.toString());
    }

    // Fallback: si no viene user, intentar extraer user_id del access_token
    if (!localStorage.getItem('user_id') && response.tokens?.access) {
      const payload = decodeJwtPayload(response.tokens.access);
      const tokenUserId = payload?.user_id;
      if (tokenUserId) {
        localStorage.setItem('user_id', String(tokenUserId));
        console.log('🧩 user_id obtenido desde access_token:', tokenUserId);
      } else {
        console.warn('⚠️ No se pudo obtener user_id desde access_token');
      }
    }

    // Fallback extra: algunos backends retornan user_id al nivel raíz
    const rootUserId = (response as any)?.user_id;
    if (!localStorage.getItem('user_id') && rootUserId) {
      localStorage.setItem('user_id', String(rootUserId));
      console.log('🧩 user_id obtenido desde respuesta raíz:', rootUserId);
    }
    
    // Asignar mascota por defecto (gratis - costo 0)
    try {
      const accessToken = localStorage.getItem('access_token');
      console.log('🔑 Token disponible:', accessToken ? 'Sí' : 'No');
      if (accessToken) {
        const petResponse = await fetch(`${API_CONFIG.BASE_URL}/progression/shop/buy-pet/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`
          },
          body: JSON.stringify({ pet_id: 7 })
        });
        const petData = await petResponse.json();
        console.log('🐾 Respuesta del servidor:', petResponse.status, petData);
        if (petResponse.ok) {
          console.log('✅ Pet por defecto asignado correctamente');
        } else {
          console.error('❌ Error del servidor:', petData);
        }
      }
    } catch (petError) {
      console.error('❌ Error asignando pet por defecto:', petError);
    }
    
    successMessage.value = '¡Cuenta creada exitosamente! Redirigiendo...';
    
    setTimeout(() => {
      router.push('/profile-setup');
    }, 1500);
  } catch (error: any) {
    if (error && typeof error === 'object') {
      // Traducir mensajes del backend si es necesario
      const translatedErrors: ValidationErrors = {};

      const arrayFields = new Set<Exclude<keyof ValidationErrors, 'error'>>([
        'username',
        'email',
        'password',
        'password_confirm',
        'non_field_errors',
      ]);

      for (const [key, value] of Object.entries(error)) {
        if (key === 'error' && typeof value === 'string') {
          translatedErrors.non_field_errors = [value];
          continue;
        }

        if (Array.isArray(value) && arrayFields.has(key as Exclude<keyof ValidationErrors, 'error'>)) {
          (translatedErrors[key as Exclude<keyof ValidationErrors, 'error'>] as string[]) = value.map((msg: string) => {
            // Traducir mensajes comunes del backend
            if (msg.includes('This field is required') || msg.includes('required')) {
              return 'Este campo es obligatorio';
            }
            if (msg.includes('already exists') || msg.includes('already registered')) {
              return 'Este correo ya está registrado';
            }
            if (msg.includes('password') && msg.includes('match')) {
              return 'Las contraseñas no coinciden';
            }
            return msg;
          });
        }
      }
      errors.value = translatedErrors;
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
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  overflow: hidden;
}

.register-container {
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
  color: #667eea;
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

.register-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 30px;
  padding: 2rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border: 5px solid #667eea;
  backdrop-filter: blur(10px);
  overflow-y: auto;
  max-height: calc(100vh - 100px);
}

.register-title {
  font-size: 3.5rem;
  color: #667eea;
  text-align: center;
  margin: 0 0 0.5rem 0;
  text-shadow: 2px 2px 4px rgba(102, 126, 234, 0.3);
}

.register-subtitle {
  font-size: 1.6rem;
  color: #666;
  text-align: center;
  margin: 0 0 1.5rem 0;
  font-weight: 600;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
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
  font-size: 1.2rem;
  font-weight: bold;
  margin-top: 0.3rem;
  animation: shake 0.3s ease;
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
  background: linear-gradient(135deg, #48c6ef 0%, #6f86d6 100%);
  color: white;
  border: none;
  padding: 1.5rem 2rem;
  border-radius: 30px;
  font-size: 1.8rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  box-shadow: 0 10px 30px rgba(72, 198, 239, 0.4);
  margin-top: 0.5rem;
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
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 2px solid #e0e0e0;
}

.login-link p {
  font-size: 1.4rem;
  color: #666;
  margin: 0 0 0.8rem 0;
}

.link-button {
  color: #ff6b6b;
  font-size: 1.5rem;
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
@media (max-height: 800px) {
  .register-title {
    font-size: 3rem;
  }
  
  .register-subtitle {
    font-size: 1.4rem;
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
  
  .register-card {
    padding: 1.5rem;
  }
  
  .register-form {
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  .register-title {
    font-size: 2.5rem;
  }
  
  .register-subtitle {
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
