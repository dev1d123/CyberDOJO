// Service for simulation/game session API calls
import { API_CONFIG } from '../config/api.config';

const API_BASE_URL = `${API_CONFIG.BASE_URL}/simulation`;

export interface ScenarioDto {
  scenario_id: number;
  name: string;
  description: string | null;
  antagonist_goal: string;
  difficulty_level: number;
  base_points: number;
  threat_type: string | null;
  is_active: boolean;
}

interface StartSessionResponse {
  session_id: number;
  initial_message: string;
  resumed: boolean;
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
  antagonist_attempts?: number;
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

  static async getScenarios(): Promise<ScenarioDto[]> {
    const response = await fetch(`${API_BASE_URL}/scenarios/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new Error(text || `Error al obtener escenarios: ${response.status}`);
    }

    const data = (await response.json()) as ScenarioDto[];
    return [...data].sort((a, b) => (a.difficulty_level - b.difficulty_level) || (a.scenario_id - b.scenario_id));
  }

  static async startSession(scenarioId: number): Promise<StartSessionResponse> {
    console.log('🚀 [START SESSION] Request:', { scenario_id: scenarioId });
    
    const response = await fetch(`${API_BASE_URL}/session/start-role/`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ scenario_id: scenarioId }),
    });

    console.log('📥 [START SESSION] Response status:', response.status);

    if (!response.ok) {
      const error = await response.json();
      console.error('❌ [START SESSION] Error:', error);
      throw new Error(error.error || 'Error al iniciar sesión');
    }

    const data = await response.json();
    console.log('✅ [START SESSION] Success:', data);
    return data;
  }

  static async resumeSession(scenarioId?: number): Promise<ResumeSessionResponse> {
    console.log('🔄 [RESUME SESSION] Request:', scenarioId ? { scenario_id: scenarioId } : {});
    
    const url = scenarioId 
      ? `${API_BASE_URL}/session/resume/?scenario_id=${scenarioId}`
      : `${API_BASE_URL}/session/resume/`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    console.log('📥 [RESUME SESSION] Response status:', response.status);

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
    console.log('✅ [RESUME SESSION] Success:', data);
    return data;
  }

  static async sendMessage(sessionId: number, message: string): Promise<ChatResponse> {
    console.log('💬 [SEND MESSAGE] Request:', { session_id: sessionId, message });
    
    const response = await fetch(`${API_BASE_URL}/chat/`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        session_id: sessionId,
        message: message,
      }),
    });

    console.log('📥 [SEND MESSAGE] Response status:', response.status);

    const contentType = response.headers.get('content-type') || '';
    const body = contentType.includes('application/json') ? await response.json() : await response.text();

    if (!response.ok) {
      console.error('❌ [SEND MESSAGE] Error:', body);
      const errObj: any = body;
      throw new Error(errObj?.error || (typeof body === 'string' ? body : 'Error al enviar mensaje'));
    }

    const data = body as ChatResponse;
    console.log('✅ [SEND MESSAGE] Success:', data);
    if (data.llm_analysis) {
      console.log('🧠 [LLM] analysis:', data.llm_analysis);
    }
    return data;
  }

  static async getSessionMessages(sessionId: number) {
    console.log('📨 [GET MESSAGES] Request:', { session_id: sessionId });
    
    const response = await fetch(`${API_BASE_URL}/session/${sessionId}/messages/`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    console.log('📥 [GET MESSAGES] Response status:', response.status);

    if (!response.ok) {
      console.error('❌ [GET MESSAGES] Error');
      throw new Error('Error al obtener mensajes');
    }

    const data = await response.json();
    console.log('✅ [GET MESSAGES] Success:', data);
    return data;
  }
}
