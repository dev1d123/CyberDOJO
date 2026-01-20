import type { 
  CosmeticItem, 
  BuyCosmeticResponse, 
  EquipCosmeticResponse,
  MyPurchasesResponse 
} from '../dto/cosmetic.dto';

import { API_CONFIG } from '../config/api.config';

const API_BASE_URL = API_CONFIG.BASE_URL;

export class CosmeticService {
  // Obtener todos los items cosméticos de la tienda
  static async getShopCosmetics(): Promise<CosmeticItem[]> {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      throw new Error('No hay token de acceso');
    }

    const response = await fetch(`${API_BASE_URL}/progression/cosmetics/shop/`, {
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

  // Obtener items cosméticos por tipo (effect, avatar, frame, background)
  static async getCosmeticsByType(type: string): Promise<CosmeticItem[]> {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      throw new Error('No hay token de acceso');
    }

    const response = await fetch(`${API_BASE_URL}/progression/cosmetics/?type=${type}`, {
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

  // Obtener el inventario del usuario
  static async getMyPurchases(): Promise<MyPurchasesResponse> {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      throw new Error('No hay token de acceso');
    }

    const response = await fetch(`${API_BASE_URL}/progression/shop/my-purchases/`, {
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

  // Comprar un item cosmético
  static async buyCosmetic(itemId: number): Promise<BuyCosmeticResponse> {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      throw new Error('No hay token de acceso');
    }

    const response = await fetch(`${API_BASE_URL}/progression/shop/buy-cosmetic/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ item_id: itemId }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw error;
    }

    return await response.json();
  }

  // Equipar un item cosmético
  static async equipCosmetic(itemId: number): Promise<EquipCosmeticResponse> {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      throw new Error('No hay token de acceso');
    }

    const response = await fetch(`${API_BASE_URL}/progression/shop/equip-cosmetic/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ item_id: itemId }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw error;
    }

    return await response.json();
  }
}
