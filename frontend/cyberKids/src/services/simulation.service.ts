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
    const response = await fetch(`${API_BASE_URL}/session/start-role/`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ scenario_id: scenarioId }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al iniciar sesión');
    }

    return response.json();
  }

  static async resumeSession(): Promise<ResumeSessionResponse> {
    const response = await fetch(`${API_BASE_URL}/session/resume/`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'No hay sesión activa');
    }

    return response.json();
  }

  static async sendMessage(sessionId: number, message: string): Promise<ChatResponse> {
    const response = await fetch(`${API_BASE_URL}/chat/`, {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        session_id: sessionId,
        message: message,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error al enviar mensaje');
    }

    return response.json();
  }

  static async getSessionMessages(sessionId: number) {
    const response = await fetch(`${API_BASE_URL}/session/${sessionId}/messages/`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Error al obtener mensajes');
    }

    return response.json();
  }
}
