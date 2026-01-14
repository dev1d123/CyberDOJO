import type { UserDto, UpdateUserDto, UpdatePreferencesDto } from '../dto/user.dto';

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

  // Actualizar usuario
  static async updateUser(userId: number, data: UpdateUserDto): Promise<UserDto> {
    const token = localStorage.getItem('access_token');
    
    console.log('🔧 UserService.updateUser called');
    console.log('👤 User ID:', userId);
    console.log('📦 Data to send:', data);
    
    if (!token) {
      throw new Error('No hay token de acceso');
    }

    const url = `${API_BASE_URL}/${userId}/`;
    console.log('🌐 URL:', url);
    console.log('🔑 Token:', token);

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
    return result;
  }

  // Actualizar preferencias de usuario
  static async updatePreferences(userId: number, data: UpdatePreferencesDto): Promise<UserDto> {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      throw new Error('No hay token de acceso');
    }

    // Las preferencias se actualizan junto con el usuario
    const response = await fetch(`${API_BASE_URL}/${userId}/`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ preferences: data }),
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

    const response = await fetch(`https://juliojc.pythonanywhere.com/api/onboarding/responses/status/${userId}/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      // Si falla, asumimos que no ha completado el onboarding
      return { completed: false, has_responses: false };
    }

    return await response.json();
  }
}
