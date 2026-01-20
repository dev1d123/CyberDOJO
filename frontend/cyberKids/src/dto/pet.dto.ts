export interface Pet {
  pet_id: number;
  name: string;
  description: string;
  base_sprite: string | null;
  cybercreds_cost: number;
  is_default: boolean;
  states: any[];
}

export interface UserPet {
  user_pet_id: number;
  user: number;
  pet: number;
  is_equipped: boolean;
  acquired_at: string;
}

export interface PaginatedResponse<T> {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results: T[];
}

export interface BuyPetResponse {
  message: string;
  user_pet: UserPet;
  remaining_cybercreds: number;
}

export interface EquipPetResponse {
  message: string;
  user_pet: UserPet;
}
