<template>
  <div class="simulation-page">
    <div class="simulation-container">
      <!-- Header -->
      <header class="simulation-header">
        <button class="back-button" @click="goBack">
          ← Volver
        </button>
        <div class="scenario-info">
          <h2 class="scenario-title">{{ scenarioName }}</h2>
          <div v-if="!showInitScreen" class="attempts-indicator">
            Intentos del antagonista: {{ antagonistAttempts }}/3
          </div>
        </div>
      </header>

      <!-- Initial Screen: Continue or Start New -->
      <div v-if="showInitScreen" class="init-screen">
        <div class="init-card">
          <h2 class="init-title">{{ scenarioName }}</h2>
          <p class="init-description">Prepárate para enfrentar un escenario de ingeniería social</p>
          
          <div class="init-actions">
            <button 
              v-if="hasActiveSession" 
              class="continue-button" 
              @click="continueSession"
              :disabled="loading"
            >
              <span class="button-icon">▶️</span>
              Continuar Conversación
            </button>
            
            <button 
              class="new-session-button" 
              @click="confirmNewSession"
              :disabled="loading"
            >
              <span class="button-icon">🆕</span>
              Nueva Conversación
            </button>
          </div>
          
          <div v-if="loading" class="init-loading">
            <div class="spinner"></div>
            <p>Cargando...</p>
          </div>
        </div>
      </div>

      <!-- Chat Area -->
      <div v-else class="chat-container" ref="chatContainer">
        <div v-if="loading" class="loading">
          <div class="spinner"></div>
          <p>Cargando conversación...</p>
        </div>

        <div v-else class="messages">
          <div
            v-for="(msg, index) in messages"
            :key="index"
            :class="['message', msg.role]"
          >
            <div class="message-content">
              <div class="message-header">
                <span class="message-sender">{{ getSenderName(msg.role) }}</span>
                <span class="message-time">{{ formatTime(msg.sent_at) }}</span>
              </div>
              <p class="message-text">{{ msg.content }}</p>
            </div>
          </div>
        </div>

        <!-- Game Over Overlay -->
        <div v-if="gameOver" class="game-over-overlay">
          <div class="game-over-card">
            <div :class="['game-over-icon', outcome]">
              {{ outcome === 'won' ? '🎉' : '😞' }}
            </div>
            <h2 class="game-over-title">
              {{ outcome === 'won' ? '¡Felicitaciones!' : '¡Juego Terminado!' }}
            </h2>
            <p class="game-over-message">{{ gameOverMessage }}</p>
            <div v-if="outcome === 'won' && pointsEarned > 0" class="points-earned">
              +{{ pointsEarned }} CyberCreds
            </div>
            <div class="game-over-actions">
              <button class="primary-button" @click="goBack">
                Volver al Mapa
              </button>
              <button v-if="outcome === 'failed'" class="secondary-button" @click="retryLevel">
                Reintentar Nivel
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div v-if="!gameOver && !showInitScreen" class="input-container">
        <textarea
          v-model="userInput"
          v-pet-hint="{ behavior: 'hover', vars: { target: 'escribir tu respuesta' } }"
          @keydown.enter.prevent="sendMessage"
          placeholder="Escribe tu respuesta..."
          class="message-input"
          rows="2"
          :disabled="sending"
        ></textarea>
        <button
          @click="sendMessage"
          v-pet-hint="{ behavior: 'hover_button', vars: { target: 'enviar tu mensaje' }, click: { behavior: 'send_message', ttlMs: 2200, priority: 1 } }"
          :disabled="!userInput.trim() || sending"
          class="send-button"
        >
          {{ sending ? '...' : '➤' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { SimulationService } from '../services/simulation.service';
import { useAudio } from '../composables/useAudio';
import { PetSpeech } from '@/stores/petSpeech.store';

const router = useRouter();
const route = useRoute();

// Audio service
const { playSend, playReceive, playDialog } = useAudio();

const scenarioId = ref<number>(parseInt(route.params.scenarioId as string));
const scenarioName = ref<string>('');
const sessionId = ref<number | null>(null);
const messages = ref<any[]>([]);
const userInput = ref('');
const loading = ref(false);
const sending = ref(false);
const gameOver = ref(false);
const outcome = ref<string | null>(null);
const gameOverMessage = ref('');
const pointsEarned = ref(0);
const antagonistAttempts = ref(0);
const chatContainer = ref<HTMLElement | null>(null);
const showInitScreen = ref(true);
const hasActiveSession = ref(false);

const scenarioNames: Record<number, string> = {
  1: 'Ingeniería Social',
  2: 'Suplantación Digital',
  3: 'Fuga de Datos',
  4: 'Pretextos Falsos',
  5: 'Trampas Digitales',
  6: 'Suplantación de Identidad',
};

// Initialize on mount
onMounted(() => {
  scenarioName.value = scenarioNames[scenarioId.value] || 'Simulación';
  checkActiveSession();
});

async function checkActiveSession() {
  try {
    loading.value = true;
    
    // Check if there's an active session for this scenario
    await SimulationService.resumeSession(scenarioId.value);
    
    // If we get here, there's an active session
    hasActiveSession.value = true;
  } catch (error) {
    // No active session found
    console.log('No hay sesión activa, mostrando pantalla inicial');
    hasActiveSession.value = false;
  } finally {
    // SIEMPRE desactivar loading
    loading.value = false;
  }
}

async function continueSession() {
  try {
    loading.value = true;
    showInitScreen.value = false;

    // Reproducir sonido de diálogo
    playDialog();

    const resumeResponse = await SimulationService.resumeSession(scenarioId.value);
    sessionId.value = resumeResponse.session_id;
    messages.value = resumeResponse.messages;
    antagonistAttempts.value = resumeResponse.antagonist_attempts || 0;

    loading.value = false;
    await scrollToBottom();
  } catch (error: any) {
    console.error('Error continuing session:', error);
    alert('Error al continuar la sesión: ' + error.message);
    showInitScreen.value = true;
    loading.value = false;
  }
}

async function confirmNewSession() {
  if (hasActiveSession.value) {
    const confirmed = confirm(
      '⚠️ Ya tienes una conversación activa en este nivel.\n\n' +
      'Si inicias una nueva conversación, perderás el progreso de la conversación actual.\n\n' +
      '¿Estás seguro de que deseas comenzar de nuevo?'
    );
    
    if (!confirmed) {
      return;
    }
  }
  
  await startNewSession();
}

async function startNewSession() {
  try {
    loading.value = true;
    showInitScreen.value = false;

    // Reproducir sonido de diálogo
    playDialog();

    const startResponse = await SimulationService.startSession(scenarioId.value);
    sessionId.value = startResponse.session_id;
    messages.value = [
      {
        role: 'antagonist',
        content: startResponse.initial_message,
        sent_at: new Date().toISOString(),
      },
    ];
    antagonistAttempts.value = 0;
    hasActiveSession.value = true;

    loading.value = false;
    await scrollToBottom();
  } catch (error: any) {
    console.error('Error starting new session:', error);
    alert('Error al iniciar nueva sesión: ' + error.message);
    showInitScreen.value = true;
    loading.value = false;
  }
}

async function sendMessage() {
  if (!userInput.value.trim() || sending.value || !sessionId.value) return;

  const messageText = userInput.value.trim();
  userInput.value = '';
  sending.value = true;

  // Reproducir sonido de enviar
  playSend();
  PetSpeech.speak({ behavior: 'send_message', ttlMs: 2400, priority: 1 });

  // Add user message to UI
  messages.value.push({
    role: 'user',
    content: messageText,
    sent_at: new Date().toISOString(),
  });

  await scrollToBottom();

  try {
    const response = await SimulationService.sendMessage(sessionId.value, messageText);

    // Reproducir sonido de recibir
    playReceive();
    PetSpeech.speak({ behavior: 'receive_message', ttlMs: 3200, priority: 1 });

    // Add antagonist response
    messages.value.push({
      role: 'antagonist',
      content: response.reply,
      sent_at: new Date().toISOString(),
    });

    antagonistAttempts.value = response.antagonist_attempts;

    // Check if game is over
    if (response.is_game_over !== null) {
      gameOver.value = true;
      outcome.value = response.outcome;

      PetSpeech.speak({
        behavior: response.outcome === 'won' ? 'success' : 'error',
        ttlMs: 2800,
        priority: 2,
      });
      
      if (response.outcome === 'won') {
        gameOverMessage.value = '¡Excelente trabajo! Resististe todos los intentos de ingeniería social.';
        pointsEarned.value = 180; // Could get from response
      } else {
        gameOverMessage.value = response.game_over_reason || 'Compartiste información sensible. ¡Inténtalo de nuevo!';
      }
    }

    await scrollToBottom();
  } catch (error: any) {
    console.error('Error sending message:', error);
    PetSpeech.speak({ behavior: 'error', ttlMs: 2800, priority: 2 });
    alert('Error al enviar mensaje: ' + error.message);
  } finally {
    sending.value = false;
  }
}

function getSenderName(role: string): string {
  if (role === 'user') return 'Tú';
  if (role === 'antagonist') return 'Desconocido';
  return 'Sistema';
}

function formatTime(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
}

async function scrollToBottom() {
  await nextTick();
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
}

function goBack() {
  router.push('/history');
}

function retryLevel() {
  router.go(0); // Reload page to start new session
}
</script>

<style scoped>
.simulation-page {
  height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.simulation-container {
  width: 100%;
  max-width: 900px;
  height: 90vh;
  background: white;
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.simulation-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-button {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.2s;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.3);
}

.scenario-info {
  flex: 1;
}

.scenario-title {
  margin: 0 0 4px 0;
  font-size: 1.5rem;
  font-weight: 700;
}

.attempts-indicator {
  font-size: 0.9rem;
  opacity: 0.9;
}

.init-screen {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: #f5f5f5;
}

.init-card {
  background: white;
  padding: 48px;
  border-radius: 24px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 500px;
  width: 100%;
}

.init-title {
  margin: 0 0 16px 0;
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
}

.init-description {
  margin: 0 0 32px 0;
  font-size: 1.1rem;
  color: #666;
  line-height: 1.6;
}

.init-actions {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.continue-button,
.new-session-button {
  padding: 16px 32px;
  border-radius: 16px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.continue-button {
  background: linear-gradient(135deg, #52c41a 0%, #389e0d 100%);
  color: white;
}

.continue-button:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(82, 196, 26, 0.4);
}

.new-session-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.new-session-button:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
}

.continue-button:disabled,
.new-session-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.button-icon {
  font-size: 1.3rem;
}

.init-loading {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #666;
}

.init-loading .spinner {
  width: 32px;
  height: 32px;
}

.init-loading p {
  margin: 0;
  font-size: 0.95rem;
}

.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: #f5f5f5;
  position: relative;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 16px;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e0e0e0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message {
  display: flex;
  max-width: 70%;
}

.message.user {
  align-self: flex-end;
}

.message.antagonist {
  align-self: flex-start;
}

.message-content {
  background: white;
  padding: 12px 16px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message.user .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  gap: 12px;
}

.message-sender {
  font-weight: 700;
  font-size: 0.85rem;
}

.message.user .message-sender {
  color: rgba(255, 255, 255, 0.9);
}

.message-time {
  font-size: 0.75rem;
  opacity: 0.6;
}

.message-text {
  margin: 0;
  line-height: 1.5;
  word-wrap: break-word;
}

.game-over-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  z-index: 10;
}

.game-over-card {
  background: white;
  padding: 40px;
  border-radius: 24px;
  text-align: center;
  max-width: 500px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}

.game-over-icon {
  font-size: 5rem;
  margin-bottom: 16px;
}

.game-over-title {
  margin: 0 0 16px 0;
  font-size: 2rem;
  color: #2c3e50;
}

.game-over-message {
  margin: 0 0 24px 0;
  color: #666;
  font-size: 1.1rem;
  line-height: 1.6;
}

.points-earned {
  font-size: 2rem;
  font-weight: 900;
  color: #667eea;
  margin-bottom: 24px;
}

.game-over-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.primary-button,
.secondary-button {
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.primary-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.primary-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
}

.secondary-button {
  background: #e0e0e0;
  color: #333;
}

.secondary-button:hover {
  background: #d0d0d0;
}

.input-container {
  padding: 16px 24px;
  background: white;
  border-top: 2px solid #e0e0e0;
  display: flex;
  gap: 12px;
}

.message-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 16px;
  font-size: 1rem;
  font-family: inherit;
  resize: none;
  transition: border-color 0.2s;
}

.message-input:focus {
  outline: none;
  border-color: #667eea;
}

.message-input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.send-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  width: 56px;
  height: 56px;
  border-radius: 16px;
  font-size: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-button:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .simulation-page {
    padding: 0;
  }

  .simulation-container {
    height: 100vh;
    border-radius: 0;
    max-width: 100%;
  }

  .message {
    max-width: 85%;
  }
}
</style>
