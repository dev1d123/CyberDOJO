// Service for simulation/game session API calls
import { API_CONFIG } from '../config/api.config';
import { AuthService } from './auth.service';

const API_BASE_URL = `${API_CONFIG.BASE_URL}/simulation`;
const devLog = (...args: unknown[]) => {
  if (import.meta.env.DEV) {
    console.log(...args);
  }
};

export interface ScenarioDto {
  scenario_id: number;
  name: string;
  description: string | null;
  antagonist_goal: string;
  difficulty_level: number;
  base_points: number;
  threat_type: string | null;
  is_active: boolean;
  user_score?: number;
}

interface StartSessionResponse {
  session_id: number;
  initial_message: string;
  resumed: boolean;
}

export interface GameState {
  lives_remaining: number;
  max_lives: number;
  current_progress: number;
  max_progress: number;
  is_game_over: boolean;
  outcome: string | null;
}

export interface GameWarning {
  message: string;
  title: string;
  type: string;
  lives_remaining: number;
}

interface ChatResponse {
  reply: string;
  session_id: number;
  disclosure: boolean;
  disclosure_reason: string | null;
  llm_analysis?: {
    has_disclosure: boolean;
    disclosure_reason: string;
    is_attack_attempt: boolean;
    is_user_evasion: boolean;
    force_end_session: boolean;
  };
  antagonist_attempts: number;
  is_game_over: boolean | null;
  outcome: string | null;
  game_over_reason: string | null;
  points_earned?: number;

  // New fields
  game_state?: GameState;
  warning?: GameWarning;
  credits_awarded?: number; // Actual credits added to wallet
  achievements_unlocked?: Array<{ id: number; name: string; description: string; icon?: string }>;
}

interface ChatMessage {
  role: string;
  content: string;
  sent_at: string;
}

interface ResumeSessionResponse {
  session_id: number;
  messages: ChatMessage[];
  resumed: boolean;
  antagonist_attempts?: number; // Repurposed as progress
  lives_remaining?: number;
}

export class SimulationService {
  private static getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('No hay token de autenticación. Por favor inicia sesión.');
    }
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };
  }

  // Wrapper function to handle 401 token expiration and refresh logic
  private static async fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
    const headers = this.getAuthHeaders();
    const finalOptions = {
      ...options,
      headers: {
        ...headers,
        ...(options.headers || {}),
      }
    };

    let response = await fetch(url, finalOptions);

    if (response.status === 401) {
      // Attempt token refresh
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          console.log('🔄 Token expired, attempting refresh...');
          const authData = await AuthService.refresh(refreshToken);

          // Update tokens
          if (authData.access) localStorage.setItem('access_token', authData.access);
          if (authData.refresh) localStorage.setItem('refresh_token', authData.refresh); // Rotate if provided

          // Retry original request with new token
          const newHeaders = this.getAuthHeaders();
          const retryOptions = {
            ...options,
            headers: {
              ...newHeaders,
              ...(options.headers || {}),
            }
          };
          console.log('🔄 Retrying request with new token...');
          response = await fetch(url, retryOptions);
        } catch (refreshError) {
          console.error('❌ Token refresh failed:', refreshError);
          // Redirect to login or throw error (let interceptors handle redirection if present)
          window.location.href = '/login'; // Simple client-side redirect fallback
          throw new Error('Sesión expirada. Por favor inicia sesión de nuevo.');
        }
      } else {
        // No refresh token available
        throw new Error('Sesión expirada. No refresh token available.');
      }
    }

    return response;
  }

  static async getScenarios(): Promise<ScenarioDto[]> {
    const response = await this.fetchWithAuth(`${API_BASE_URL}/scenarios/`, {
      method: 'GET',
    });

    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new Error(text || `Error al obtener escenarios: ${response.status}`);
    }

    const raw = await response.json();
    const scenarios = Array.isArray(raw) ? raw : (raw?.results ?? []);
    return [...scenarios].sort((a, b) => (a.difficulty_level - b.difficulty_level) || (a.scenario_id - b.scenario_id));
  }

  static async startSession(scenarioId: number): Promise<StartSessionResponse> {
    devLog('🚀 [START SESSION] Request:', { scenario_id: scenarioId });
    
    const response = await fetch(`${API_BASE_URL}/session/start-role/`, {
      method: 'POST',
      body: JSON.stringify({ scenario_id: scenarioId }),
    });

    devLog('📥 [START SESSION] Response status:', response.status);

    if (!response.ok) {
      const error = await response.json();
      console.error('❌ [START SESSION] Error:', error);
      throw new Error(error.error || 'Error al iniciar sesión');
    }

    const data = await response.json();
    devLog('✅ [START SESSION] Success:', data);
    return data;
  }

  static async resumeSession(scenarioId?: number): Promise<ResumeSessionResponse> {
    devLog('🔄 [RESUME SESSION] Request:', scenarioId ? { scenario_id: scenarioId } : {});
    
    const url = scenarioId 
      ? `${API_BASE_URL}/session/resume/?scenario_id=${scenarioId}`
      : `${API_BASE_URL}/session/resume/`;

    const response = await this.fetchWithAuth(url, {
      method: 'GET',
    });

    devLog('📥 [RESUME SESSION] Response status:', response.status);

    if (!response.ok) {
      // Backend retorna 404 con { error: 'no_active_session' } cuando no hay sesión.
      // Eso es un caso esperado; no lo tratamos como error ruidoso.
      if (response.status === 404) {
        const body: any = await response.json().catch(() => null);
        if (body?.error === 'no_active_session') {
          throw new Error('no_active_session');
        }
      }

      const error: any = await response.json().catch(() => null);
      throw new Error(error?.error || 'No hay sesión activa');
    }

    const data = await response.json();
    devLog('✅ [RESUME SESSION] Success:', data);
    return data;
  }

  static async sendMessage(sessionId: number, message: string): Promise<ChatResponse> {
    devLog('💬 [SEND MESSAGE] Request:', { session_id: sessionId, message });
    
    const response = await fetch(`${API_BASE_URL}/chat/`, {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        message: message,
      }),
    });

    devLog('📥 [SEND MESSAGE] Response status:', response.status);

    const contentType = response.headers.get('content-type') || '';
    const body = contentType.includes('application/json') ? await response.json() : await response.text();

    if (!response.ok) {
      console.error('❌ [SEND MESSAGE] Error:', body);
      const errObj: any = body;
      throw new Error(errObj?.error || (typeof body === 'string' ? body : 'Error al enviar mensaje'));
    }

    const data = body as ChatResponse;
    devLog('✅ [SEND MESSAGE] Success:', data);
    if (data.llm_analysis) {
      devLog('🧠 [LLM] analysis:', data.llm_analysis);
    }
    return data;
  }

  static async getSessionMessages(sessionId: number) {
    devLog('📨 [GET MESSAGES] Request:', { session_id: sessionId });
    
    const response = await fetch(`${API_BASE_URL}/session/${sessionId}/messages/`, {
      method: 'GET',
    });

    devLog('📥 [GET MESSAGES] Response status:', response.status);

    if (!response.ok) {
      console.error('❌ [GET MESSAGES] Error');
      throw new Error('Error al obtener mensajes');
    }

    const data = await response.json();
    devLog('✅ [GET MESSAGES] Success:', data);
    return data;
  }
}
