import type { UserDto, UpdateUserDto, UpdateMeResponseDto, UpdatePreferencesDto } from '../dto/user.dto';

const API_BASE_URL = 'https://juliojc.pythonanywhere.com/api/users';

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
      const response = await fetch(`https://juliojc.pythonanywhere.com/api/onboarding/responses/my-status/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        // Backend devuelve: { is_complete, answered_questions, total_questions, ... }
        const isComplete = Boolean((data as any)?.is_complete);
        const answered = Number((data as any)?.answered_questions ?? 0);
        return { completed: isComplete, has_responses: answered > 0 };
      }
    } catch {
      // fallback below
    }

    // Fallback legacy: status/<user_id>/ (mapea is_complete -> completed)
    const legacyResponse = await fetch(`https://juliojc.pythonanywhere.com/api/onboarding/responses/status/${userId}/`, {
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
    const legacyIsComplete = Boolean((legacyData as any)?.is_complete);
    const legacyAnswered = Number((legacyData as any)?.answered_questions ?? 0);
    return { completed: legacyIsComplete, has_responses: legacyAnswered > 0 };
  }
}
