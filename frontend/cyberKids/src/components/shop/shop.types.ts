export type ShopCategory = 'pets' | 'sounds';

export interface ShopItemBase {
  id: string;
  category: ShopCategory;
  name: string;
  description: string;
  price: number; // CyberCredits
}

export interface ShopPetItem extends ShopItemBase {
  category: 'pets';
  imageSrc: string;
  alt: string;
  petId?: number;
  isDefault?: boolean;
}

export type SoundTheme = 'normal' | 'fun' | 'retro' | 'epic';

export interface ShopSoundItem extends ShopItemBase {
  category: 'sounds';
  theme: SoundTheme;
}

export type ShopItem = ShopPetItem | ShopSoundItem;
