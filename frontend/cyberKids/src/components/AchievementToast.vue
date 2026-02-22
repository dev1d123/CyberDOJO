<template>
  <Teleport to="body">
    <Transition name="achievement-toast">
      <div
        v-if="isVisible && current"
        class="achievement-toast"
        @click="dismiss"
        role="alert"
      >
        <div class="toast-glow"></div>
        <div class="toast-content">
          <div class="toast-icon">
            <img v-if="current.icon" :src="current.icon" alt="" class="toast-icon-img" />
            <span v-else class="toast-icon-emoji">{{ getCategoryIcon(current.category) }}</span>
          </div>
          <div class="toast-info">
            <span class="toast-label">🏆 ¡Logro desbloqueado!</span>
            <span class="toast-name">{{ current.name }}</span>
            <span class="toast-desc">{{ current.description }}</span>
            <div class="toast-rewards">
              <span v-if="current.cybercreds_reward > 0" class="toast-reward coins">
                💰 +{{ current.cybercreds_reward }}
              </span>
              <span v-if="current.xp_reward > 0" class="toast-reward xp">
                ⭐ +{{ current.xp_reward }} XP
              </span>
            </div>
          </div>
        </div>
        <div class="toast-progress">
          <div class="toast-progress-bar"></div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { achievementNotifications } from '../stores/achievementNotification.store';

const { current, isVisible, dismiss } = achievementNotifications;

const getCategoryIcon = (category: string): string => {
  const icons: Record<string, string> = {
    quiz: '📝',
    simulation: '🛡️',
    progression: '🚀',
    social: '👥',
    collection: '✨',
  };
  return icons[category] || '🏆';
};
</script>

<style scoped>
.achievement-toast {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 99999;
  min-width: 320px;
  max-width: 420px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
  border: 2px solid rgba(255, 215, 0, 0.6);
  border-radius: 16px;
  padding: 16px 20px 10px;
  cursor: pointer;
  overflow: hidden;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.5),
    0 0 40px rgba(255, 215, 0, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.toast-glow {
  position: absolute;
  inset: -2px;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.3), transparent 60%);
  pointer-events: none;
  animation: glowPulse 2s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}

.toast-content {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  position: relative;
  z-index: 1;
}

.toast-icon {
  width: 52px;
  height: 52px;
  min-width: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.2), rgba(255, 140, 0, 0.15));
  border-radius: 12px;
  border: 1px solid rgba(255, 215, 0, 0.3);
  animation: iconPop 0.5s cubic-bezier(0.17, 0.67, 0.35, 1.3);
}

@keyframes iconPop {
  0% { transform: scale(0); }
  60% { transform: scale(1.2); }
  100% { transform: scale(1); }
}

.toast-icon-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
}

.toast-icon-emoji {
  font-size: 1.8rem;
}

.toast-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
  min-width: 0;
}

.toast-label {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  color: #ffd700;
  font-weight: 700;
}

.toast-name {
  font-size: 1.05rem;
  font-weight: 700;
  color: #fff;
  line-height: 1.3;
}

.toast-desc {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.65);
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.toast-rewards {
  display: flex;
  gap: 10px;
  margin-top: 4px;
}

.toast-reward {
  font-size: 0.78rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 8px;
}

.toast-reward.coins {
  background: rgba(255, 215, 0, 0.15);
  color: #ffd700;
}

.toast-reward.xp {
  background: rgba(96, 165, 250, 0.15);
  color: #60a5fa;
}

/* Auto-dismiss progress bar */
.toast-progress {
  position: relative;
  z-index: 1;
  height: 3px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  margin-top: 10px;
  overflow: hidden;
}

.toast-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #ffd700, #ff8c00);
  border-radius: 2px;
  animation: progressShrink 5s linear forwards;
}

@keyframes progressShrink {
  from { width: 100%; }
  to { width: 0%; }
}

/* Transitions */
.achievement-toast-enter-active {
  animation: toastSlideIn 0.5s cubic-bezier(0.17, 0.67, 0.35, 1.2);
}

.achievement-toast-leave-active {
  animation: toastSlideOut 0.35s ease-in forwards;
}

@keyframes toastSlideIn {
  0% {
    transform: translateX(120%);
    opacity: 0;
  }
  100% {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes toastSlideOut {
  0% {
    transform: translateX(0);
    opacity: 1;
  }
  100% {
    transform: translateX(120%);
    opacity: 0;
  }
}

/* Responsive */
@media (max-width: 480px) {
  .achievement-toast {
    bottom: 16px;
    right: 16px;
    left: 16px;
    min-width: unset;
    max-width: unset;
  }
}
</style>
