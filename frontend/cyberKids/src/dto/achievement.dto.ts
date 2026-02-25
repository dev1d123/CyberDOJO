export interface Achievement {
  achievement_id: number;
  name: string;
  description: string;
  category: 'quiz' | 'simulation' | 'progression' | 'social' | 'collection';
  icon: string | null;
  cybercreds_reward: number;
  xp_reward: number;
  requirement_type: string;
  requirement_value: number;
  is_hidden: boolean;
  is_unlocked: boolean;
  progress: number;
  unlocked_at: string | null;
  is_claimed: boolean;
}

export interface AchievementSummary {
  total: number;
  unlocked: number;
  claimed: number;
  pending_claims: number;
  percentage: number;
  recent: UserAchievement[];
}

export interface UserAchievement {
  user_achievement_id: number;
  user: number;
  achievement: number;
  unlocked_at: string;
  progress: number;
  is_claimed: boolean;
  achievement_name: string;
  achievement_description: string;
  achievement_category: string;
  achievement_icon: string | null;
  cybercreds_reward: number;
  xp_reward: number;
  requirement_value: number;
  is_hidden: boolean;
}

export interface ClaimAchievementResponse {
  message: string;
  cybercreds_earned: number;
  xp_earned: number;
  new_cybercreds: number;
}

export interface AchievementCategory {
  value: string;
  label: string;
}
