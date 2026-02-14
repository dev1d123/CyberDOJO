import type { RegisterDto, LoginDto, AuthResponse } from '../dto/auth.dto';

import { API_CONFIG } from '../config/api.config';

const API_BASE_URL = `${API_CONFIG.BASE_URL}/users/auth`;

export class AuthService {
  static async register(data: RegisterDto): Promise<AuthResponse> {
    console.log('📤 Register request data:', data);

    const response = await fetch(`${API_BASE_URL}/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    console.log('📥 Register response status:', response.status);

    if (!response.ok) {
      const error = await response.json();
      console.error('❌ Register error:', error);
      throw error;
    }

    const result = await response.json();
    console.log('✅ Register success response:', result);

    return result;
  }

  static async login(data: LoginDto): Promise<AuthResponse> {
    console.log('📤 Login request data:', data);

    const response = await fetch(`${API_BASE_URL}/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    console.log('📥 Login response status:', response.status);

    if (!response.ok) {
      const error = await response.json();
      console.error('❌ Login error:', error);
      throw error;
    }

    const result = await response.json();
    console.log('✅ Login success response:', result);

    return result;
  }

  static async refresh(refreshToken: string): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Error refrescando sesión' }));
      throw error;
    }

    return response.json();
  }
}
