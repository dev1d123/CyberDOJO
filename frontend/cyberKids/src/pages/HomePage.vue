<script setup lang="ts">
</script>

<template>
  <div class="home-page">
    <div class="content-container">
      <!-- Hero Section with GIF -->
      <div class="hero-container">
        <h1 class="hero-title">¡Bienvenido a CyberDojo!</h1>
        <div class="welcome-gif-container">
          <img src="/src/assets/gif/welcome.gif" alt="Welcome" class="welcome-gif" />
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
        <div class="action-container">
          <button class="cta-button primary">
            <span class="button-icon">👤</span>
            ¡Crea una cuenta!
          </button>
          <p class="cta-subtext">o inicia sesión si ya tienes una</p>
        </div>
        
        <div class="help-box">
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
  padding: 2rem;
  overflow: hidden;
}

.content-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  max-width: 1400px;
  width: 100%;
  align-items: center;
  justify-content: center;
}

/* Hero Container with GIF */
.hero-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2rem;
  flex-wrap: wrap;
}

/* Hero Title */
.hero-title {
  font-size: 5rem;
  color: #fff;
  text-shadow: 
    4px 4px 0px #ff6b6b,
    8px 8px 0px rgba(0, 0, 0, 0.3);
  margin: 0;
  animation: heroFloat 3s ease-in-out infinite;
  line-height: 1.2;
}

/* Mission Box */
.mission-box {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 30px;
  padding: 2.5rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  border: 5px solid #ff6b6b;
  backdrop-filter: blur(10px);
  transform: translateZ(0);
  transition: all 0.4s ease;
  width: 100%;
  max-width: 1100px;
}

.mission-text {
  font-size: 1.8rem;
  line-height: 1.6;
  color: #2c3e50;
  margin: 0 0 1rem 0;
  text-align: center;
}

.highlight {
  color: #ff6b6b;
  font-weight: bold;
  font-size: 1.15em;
  text-shadow: 2px 2px 4px rgba(255, 107, 107, 0.3);
}

.action-text {
  font-size: 1.6rem;
  margin-top: 1.5rem;
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
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 3rem;
  flex-wrap: wrap;
  width: 100%;
  max-width: 1100px;
}

/* Action Container */
.action-container {
  text-align: center;
  flex: 1;
  min-width: 300px;
}

.cta-button {
  background: linear-gradient(135deg, #48c6ef 0%, #6f86d6 100%);
  color: white;
  border: none;
  padding: .5rem 3rem;
  border-radius: 50px;
  font-size: 1.8rem;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 15px 40px rgba(72, 198, 239, 0.5);
  transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  display: inline-flex;
  align-items: center;
  gap: 1rem;
  border: 4px solid rgba(255, 255, 255, 0.5);
}

.cta-button:hover {
  transform: translateY(-8px) scale(1.08);
  box-shadow: 0 20px 50px rgba(72, 198, 239, 0.7);
  background: linear-gradient(135deg, #6f86d6 0%, #48c6ef 100%);
}

.button-icon {
  font-size: 2rem;
  animation: iconSpin 2s infinite;
}

.cta-subtext {
  margin-top: 1rem;
  font-size: 1.4rem;
  color: white;
  font-weight: bold;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

/* Welcome GIF */
.welcome-gif-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
  border: 5px solid #fdcb6e;
  transition: all 0.3s ease;
  flex: 1;
  min-width: 300px;
}

.help-box {
  background: rgba(254, 202, 87, 0.95);
  border-radius: 25px;
  padding: 0rem;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3);
  border: 5px solid #fdcb6e;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  flex: 1;
  min-width: 300px;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.help-box:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
}

.lightbulb-icon {
  font-size: 3.5rem;
  animation: glow 2s infinite;
  flex-shrink: 0;
}

.help-text {
  font-size: 1.5rem;
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
    padding: 1.2rem 2.5rem;
  }
  
  .welcome-gif {
    max-height: 180px;
  }
  
  .actions-row {
    gap: 2rem;
  }
}

@media (max-width: 768px) {
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
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .cta-button {
    font-size: 1.2rem;
    padding: 1rem 2rem;
  }
  
  .help-text {
    font-size: 1.2rem;
  }
}
</style>
