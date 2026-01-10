export interface RegisterDto {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
}

export interface LoginDto {
  email: string;
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
  tokens?: {
    access: string;
    refresh: string;
  };
}

export interface ValidationErrors {
  username?: string[];
  email?: string[];
  password?: string[];
  password_confirm?: string[];
  non_field_errors?: string[];
  error?: string;
}
