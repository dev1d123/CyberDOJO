export interface UserDto {
  user_id: number;
  username: string;
  email: string;
  avatar?: string | null;
  country?: number | null;
  pet_id?: number | null;
  cybercreds?: number;
  is_active?: boolean;
  date_joined?: string;
  preferences?: UserPreferencesDto;
}

export interface TokensDto {
  access: string;
  refresh: string;
}

export interface UpdateMeResponseDto {
  message: string;
  user: UserDto;
  tokens: TokensDto;
}

export interface UserPreferencesDto {
  preference_id?: number;
  receive_newsletters: boolean;
  dark_mode?: boolean;
  base_content?: string | null;
  tone_instructions?: string | null;
  age?: number | null;
  // Compat legacy (no usado por backend actual)
  theme?: string;
}

export interface UpdateUserDto {
  username?: string;
  avatar?: string;
  country?: number;
}

export interface UpdatePreferencesDto {
  receive_newsletters?: boolean;
  dark_mode?: boolean;
  base_content?: string | null;
  tone_instructions?: string | null;
  age?: number | null;
  // Compat legacy
  theme?: string;
}

// Para el setup inicial del perfil
export interface ProfileSetupDto {
  username: string;
  country: number | '';
  avatar?: string;
}
