// Service for simulation/game session API calls

const API_BASE_URL = 'https://juliojc.pythonanywhere.com/api/simulation';

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
  antagonist_attempts: number;
  is_game_over: boolean | null;
  outcome: string | null;
  game_over_reason: string | null;
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

  static async resumeSession(): Promise<ResumeSessionResponse> {
    console.log('🔄 [RESUME SESSION] Request');
    
    const response = await fetch(`${API_BASE_URL}/session/resume/`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    console.log('📥 [RESUME SESSION] Response status:', response.status);

    if (!response.ok) {
      const error = await response.json();
      console.error('❌ [RESUME SESSION] Error:', error);
      throw new Error(error.error || 'No hay sesión activa');
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

    if (!response.ok) {
      const error = await response.json();
      console.error('❌ [SEND MESSAGE] Error:', error);
      throw new Error(error.error || 'Error al enviar mensaje');
    }

    const data = await response.json();
    console.log('✅ [SEND MESSAGE] Success:', data);
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
