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

export interface BuyPetResponse {
  message: string;
  user_pet: UserPet;
  cybercreds: number;
}

export interface EquipPetResponse {
  message: string;
  equipped_pet: UserPet;
}
