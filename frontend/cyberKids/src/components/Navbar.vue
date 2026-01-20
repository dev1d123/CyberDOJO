<script setup lang="ts">
import { ref } from 'vue';

const showTooltip = ref<string | null>(null);

const showTooltipHandler = (tooltip: string) => {
  showTooltip.value = tooltip;
};

const hideTooltipHandler = () => {
  showTooltip.value = null;
};
</script>

<template>
  <nav class="navbar">
    <div class="navbar-content">
      <div class="logo-container">
        <img
          v-pet-hint="{ behavior: 'hover', vars: { target: 'el logo de CyberDojo' } }"
          src="/src/assets/gif/logo.gif"
          alt="CyberDojo Logo"
          class="logo-img"
        />
      </div>
      
      <div class="nav-buttons">
        <button 
          class="nav-btn"
          v-pet-hint="{ behavior: 'hover_button', vars: { target: 'ver preguntas frecuentes' } }"
          @mouseenter="showTooltipHandler('faq')"
          @mouseleave="hideTooltipHandler"
        >
          FAQ
          <span v-if="showTooltip === 'faq'" class="tooltip">
            Preguntas frecuentes sobre CyberDojo
          </span>
        </button>
        
        <button 
          class="nav-btn"
          v-pet-hint="{ behavior: 'hover_button', vars: { target: 'conocer el proyecto' } }"
          @mouseenter="showTooltipHandler('about')"
          @mouseleave="hideTooltipHandler"
        >
          Sobre Nosotros
          <span v-if="showTooltip === 'about'" class="tooltip">
            Conoce más sobre nuestro proyecto
          </span>
        </button>
        
        <button 
          class="nav-btn"
          v-pet-hint="{ behavior: 'hover_button', vars: { target: 'apoyar el proyecto' } }"
          @mouseenter="showTooltipHandler('support')"
          @mouseleave="hideTooltipHandler"
        >
          Apóyanos
          <span v-if="showTooltip === 'support'" class="tooltip">
            Ayúdanos a crecer y mejorar
          </span>
        </button>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  background-color: rgba(0, 0, 0, 0.95);
  padding: 0.8rem 2rem;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
  flex-shrink: 0;
}

.navbar-content {
  max-width: 1600px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.logo-container {
  display: flex;
  align-items: center;
}

.logo-img {
  height: 80px;
  width: auto;
  border-radius: 15px;
  filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.3));
  transition: all 0.3s ease;
}

.logo-img:hover {
  transform: scale(1.1) rotate(5deg);
  filter: drop-shadow(0 0 20px rgba(255, 107, 107, 0.6));
}

.nav-buttons {
  display: flex;
  gap: 1rem;
}

.nav-btn {
  background: linear-gradient(135deg, #ff6b6b, #ff8e53);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 25px;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  position: relative;
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  box-shadow: 0 6px 15px rgba(255, 107, 107, 0.4);
}

.nav-btn:hover {
  transform: translateY(-5px) scale(1.08);
  box-shadow: 0 10px 25px rgba(255, 107, 107, 0.6);
  background: linear-gradient(135deg, #ff8e53, #ff6b6b);
}

.tooltip {
  position: absolute;
  top: 110%;
  left: 50%;
  transform: translateX(-50%);
  background-color: rgba(0, 0, 0, 0.95);
  color: white;
  padding: 0.8rem 1.2rem;
  border-radius: 12px;
  font-size: 1rem;
  white-space: nowrap;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.5);
  z-index: 1001;
  animation: tooltipFadeIn 0.3s ease;
  border: 2px solid #ff6b6b;
}

.tooltip::before {
  content: '';
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 8px solid transparent;
  border-bottom-color: #ff6b6b;
}

@keyframes tooltipFadeIn {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

@media (max-width: 768px) {
  .navbar {
    padding: 0.6rem 1rem;
  }
  
  .logo-img {
    height: 60px;
  }
  
  .nav-btn {
    font-size: 1rem;
    padding: 0.8rem 1.5rem;
  }
}
</style>
