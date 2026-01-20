import axios from 'axios';
import type { CountryDto } from '../dto/country.dto';

import { API_CONFIG } from '../config/api.config';

const API_BASE_URL = API_CONFIG.BASE_URL;

type PaginatedResponse<T> = {
  count?: number;
  next?: string | null;
  previous?: string | null;
  results?: T[];
};

class CountryServiceClass {
  /**
   * Obtiene todos los países disponibles
   */
  async getAllCountries(): Promise<CountryDto[]> {
    try {
      console.log('🌎 Obteniendo países del backend...');

      const endpoint = '/users/countries/';
      let url: string | null = `${API_BASE_URL}${endpoint}`;
      const allCountries: CountryDto[] = [];

      while (url) {
        console.log('📤 Countries request:', { url });

        const response = await axios.get<CountryDto[] | PaginatedResponse<CountryDto>>(url);
        console.log('📥 Countries response:', {
          status: response.status,
          statusText: response.statusText,
          data: response.data,
        });

        if (Array.isArray(response.data)) {
          return response.data;
        }

        const data = response.data as PaginatedResponse<CountryDto>;
        if (Array.isArray(data.results)) {
          allCountries.push(...data.results);
        }

        if (data.next) {
          url = data.next.startsWith('http') ? data.next : `${API_BASE_URL}${data.next}`;
        } else {
          url = null;
        }
      }

      if (allCountries.length > 0) {
        return allCountries;
      }

      console.log('⚠️ Countries endpoint respondió sin resultados, usando lista por defecto');
      return this.getDefaultCountries();
      
    } catch (error: any) {
      console.error('❌ Error obteniendo países:', error);
      return this.getDefaultCountries();
    }
  }

  /**
   * Países por defecto si no hay endpoint
   */
  private getDefaultCountries(): CountryDto[] {
    return [
      { country_id: 1, name: 'Argentina', iso_code: 'AR', language: 'Español', is_active: true },
      { country_id: 2, name: 'Bolivia', iso_code: 'BO', language: 'Español', is_active: true },
      { country_id: 3, name: 'Chile', iso_code: 'CL', language: 'Español', is_active: true },
      { country_id: 4, name: 'Colombia', iso_code: 'CO', language: 'Español', is_active: true },
      { country_id: 5, name: 'Costa Rica', iso_code: 'CR', language: 'Español', is_active: true },
      { country_id: 6, name: 'Cuba', iso_code: 'CU', language: 'Español', is_active: true },
      { country_id: 7, name: 'Ecuador', iso_code: 'EC', language: 'Español', is_active: true },
      { country_id: 8, name: 'El Salvador', iso_code: 'SV', language: 'Español', is_active: true },
      { country_id: 9, name: 'España', iso_code: 'ES', language: 'Español', is_active: true },
      { country_id: 10, name: 'Guatemala', iso_code: 'GT', language: 'Español', is_active: true },
      { country_id: 11, name: 'Honduras', iso_code: 'HN', language: 'Español', is_active: true },
      { country_id: 12, name: 'México', iso_code: 'MX', language: 'Español', is_active: true },
      { country_id: 13, name: 'Nicaragua', iso_code: 'NI', language: 'Español', is_active: true },
      { country_id: 14, name: 'Panamá', iso_code: 'PA', language: 'Español', is_active: true },
      { country_id: 15, name: 'Paraguay', iso_code: 'PY', language: 'Español', is_active: true },
      { country_id: 16, name: 'Perú', iso_code: 'PE', language: 'Español', is_active: true },
      { country_id: 17, name: 'República Dominicana', iso_code: 'DO', language: 'Español', is_active: true },
      { country_id: 18, name: 'Uruguay', iso_code: 'UY', language: 'Español', is_active: true },
      { country_id: 19, name: 'Venezuela', iso_code: 'VE', language: 'Español', is_active: true },
    ];
  }
}

export const CountryService = new CountryServiceClass();
