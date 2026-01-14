// Script para poblar países de habla hispana en el backend
const API_BASE_URL = 'https://juliojc.pythonanywhere.com/api';

const SPANISH_SPEAKING_COUNTRIES = [
  { name: 'Argentina', iso_code: 'AR', language: 'Español' },
  { name: 'Bolivia', iso_code: 'BO', language: 'Español' },
  { name: 'Chile', iso_code: 'CL', language: 'Español' },
  { name: 'Colombia', iso_code: 'CO', language: 'Español' },
  { name: 'Costa Rica', iso_code: 'CR', language: 'Español' },
  { name: 'Cuba', iso_code: 'CU', language: 'Español' },
  { name: 'Ecuador', iso_code: 'EC', language: 'Español' },
  { name: 'El Salvador', iso_code: 'SV', language: 'Español' },
  { name: 'España', iso_code: 'ES', language: 'Español' },
  { name: 'Guatemala', iso_code: 'GT', language: 'Español' },
  { name: 'Honduras', iso_code: 'HN', language: 'Español' },
  { name: 'México', iso_code: 'MX', language: 'Español' },
  { name: 'Nicaragua', iso_code: 'NI', language: 'Español' },
  { name: 'Panamá', iso_code: 'PA', language: 'Español' },
  { name: 'Paraguay', iso_code: 'PY', language: 'Español' },
  { name: 'Perú', iso_code: 'PE', language: 'Español' },
  { name: 'República Dominicana', iso_code: 'DO', language: 'Español' },
  { name: 'Uruguay', iso_code: 'UY', language: 'Español' },
  { name: 'Venezuela', iso_code: 'VE', language: 'Español' },
];

async function getToken(email, password) {
  console.log('🔑 Obteniendo token de autenticación...');
  
  try {
    const response = await fetch(`${API_BASE_URL}/users/auth/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      throw new Error(`Error al autenticar: ${response.status}`);
    }

    const data = await response.json();
    console.log('✅ Token obtenido');
    return data.access;
  } catch (error) {
    console.error('❌ Error obteniendo token:', error.message);
    throw error;
  }
}

async function createCountry(token, country) {
  try {
    const response = await fetch(`${API_BASE_URL}/countries/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: country.name,
        iso_code: country.iso_code,
        language: country.language,
        is_active: true,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`${response.status}: ${error}`);
    }

    const data = await response.json();
    console.log(`✅ País creado: ${country.name} (ID: ${data.country_id})`);
    return data;
  } catch (error) {
    console.error(`❌ Error creando ${country.name}:`, error.message);
    return null;
  }
}

async function getAllCountries() {
  try {
    const response = await fetch(`${API_BASE_URL}/countries/`);
    if (response.ok) {
      return await response.json();
    }
    return [];
  } catch (error) {
    return [];
  }
}

async function populateCountries() {
  console.log('🌎 Iniciando población de países de habla hispana...\n');

  // Primero verificar si ya existen países
  console.log('📋 Verificando países existentes...');
  const existingCountries = await getAllCountries();
  console.log(`Países existentes: ${existingCountries.length}`);

  // Pedir credenciales si es necesario crear países
  const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout
  });

  readline.question('Email de admin: ', async (email) => {
    readline.question('Password: ', async (password) => {
      readline.close();

      try {
        // Obtener token
        const token = await getToken(email, password);

        console.log('\n📝 Creando países...\n');
        
        let created = 0;
        let failed = 0;

        for (const country of SPANISH_SPEAKING_COUNTRIES) {
          const result = await createCountry(token, country);
          if (result) {
            created++;
          } else {
            failed++;
          }
          // Pequeña pausa entre requests
          await new Promise(resolve => setTimeout(resolve, 200));
        }

        console.log('\n📊 RESUMEN:');
        console.log(`✅ Países creados exitosamente: ${created}`);
        if (failed > 0) {
          console.log(`❌ Países que fallaron: ${failed}`);
        }
        console.log('\n✅ Proceso completado!');

      } catch (error) {
        console.error('❌ Error en el proceso:', error.message);
        process.exit(1);
      }
    });
  });
}

populateCountries();

