# CyberDOJO

Plataforma educativa de ciberseguridad para niños con un backend en Django y un frontend en Vue 3.

## Demo

https://cyber-dojo-flame.vercel.app/

## Estructura

- backend/cyberkids: API y lógica de negocio (Django)
- frontend/cyberKids: aplicación web (Vue 3 + Vite + TypeScript)
- INTEGRATION_DOCS.md: documentación de integración
- USER_FLOW_SOCIAL.puml: diagramas de flujo

## Requisitos

- Node.js 18+
- Python 3.10+

## Configuración rápida

### Backend (Django)

1. Crear y activar entorno virtual.
2. Instalar dependencias.
3. Ejecutar migraciones.
4. Levantar el servidor.

Comandos sugeridos (desde backend/cyberkids):

- pip install -r requirements.txt
- python manage.py migrate
- python manage.py runserver

Consulta también backend/cyberkids/README_GEMINI_ENV.md para variables de entorno.

### Frontend (Vue 3)

1. Instalar dependencias.
2. Levantar el servidor de desarrollo.

Comandos sugeridos (desde frontend/cyberKids):

- npm install
- npm run dev

Para build de producción:

- npm run build

## Variables de entorno

Las variables de entorno específicas del backend se documentan en backend/cyberkids/README_GEMINI_ENV.md. Para cualquier integración adicional, revisa INTEGRATION_DOCS.md.

## Scripts útiles

Frontend:

- npm run dev: entorno de desarrollo
- npm run build: build de producción
- npm run preview: previsualización local del build

Backend:

- python manage.py runserver: servidor local
- python manage.py test: ejecutar tests

## Contribución

1. Crea una rama para tu cambio.
2. Incluye una descripción clara del objetivo.
3. Verifica que el build funcione en frontend y backend.

## Licencia

Consulta LICENSE.
