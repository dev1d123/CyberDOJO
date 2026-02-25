import { ref, readonly } from 'vue';

export interface AchievementNotification {
  id: number;
  name: string;
  description: string;
  category: string;
  icon: string | null;
  cybercreds_reward: number;
  xp_reward: number;
}

const queue = ref<AchievementNotification[]>([]);
const current = ref<AchievementNotification | null>(null);
const isVisible = ref(false);

let dismissTimer: ReturnType<typeof setTimeout> | null = null;

function showNext() {
  if (queue.value.length === 0) {
    current.value = null;
    isVisible.value = false;
    return;
  }

  current.value = queue.value.shift()!;
  isVisible.value = true;

  dismissTimer = setTimeout(() => {
    dismiss();
  }, 5000);
}

/**
 * Add one or more achievement notifications to the queue.
 */
function notify(achievements: AchievementNotification | AchievementNotification[]) {
  const list = Array.isArray(achievements) ? achievements : [achievements];
  if (list.length === 0) return;

  queue.value.push(...list);

  // If nothing is showing, start the chain
  if (!isVisible.value) {
    showNext();
  }
}

/**
 * Dismiss the current notification and show the next one (if any).
 */
function dismiss() {
  if (dismissTimer) {
    clearTimeout(dismissTimer);
    dismissTimer = null;
  }
  isVisible.value = false;

  // Small delay before showing the next one
  setTimeout(() => {
    showNext();
  }, 400);
}

/**
 * Parse unlocked achievements from a backend API response and trigger notifications.
 * Backend responses include an `achievements_unlocked` array.
 */
function handleApiResponse(response: any) {
  if (!response) return;

  const unlocked: any[] = response.achievements_unlocked ?? response.unlocked_achievements ?? [];
  if (!Array.isArray(unlocked) || unlocked.length === 0) return;

  const notifications: AchievementNotification[] = unlocked.map((a: any) => ({
    id: a.achievement_id ?? a.id ?? 0,
    name: a.name ?? 'Logro desbloqueado',
    description: a.description ?? '',
    category: a.category ?? '',
    icon: a.icon ?? null,
    cybercreds_reward: a.cybercreds_reward ?? 0,
    xp_reward: a.xp_reward ?? 0,
  }));

  notify(notifications);
}

export const achievementNotifications = {
  current: readonly(current),
  isVisible: readonly(isVisible),
  queueSize: readonly(queue),
  notify,
  dismiss,
  handleApiResponse,
};
