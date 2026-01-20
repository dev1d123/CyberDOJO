import type { UserDto, UpdateUserDto, UpdateMeResponseDto, UpdatePreferencesDto } from '../dto/user.dto';

import { API_CONFIG } from '../config/api.config';

const API_BASE_URL = `${API_CONFIG.BASE_URL}/users`;

export class UserService {
  // Obtener información del usuario autenticado
  static async getCurrentUser(): Promise<UserDto> {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      throw new Error('No hay token de acceso');
    }

    const response = await fetch(`${API_BASE_URL}/auth/me/`, {
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

  // Obtener usuario por ID
  static async getUserById(userId: number): Promise<UserDto> {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      throw new Error('No hay token de acceso');
    }

    const response = await fetch(`${API_BASE_URL}/${userId}/`, {
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

  // Actualizar el perfil del usuario autenticado
  static async updateMe(data: UpdateUserDto): Promise<UpdateMeResponseDto> {
    const token = localStorage.getItem('access_token');
    
    console.log('🔧 UserService.updateMe called');
    console.log('📦 Data to send:', data);
    
    if (!token) {
      throw new Error('No hay token de acceso');
    }

    const url = `${API_BASE_URL}/auth/me/update/`;
    console.log('🌐 URL:', url);

    const response = await fetch(url, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    console.log('📡 Response status:', response.status);
    
    if (!response.ok) {
      const error = await response.json();
      console.error('❌ Error response:', error);
      throw error;
    }

    const result = await response.json();
    console.log('✅ Success response:', result);
    return result as UpdateMeResponseDto;
  }

  // Actualizar usuario autenticado (multipart) - útil para subir avatar como archivo
  static async updateMeMultipart(data: {
    username?: string;
    country?: number;
    avatarFile?: File;
  }): Promise<UpdateMeResponseDto> {
    const token = localStorage.getItem('access_token');

    console.log('🔧 UserService.updateMeMultipart called');
    console.log('📦 Data to send (multipart):', {
      username: data.username,
      country: data.country,
      avatarFile: data.avatarFile
        ? { name: data.avatarFile.name, type: data.avatarFile.type, size: data.avatarFile.size }
        : null,
    });

    if (!token) {
      throw new Error('No hay token de acceso');
    }

    const url = `${API_BASE_URL}/auth/me/update/`;
    console.log('🌐 URL:', url);

    const form = new FormData();
    if (data.username != null) form.append('username', data.username);
    if (data.country != null) form.append('country', String(data.country));
    if (data.avatarFile) form.append('avatar', data.avatarFile);

    const response = await fetch(url, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        // No setear Content-Type; el browser agrega boundary
      },
      body: form,
    });

    console.log('📡 Response status:', response.status);

    const contentType = response.headers.get('content-type') || '';
    const responseBody = contentType.includes('application/json')
      ? await response.json()
      : await response.text();

    console.log('📥 Response body:', responseBody);

    if (!response.ok) {
      console.error('❌ Error response:', responseBody);
      throw responseBody;
    }

    return responseBody as UpdateMeResponseDto;
  }

  // Actualizar preferencias de usuario
  static async updatePreferences(data: UpdatePreferencesDto): Promise<{ message: string; preferences: unknown; tokens: { access: string; refresh: string } }> {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      throw new Error('No hay token de acceso');
    }

    const response = await fetch(`${API_BASE_URL}/auth/me/preferences/`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw error;
    }

    return await response.json();
  }

  // Obtener preferencias del usuario autenticado
  static async getPreferences(): Promise<unknown> {
    const token = localStorage.getItem('access_token');

    if (!token) {
      throw new Error('No hay token de acceso');
    }

    const response = await fetch(`${API_BASE_URL}/auth/me/preferences/`, {
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

  // Verificar si el usuario ya completó el onboarding
  static async checkOnboardingStatus(userId: number): Promise<{ completed: boolean; has_responses: boolean }> {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      throw new Error('No hay token de acceso');
    }

    // Preferir endpoint autenticado (no depende de userId y evita problemas de permisos)
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}/onboarding/responses/my-status/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        // Backend esperado: { is_complete, answered_questions, total_questions, ... }
        const rawComplete = (data as any)?.is_complete;
        const isComplete = rawComplete === true || rawComplete === 'true' || rawComplete === 1 || rawComplete === '1';
        const answeredRaw = (data as any)?.answered_questions;
        const answered = typeof answeredRaw === 'string' ? Number.parseInt(answeredRaw, 10) : Number(answeredRaw ?? 0);
        return { completed: Boolean(isComplete), has_responses: Number.isFinite(answered) && answered > 0 };
      }
    } catch {
      // fallback below
    }

    // Fallback legacy: status/<user_id>/ (mapea is_complete -> completed)
    const legacyResponse = await fetch(`${API_CONFIG.BASE_URL}/onboarding/responses/status/${userId}/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!legacyResponse.ok) {
      return { completed: false, has_responses: false };
    }

    const legacyData = await legacyResponse.json();
    const legacyRawComplete = (legacyData as any)?.is_complete;
    const legacyIsComplete = legacyRawComplete === true || legacyRawComplete === 'true' || legacyRawComplete === 1 || legacyRawComplete === '1';
    const legacyAnsweredRaw = (legacyData as any)?.answered_questions;
    const legacyAnswered = typeof legacyAnsweredRaw === 'string' ? Number.parseInt(legacyAnsweredRaw, 10) : Number(legacyAnsweredRaw ?? 0);
    return { completed: Boolean(legacyIsComplete), has_responses: Number.isFinite(legacyAnswered) && legacyAnswered > 0 };
  }
}
