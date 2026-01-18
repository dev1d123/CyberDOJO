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
          <div class="attempts-indicator">
            Intentos del antagonista: {{ antagonistAttempts }}/3
          </div>
        </div>
      </header>

      <!-- Chat Area -->
      <div class="chat-container" ref="chatContainer">
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
      <div v-if="!gameOver" class="input-container">
        <textarea
          v-model="userInput"
          @keydown.enter.prevent="sendMessage"
          placeholder="Escribe tu respuesta..."
          class="message-input"
          rows="2"
          :disabled="sending"
        ></textarea>
        <button
          @click="sendMessage"
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

const router = useRouter();
const route = useRoute();

const scenarioId = ref<number>(parseInt(route.params.scenarioId as string));
const scenarioName = ref<string>('');
const sessionId = ref<number | null>(null);
const messages = ref<any[]>([]);
const userInput = ref('');
const loading = ref(true);
const sending = ref(false);
const gameOver = ref(false);
const outcome = ref<string | null>(null);
const gameOverMessage = ref('');
const pointsEarned = ref(0);
const antagonistAttempts = ref(0);
const chatContainer = ref<HTMLElement | null>(null);

const scenarioNames: Record<number, string> = {
  1: 'Ingeniería Social',
  2: 'Suplantación Digital',
  3: 'Fuga de Datos',
  4: 'Pretextos Falsos',
  5: 'Trampas Digitales',
  6: 'Suplantación de Identidad',
};

onMounted(async () => {
  scenarioName.value = scenarioNames[scenarioId.value] || 'Simulación';
  await initializeSession();
});

async function initializeSession() {
  try {
    loading.value = true;

    // Try to resume an active session first
    try {
      const resumeResponse = await SimulationService.resumeSession();
      sessionId.value = resumeResponse.session_id;
      messages.value = resumeResponse.messages;
    } catch (resumeError) {
      // No active session, start a new one
      const startResponse = await SimulationService.startSession(scenarioId.value);
      sessionId.value = startResponse.session_id;
      messages.value = [
        {
          role: 'antagonist',
          content: startResponse.initial_message,
          sent_at: new Date().toISOString(),
        },
      ];
    }

    loading.value = false;
    await scrollToBottom();
  } catch (error: any) {
    console.error('Error initializing session:', error);
    alert('Error al iniciar la sesión: ' + error.message);
    goBack();
  }
}

async function sendMessage() {
  if (!userInput.value.trim() || sending.value || !sessionId.value) return;

  const messageText = userInput.value.trim();
  userInput.value = '';
  sending.value = true;

  // Add user message to UI
  messages.value.push({
    role: 'user',
    content: messageText,
    sent_at: new Date().toISOString(),
  });

  await scrollToBottom();

  try {
    const response = await SimulationService.sendMessage(sessionId.value, messageText);

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
