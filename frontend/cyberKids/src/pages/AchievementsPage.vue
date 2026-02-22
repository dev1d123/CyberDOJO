<template>
  <div class="achievements-page">
    <!-- Header -->
    <div class="achievements-header">
      <button class="back-button" @click="goBack">
        <span class="back-icon">←</span>
        Volver
      </button>
      <h1 class="page-title">Mis Logros</h1>
      <div class="summary-badge" v-if="summary">
        <span class="trophy-icon">🏆</span>
        <span class="summary-text">{{ summary.unlocked }}/{{ summary.total }}</span>
        <span class="percentage">({{ summary.percentage }}%)</span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>Cargando logros...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-container">
      <p class="error-text">{{ error }}</p>
      <button @click="loadAchievements" class="retry-button">Reintentar</button>
    </div>

    <!-- Content -->
    <div v-else class="achievements-content">
      <!-- Summary Cards -->
      <div class="summary-cards" v-if="summary">
        <div class="summary-card unlocked">
          <span class="card-icon">🔓</span>
          <div class="card-info">
            <span class="card-value">{{ summary.unlocked }}</span>
            <span class="card-label">Desbloqueados</span>
          </div>
        </div>
        <div class="summary-card pending" v-if="summary.pending_claims > 0">
          <span class="card-icon">🎁</span>
          <div class="card-info">
            <span class="card-value">{{ summary.pending_claims }}</span>
            <span class="card-label">Por reclamar</span>
          </div>
        </div>
        <div class="summary-card progress">
          <span class="card-icon">📊</span>
          <div class="card-info">
            <span class="card-value">{{ summary.percentage }}%</span>
            <span class="card-label">Completado</span>
          </div>
        </div>
      </div>

      <!-- Category Filter -->
      <div class="category-filter">
        <button 
          v-for="cat in categories" 
          :key="cat.value"
          :class="['filter-btn', { active: selectedCategory === cat.value }]"
          @click="filterByCategory(cat.value)"
        >
          {{ getCategoryIcon(cat.value) }} {{ cat.label }}
        </button>
      </div>

      <!-- Achievements Grid -->
      <div class="achievements-grid">
        <div 
          v-for="achievement in filteredAchievements" 
          :key="achievement.achievement_id"
          :class="['achievement-card', { 
            unlocked: achievement.is_unlocked, 
            locked: !achievement.is_unlocked,
            hidden: achievement.is_hidden && !achievement.is_unlocked,
            claimable: achievement.is_unlocked && !achievement.is_claimed
          }]"
          @click="handleAchievementClick(achievement)"
        >
          <div class="achievement-icon">
            <img 
              v-if="achievement.icon && achievement.is_unlocked" 
              :src="achievement.icon" 
              :alt="achievement.name"
              class="icon-image"
            />
            <span v-else class="icon-placeholder">
              {{ achievement.is_hidden && !achievement.is_unlocked ? '🔒' : getDefaultIcon(achievement.category) }}
            </span>
            <div v-if="achievement.is_unlocked && !achievement.is_claimed" class="claim-indicator">!</div>
            <div v-if="achievement.is_unlocked" class="unlocked-check">✓</div>
          </div>
          
          <div class="achievement-info">
            <h3 class="achievement-name">{{ achievement.name }}</h3>
            <p class="achievement-description">{{ achievement.description }}</p>
            
            <div v-if="!achievement.is_unlocked && !achievement.is_hidden" class="progress-container">
              <div class="progress-bar">
                <div 
                  class="progress-fill" 
                  :style="{ width: `${getProgressPercent(achievement)}%` }"
                ></div>
              </div>
              <span class="progress-text">{{ achievement.progress }}/{{ achievement.requirement_value }}</span>
            </div>

            <!-- Completed indicator for unlocked -->
            <div v-if="achievement.is_unlocked && !achievement.is_hidden" class="progress-container completed">
              <div class="progress-bar">
                <div class="progress-fill full" style="width: 100%"></div>
              </div>
              <span class="progress-text done">✓ Completado</span>
            </div>

            <!-- Rewards -->
            <div class="rewards" v-if="achievement.is_unlocked || !achievement.is_hidden">
              <span v-if="achievement.cybercreds_reward > 0" class="reward cybercreds">
                💰 {{ achievement.cybercreds_reward }}
              </span>
              <span v-if="achievement.xp_reward > 0" class="reward xp">
                ⭐ {{ achievement.xp_reward }} XP
              </span>
            </div>

            <div v-if="achievement.is_unlocked" class="unlocked-info">
              <span class="unlocked-date">
                🏆 Desbloqueado: {{ formatDate(achievement.unlocked_at) }}
              </span>
            </div>
          </div>

          <button 
            v-if="achievement.is_unlocked && !achievement.is_claimed"
            class="claim-button"
            @click.stop="claimReward(achievement)"
          >
            Reclamar
          </button>
          <div v-else-if="achievement.is_claimed" class="claimed-badge">
            ✓ Reclamado
          </div>
        </div>
      </div>

      <div v-if="filteredAchievements.length === 0" class="empty-state">
        <span class="empty-icon">🏆</span>
        <p>No hay logros en esta categoría</p>
      </div>
    </div>

    <!-- Claim Modal -->
    <Teleport to="body">
      <div v-if="showClaimModal" class="modal-overlay" @click="closeClaimModal">
        <div class="claim-modal" @click.stop>
          <div class="modal-header">
            <h2>¡Recompensa Reclamada!</h2>
          </div>
          <div class="modal-content">
            <div class="reward-animation">🎉</div>
            <p class="claim-message">{{ claimResult?.message }}</p>
            <div class="rewards-received">
              <div v-if="claimResult && claimResult.cybercreds_earned > 0" class="reward-item">
                <span class="reward-icon">💰</span>
                <span>+{{ claimResult?.cybercreds_earned }} CyberCredits</span>
              </div>
              <div v-if="claimResult && claimResult.xp_earned > 0" class="reward-item">
                <span class="reward-icon">⭐</span>
                <span>+{{ claimResult?.xp_earned }} XP</span>
              </div>
            </div>
          </div>
          <button class="modal-close-btn" @click="closeClaimModal">¡Genial!</button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { AchievementService } from '../services/achievement.service';
import type { Achievement, AchievementSummary, ClaimAchievementResponse, AchievementCategory } from '../dto/achievement.dto';

const router = useRouter();

const loading = ref(true);
const error = ref<string | null>(null);
const achievements = ref<Achievement[]>([]);
const summary = ref<AchievementSummary | null>(null);
const selectedCategory = ref<string>('all');
const showClaimModal = ref(false);
const claimResult = ref<ClaimAchievementResponse | null>(null);

const categories = ref<AchievementCategory[]>([
  { value: 'all', label: 'Todos' },
  { value: 'quiz', label: 'Quiz' },
  { value: 'simulation', label: 'Simulación' },
  { value: 'progression', label: 'Progresión' },
  { value: 'social', label: 'Social' },
  { value: 'collection', label: 'Colección' },
]);

const filteredAchievements = computed(() => {
  if (selectedCategory.value === 'all') {
    return achievements.value;
  }
  return achievements.value.filter(a => a.category === selectedCategory.value);
});

onMounted(() => {
  loadAchievements();
});

const loadAchievements = async () => {
  loading.value = true;
  error.value = null;

  try {
    const [achievementsData, summaryData] = await Promise.all([
      AchievementService.getMyAchievements(),
      AchievementService.getAchievementSummary()
    ]);
    
    achievements.value = achievementsData;
    summary.value = summaryData;
  } catch (err: any) {
    console.error('Error loading achievements:', err);
    error.value = 'No se pudieron cargar los logros. Intenta de nuevo.';
  } finally {
    loading.value = false;
  }
};

const filterByCategory = (category: string) => {
  selectedCategory.value = category;
};

const getCategoryIcon = (category: string): string => {
  const icons: Record<string, string> = {
    all: '📋',
    quiz: '📝',
    simulation: '🎮',
    progression: '📈',
    social: '👥',
    collection: '🎨',
  };
  return icons[category] || '🏆';
};

const getDefaultIcon = (category: string): string => {
  const icons: Record<string, string> = {
    quiz: '📝',
    simulation: '🎮',
    progression: '🎯',
    social: '🤝',
    collection: '✨',
  };
  return icons[category] || '🏆';
};

const getProgressPercent = (achievement: Achievement): number => {
  if (!achievement.requirement_value || achievement.requirement_value === 0) return 0;
  return Math.min((achievement.progress / achievement.requirement_value) * 100, 100);
};

const formatDate = (dateString: string | null): string => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('es-ES', { 
    day: 'numeric', 
    month: 'short', 
    year: 'numeric' 
  });
};

const handleAchievementClick = (achievement: Achievement) => {
  if (achievement.is_unlocked && !achievement.is_claimed) {
    claimReward(achievement);
  }
};

const claimReward = async (achievement: Achievement) => {
  try {
    const result = await AchievementService.claimAchievement(achievement.achievement_id);
    claimResult.value = result;
    showClaimModal.value = true;
    
    // Update local state
    const idx = achievements.value.findIndex(a => a.achievement_id === achievement.achievement_id);
    if (idx !== -1 && achievements.value[idx]) {
      achievements.value[idx].is_claimed = true;
    }
    
    // Update summary
    if (summary.value) {
      summary.value.claimed += 1;
      summary.value.pending_claims -= 1;
    }
  } catch (err: any) {
    console.error('Error claiming achievement:', err);
    alert(err.error || 'No se pudo reclamar la recompensa');
  }
};

const closeClaimModal = () => {
  showClaimModal.value = false;
  claimResult.value = null;
};

const goBack = () => {
  router.push('/dashboard');
};
</script>

<style scoped>
.achievements-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  padding: 20px;
  color: white;
}

.achievements-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(-5px);
}

.page-title {
  flex: 1;
  font-size: 2rem;
  background: linear-gradient(135deg, #ffd700, #ff8c00);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.summary-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 20px;
  font-weight: bold;
}

.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  gap: 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-top-color: #ffd700;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.retry-button {
  padding: 12px 30px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  border-radius: 12px;
  color: white;
  font-weight: bold;
  cursor: pointer;
  transition: transform 0.3s;
}

.retry-button:hover {
  transform: scale(1.05);
}

.summary-cards {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
  flex-wrap: wrap;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 15px 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  backdrop-filter: blur(10px);
  flex: 1;
  min-width: 150px;
}

.summary-card.unlocked {
  border: 2px solid #4ade80;
}

.summary-card.pending {
  border: 2px solid #ffd700;
  animation: pulse 2s infinite;
}

.summary-card.progress {
  border: 2px solid #60a5fa;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255, 215, 0, 0.4); }
  50% { box-shadow: 0 0 20px 5px rgba(255, 215, 0, 0.2); }
}

.card-icon {
  font-size: 2rem;
}

.card-info {
  display: flex;
  flex-direction: column;
}

.card-value {
  font-size: 1.5rem;
  font-weight: bold;
}

.card-label {
  font-size: 0.85rem;
  opacity: 0.8;
}

.category-filter {
  display: flex;
  gap: 10px;
  margin-bottom: 25px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 10px 18px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 0.9rem;
}

.filter-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.filter-btn.active {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-color: transparent;
}

.achievements-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.achievement-card {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  border: 2px solid transparent;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.achievement-card.unlocked {
  border-color: #4ade80;
  background: linear-gradient(135deg, rgba(74, 222, 128, 0.1), rgba(74, 222, 128, 0.05));
}

.achievement-card.locked {
  opacity: 0.55;
  filter: saturate(0.3);
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.08);
}

.achievement-card.locked:hover {
  opacity: 0.8;
  filter: saturate(0.6);
}

.achievement-card.hidden {
  opacity: 0.35;
  filter: grayscale(1) blur(1px);
  background: rgba(0, 0, 0, 0.2);
}

.achievement-card.hidden:hover {
  opacity: 0.5;
  filter: grayscale(0.8);
}

.achievement-card.claimable {
  border-color: #ffd700;
  animation: glow 2s infinite;
  cursor: pointer;
}

@keyframes glow {
  0%, 100% { box-shadow: 0 0 5px rgba(255, 215, 0, 0.3); }
  50% { box-shadow: 0 0 20px rgba(255, 215, 0, 0.5); }
}

.achievement-card:hover {
  transform: translateY(-5px);
}

.achievement-icon {
  position: relative;
  width: 60px;
  height: 60px;
  min-width: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
}

.icon-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 12px;
}

.icon-placeholder {
  font-size: 2rem;
}

.unlocked-check {
  position: absolute;
  bottom: -4px;
  right: -4px;
  width: 20px;
  height: 20px;
  background: #4ade80;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: bold;
  color: #1a1a2e;
  border: 2px solid #1a1a2e;
}

.claim-indicator {
  position: absolute;
  top: -5px;
  right: -5px;
  width: 20px;
  height: 20px;
  background: #ffd700;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: #1a1a2e;
  animation: bounce 1s infinite;
}

@keyframes bounce {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

.achievement-info {
  flex: 1;
}

.achievement-name {
  margin: 0 0 5px 0;
  font-size: 1.1rem;
}

.achievement-description {
  margin: 0 0 10px 0;
  font-size: 0.85rem;
  opacity: 0.8;
  line-height: 1.4;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 4px;
  transition: width 0.8s ease-out;
}

.progress-fill.full {
  background: linear-gradient(90deg, #4ade80, #22c55e);
}

.progress-container.completed .progress-bar {
  background: rgba(74, 222, 128, 0.15);
}

.progress-text {
  font-size: 0.8rem;
  opacity: 0.8;
  white-space: nowrap;
}

.progress-text.done {
  color: #4ade80;
  font-weight: 600;
}

.rewards {
  display: flex;
  gap: 10px;
  margin-bottom: 5px;
}

.reward {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}

.reward.cybercreds {
  background: rgba(255, 215, 0, 0.2);
  color: #ffd700;
}

.reward.xp {
  background: rgba(96, 165, 250, 0.2);
  color: #60a5fa;
}

.unlocked-info {
  margin-top: 8px;
}

.unlocked-date {
  font-size: 0.75rem;
  opacity: 0.6;
}

.claim-button {
  padding: 8px 16px;
  background: linear-gradient(135deg, #ffd700, #ff8c00);
  border: none;
  border-radius: 20px;
  color: #1a1a2e;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}

.claim-button:hover {
  transform: scale(1.05);
  box-shadow: 0 5px 20px rgba(255, 215, 0, 0.4);
}

.claimed-badge {
  padding: 8px 16px;
  background: rgba(74, 222, 128, 0.2);
  border-radius: 20px;
  color: #4ade80;
  font-size: 0.85rem;
  white-space: nowrap;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 15px;
  opacity: 0.5;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 20px;
}

.claim-modal {
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  border-radius: 20px;
  padding: 30px;
  max-width: 400px;
  width: 100%;
  text-align: center;
  border: 2px solid #ffd700;
  animation: modalPop 0.3s ease-out;
}

@keyframes modalPop {
  from {
    transform: scale(0.8);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.modal-header h2 {
  margin: 0 0 20px 0;
  background: linear-gradient(135deg, #ffd700, #ff8c00);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.reward-animation {
  font-size: 4rem;
  animation: celebrate 0.5s ease-out;
}

@keyframes celebrate {
  0% { transform: scale(0); }
  50% { transform: scale(1.3); }
  100% { transform: scale(1); }
}

.claim-message {
  margin: 15px 0;
  font-size: 1rem;
}

.rewards-received {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 20px 0;
}

.reward-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  font-weight: bold;
}

.reward-icon {
  font-size: 1.5rem;
}

.modal-close-btn {
  padding: 12px 40px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  border-radius: 25px;
  color: white;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.modal-close-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

/* Responsive */
@media (max-width: 768px) {
  .achievements-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .page-title {
    font-size: 1.5rem;
    order: -1;
    width: 100%;
  }
  
  .achievements-grid {
    grid-template-columns: 1fr;
  }
  
  .achievement-card {
    flex-wrap: wrap;
  }
  
  .claim-button,
  .claimed-badge {
    width: 100%;
    text-align: center;
    margin-top: 10px;
  }
}
</style>
