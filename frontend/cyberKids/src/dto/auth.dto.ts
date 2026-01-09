export interface RegisterDto {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
}

export interface LoginDto {
  username: string;
  password: string;
}

export interface AuthResponse {
  message?: string;
  user?: {
    id: number;
    username: string;
    email: string;
  };
  token?: string;
}

export interface ValidationErrors {
  username?: string[];
  email?: string[];
  password?: string[];
  password_confirm?: string[];
}
