export interface UserDto {
  user_id: number;
  username: string;
  email: string;
  avatar?: string | null;
  country?: string | null;
  cybercreds?: number;
  is_active?: boolean;
  date_joined?: string;
  preferences?: UserPreferencesDto;
}

export interface UserPreferencesDto {
  preference_id?: number;
  receive_newsletters: boolean;
  theme?: string;
}

export interface UpdateUserDto {
  username?: string;
  avatar?: string;
  country?: string;
}

export interface UpdatePreferencesDto {
  receive_newsletters?: boolean;
  theme?: string;
}

// Para el setup inicial del perfil
export interface ProfileSetupDto {
  username: string;
  country: string;
  avatar?: string;
}
