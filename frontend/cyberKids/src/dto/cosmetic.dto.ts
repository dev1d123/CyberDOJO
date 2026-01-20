export interface CosmeticItem {
  item_id: number;
  name: string;
  type: string; // 'effect' para audios, 'avatar', 'frame', 'background'
  description: string;
  image: string | null;
  cybercreds_cost: number;
  required_level: number;
  is_active: boolean;
}

export interface UserInventory {
  inventory_id: number;
  user: number;
  item: number;
  acquired_at: string;
  is_equipped: boolean;
  item_name?: string;
  item_type?: string;
}

export interface BuyCosmeticResponse {
  message: string;
  inventory: UserInventory;
  remaining_cybercreds: number;
}

export interface EquipCosmeticResponse {
  message: string;
  inventory: UserInventory;
}

export interface MyPurchasesResponse {
  pets: any[];
  cosmetics: UserInventory[];
  cybercreds: number;
}
