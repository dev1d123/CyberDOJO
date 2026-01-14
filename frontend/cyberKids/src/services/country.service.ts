import axios from 'axios';
import type { CountryDto } from '../dto/country.dto';

const API_BASE_URL = 'https://juliojc.pythonanywhere.com/api';

class CountryServiceClass {
  /**
   * Obtiene todos los países disponibles
   */
  async getAllCountries(): Promise<CountryDto[]> {
    try {
      console.log('🌎 Obteniendo países del backend...');
      
      // Intentamos obtener países desde diferentes posibles endpoints
      const possibleEndpoints = [
        '/countries/',
        '/users/countries/',
        '/cyberUser/countries/'
      ];

      for (const endpoint of possibleEndpoints) {
        try {
          const response = await axios.get(`${API_BASE_URL}${endpoint}`);
          console.log('✅ Países obtenidos:', response.data);
          return response.data;
        } catch (err) {
          console.log(`❌ Endpoint ${endpoint} no disponible`);
        }
      }

      // Si no hay endpoint, devolvemos países por defecto
      console.log('⚠️ No se encontró endpoint de países, usando lista por defecto');
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
