import type { OnboardingQuestion, OnboardingResponse, OnboardingResponseRecord, UserAnswer } from '@/dto/onboarding.dto';

import { API_CONFIG } from '../config/api.config';

const API_BASE_URL = API_CONFIG.BASE_URL;

function normalizeListResponse<T>(body: unknown): T[] {
  if (Array.isArray(body)) return body as T[];
  if (body && typeof body === 'object') {
    const maybeResults = (body as any).results;
    if (Array.isArray(maybeResults)) return maybeResults as T[];
  }
  return [];
}

export class OnboardingService {
  /**
   * Obtiene todas las preguntas de onboarding (incluye inactivas).
   */
  static async getAllQuestions(): Promise<OnboardingQuestion[]> {
    const response = await fetch(`${API_BASE_URL}/onboarding/questions/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Error al obtener preguntas: ${response.status}`);
    }

    const body = await response.json();
    const questions = normalizeListResponse<OnboardingQuestion>(body);
    return questions.sort((a, b) => (a.display_order ?? 0) - (b.display_order ?? 0));
  }

  /**
   * Obtiene las preguntas activas de onboarding
   */
  static async getActiveQuestions(): Promise<OnboardingQuestion[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/onboarding/questions/active/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Error al obtener preguntas: ${response.status}`);
      }

      const body = await response.json();
      const questions = normalizeListResponse<OnboardingQuestion>(body);
      // Ordenar por display_order para asegurar el orden correcto
      return questions.sort((a, b) => a.display_order - b.display_order);
    } catch (error) {
      console.error('Error en getActiveQuestions:', error);
      throw error;
    }
  }

  /**
   * Obtiene las respuestas del usuario autenticado.
   * Backend: GET /api/onboarding/responses/my-responses/
   */
  static async getMyResponses(): Promise<OnboardingResponseRecord[]> {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('No hay token de acceso');
    }

    const response = await fetch(`${API_BASE_URL}/onboarding/responses/my-responses/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
    });

    const contentType = response.headers.get('content-type') || '';
    const body = contentType.includes('application/json') ? await response.json() : await response.text();

    if (!response.ok) {
      throw new Error(typeof body === 'string' ? body : JSON.stringify(body));
    }

    return body as OnboardingResponseRecord[];
  }

  /**
   * Envía una respuesta de onboarding
   */
  static async submitResponse(response: OnboardingResponse): Promise<unknown> {
    try {
      const token = localStorage.getItem('access_token');

      // ⚠️ IMPORTANTE: el endpoint /responses/ (POST) crea y falla si ya existe
      // El backend expone /responses/submit/ que hace update_or_create usando request.user
      const payload = {
        question_id: response.question,
        option_id: response.option,
        open_answer: response.open_answer,
      };

      console.log('📤 OnboardingService.submitResponse payload:', payload);
      
      const result = await fetch(`${API_BASE_URL}/onboarding/responses/submit/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      console.log('📥 OnboardingService.submitResponse status:', result.status);

      const contentType = result.headers.get('content-type') || '';
      const body = contentType.includes('application/json') ? await result.json() : await result.text();
      console.log('📥 OnboardingService.submitResponse body:', body);

      if (!result.ok) {
        throw new Error(typeof body === 'string' ? body : JSON.stringify(body));
      }

      return body;
    } catch (error) {
      console.error('Error en submitResponse:', error);
      throw error;
    }
  }

  /**
   * Envía múltiples respuestas en lote (upsert) para el usuario autenticado.
   * Backend: POST /api/onboarding/responses/submit-batch/
   */
  static async submitBatch(
    responses: Array<{ question_id: number; option_id: number | null; open_answer?: string | null }>
  ): Promise<unknown> {
    const token = localStorage.getItem('access_token');
    if (!token) {
      throw new Error('No hay token de acceso');
    }

    const payload = { responses };
    console.log('📤 OnboardingService.submitBatch payload:', payload);

    const result = await fetch(`${API_BASE_URL}/onboarding/responses/submit-batch/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });

    console.log('📥 OnboardingService.submitBatch status:', result.status);

    const contentType = result.headers.get('content-type') || '';
    const body = contentType.includes('application/json') ? await result.json() : await result.text();
    console.log('📥 OnboardingService.submitBatch body:', body);

    if (!result.ok) {
      throw new Error(typeof body === 'string' ? body : JSON.stringify(body));
    }

    return body;
  }

  /**
   * Calcula el nivel de riesgo basado en las respuestas
   */
  static calculateRiskLevel(answers: UserAnswer[]): {
    total_risk_score: number;
    risk_level: 'low' | 'medium' | 'high' | 'critical';
    recommendations: string[];
  } {
    // Calcular score ponderado
    const total_risk_score = answers.reduce((sum, answer) => {
      return sum + (answer.risk_value * answer.risk_weight);
    }, 0);

    // Calcular score máximo posible
    const max_possible_score = answers.reduce((sum, answer) => {
      return sum + (5 * answer.risk_weight); // 5 es el risk_value máximo
    }, 0);

    // Calcular porcentaje de riesgo
    const risk_percentage = (total_risk_score / max_possible_score) * 100;

    // Determinar nivel de riesgo
    let risk_level: 'low' | 'medium' | 'high' | 'critical';
    let recommendations: string[];

    if (risk_percentage < 25) {
      risk_level = 'low';
      recommendations = [
        '¡Excelente! Tienes muy buenos hábitos de seguridad en línea.',
        'Sigue siendo cuidadoso con la información que compartes.',
        'Recuerda siempre hablar con un adulto de confianza si algo te incomoda.'
      ];
    } else if (risk_percentage < 50) {
      risk_level = 'medium';
      recommendations = [
        'Tienes buenos hábitos, pero hay áreas donde puedes mejorar.',
        'Evita aceptar solicitudes de amistad de personas desconocidas.',
        'Nunca compartas información personal como tu dirección o número de teléfono.',
        'Si alguien te hace sentir incómodo, bloquéalo y avisa a un adulto.'
      ];
    } else if (risk_percentage < 75) {
      risk_level = 'high';
      recommendations = [
        'Es importante que mejores tus hábitos de seguridad en línea.',
        'NUNCA compartas información personal con desconocidos en internet.',
        'No aceptes reunirte en persona con alguien que conociste en línea.',
        'Habla con tus padres o maestros sobre seguridad en internet.',
        'Bloquea y reporta a cualquier persona que te haga sentir incómodo.'
      ];
    } else {
      risk_level = 'critical';
      recommendations = [
        '⚠️ NECESITAS AYUDA URGENTE - Habla con un adulto de confianza AHORA.',
        'Tus respuestas indican que podrías estar en situación de riesgo.',
        'NUNCA te reúnas con personas que conociste en internet.',
        'NUNCA envíes fotos o videos personales a desconocidos.',
        'Si alguien te ha pedido hacer algo que te hace sentir mal, cuéntale a un adulto.',
        'Recuerda: los adultos responsables NUNCA te pedirán guardar secretos.'
      ];
    }

    return {
      total_risk_score: Math.round(risk_percentage),
      risk_level,
      recommendations
    };
  }
}
