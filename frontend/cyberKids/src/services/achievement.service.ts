import type { 
  Achievement, 
  AchievementSummary, 
  ClaimAchievementResponse,
  AchievementCategory 
} from '../dto/achievement.dto';

import { API_CONFIG } from '../config/api.config';

const API_BASE_URL = API_CONFIG.BASE_URL;

export class AchievementService {
  /**
   * Obtener todos los logros con su estado para el usuario actual
   */
  static async getMyAchievements(): Promise<Achievement[]> {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      throw new Error('No hay token de acceso');
    }

    const response = await fetch(`${API_BASE_URL}/progression/user-achievements/my-achievements/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw error;
    }

    return await response.json();
  }

  /**
   * Obtener resumen de logros del usuario
   */
  static async getAchievementSummary(): Promise<AchievementSummary> {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      throw new Error('No hay token de acceso');
    }

    const response = await fetch(`${API_BASE_URL}/progression/user-achievements/summary/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw error;
    }

    return await response.json();
  }

  /**
   * Reclamar recompensa de un logro
   */
  static async claimAchievement(achievementId: number): Promise<ClaimAchievementResponse> {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      throw new Error('No hay token de acceso');
    }

    const response = await fetch(`${API_BASE_URL}/progression/user-achievements/claim/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ achievement_id: achievementId }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw error;
    }

    return await response.json();
  }

  /**
   * Obtener categorías de logros disponibles
   */
  static async getCategories(): Promise<AchievementCategory[]> {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      throw new Error('No hay token de acceso');
    }

    const response = await fetch(`${API_BASE_URL}/progression/achievements/categories/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw error;
    }

    return await response.json();
  }

  /**
   * Obtener logros por categoría
   */
  static async getAchievementsByCategory(category: string): Promise<Achievement[]> {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      throw new Error('No hay token de acceso');
    }

    const response = await fetch(`${API_BASE_URL}/progression/achievements/?category=${category}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw error;
    }

    return await response.json();
  }
}
