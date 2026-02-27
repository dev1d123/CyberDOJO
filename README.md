# 🥷 CyberDOJO

> Practica, juega e interactúa mientras aprendes a detectar situaciones peligrosas.
> **HackOdiseia4Good** · Plataforma gamificada de educación en ciberseguridad para menores.

[![Demo](https://img.shields.io/badge/Demo%20en%20vivo-cyber--dojo--flame.vercel.app-blue?style=for-the-badge&logo=vercel)](https://cyber-dojo-flame.vercel.app)
[![Backend](https://img.shields.io/badge/Backend%20API-Railway-purple?style=for-the-badge&logo=railway)](https://cyberdojo-production.up.railway.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Vue 3](https://img.shields.io/badge/Vue-3.x-42b883?style=for-the-badge&logo=vue.js)](https://vuejs.org)
[![Django](https://img.shields.io/badge/Django-4.x-092e20?style=for-the-badge&logo=django)](https://djangoproject.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776ab?style=for-the-badge&logo=python)](https://python.org)

---

## Tabla de contenidos

1. [¿Qué es CyberDOJO?](#-qué-es-cyberdojo)
2. [Demo y URLs de producción](#-demo-y-urls-de-producción)
3. [Stack tecnológico](#-stack-tecnológico)
4. [Estructura del proyecto](#-estructura-del-proyecto)
5. [Escenarios de simulación](#-escenarios-de-simulación)
6. [API Reference](#-api-reference)
7. [Instalación y desarrollo local](#-instalación-y-desarrollo-local)
8. [Variables de entorno](#-variables-de-entorno)
9. [Arquitectura del sistema](#-arquitectura-del-sistema)
10. [Modelo económico (Unit Economics)](#-modelo-económico-unit-economics)
11. [Roadmap](#-roadmap)
12. [Contribución](#-contribución)
13. [Solución de problemas frecuentes](#-solución-de-problemas-frecuentes)
14. [Licencia](#-licencia)

---

## 🎯 ¿Qué es CyberDOJO?

CyberDOJO es una **plataforma educativa gamificada** diseñada para niños y adolescentes de **6 a 12 años** que aprenden a identificar y resistir amenazas digitales de forma segura y divertida.

- **IA conversacional**: utiliza OpenRouter con modelos Bytedance Seed 1.6 Flash y Google Gemini 2.5 Flash para generar antagonistas que simulan ataques reales de ingeniería social.
- **Práctica activa**: el usuario practica cómo resistir ataques de **ingeniería social, phishing, grooming y suplantación de identidad** sin exponerse a riesgos reales.
- **Sistema de gamificación completo**: puntos, mascotas virtuales, tienda de objetos, logros desbloqueables y mapa de islas temáticas.
- **Onboarding personalizado**: evaluación inicial de riesgo que adapta la dificultad al perfil del usuario.

---

## 🌐 Demo y URLs de producción

| Servicio | URL |
|---|---|
| 🌐 Frontend (Demo) | https://cyber-dojo-flame.vercel.app |
| ⚙️ Backend API | https://cyberdojo-production.up.railway.app |
| 📋 Django Admin | https://cyberdojo-production.up.railway.app/admin/ |

---

## 🛠 Stack tecnológico

| Capa | Tecnología | Descripción |
|---|---|---|
| Frontend | Vue 3 + TypeScript + Vite | SPA, desplegada en Vercel |
| Backend | Django 4 + DRF + Gunicorn | API REST, desplegada en Railway |
| Base de datos | PostgreSQL (Railway Managed) | Conexión SSL, `dj-database-url` |
| IA | OpenRouter (Bytedance / Gemini 2.5) | Antagonistas conversacionales |
| Media | Cloudinary | Avatares, mascotas, recursos gráficos |
| Hosting backend | Railway | `cyberdojo-production.up.railway.app` |
| Hosting frontend | Vercel | CDN global, capa gratuita |

---

## 📁 Estructura del proyecto

```
CyberDOJO/
├── backend/
│   └── cyberkids/
│       ├── apps/
│       │   ├── simulation/      # Simulación con IA (GameSession, ChatMessage, SensitivePattern)
│       │   ├── quiz/            # Quiz educativo (AudienceSegment, RiskCategory)
│       │   ├── cyberUser/       # Usuarios y autenticación JWT
│       │   ├── pets/            # Mascotas virtuales
│       │   ├── progression/     # Puntos, tienda, logros
│       │   ├── onboarding/      # Evaluación inicial de riesgo
│       │   └── minigames/       # Minijuegos adicionales
│       ├── cyberkids/
│       │   ├── settings.py      # Configuración Django + Railway + Cloudinary
│       │   └── urls.py
│       └── requirements.txt
├── frontend/
│   └── cyberKids/
│       ├── src/
│       │   ├── config/
│       │   │   └── api.config.ts  # BASE_URL → Railway
│       │   ├── dto/               # Interfaces TypeScript
│       │   └── ...
│       ├── scripts/
│       │   └── populate-questions.js
│       ├── vite.config.ts
│       └── package.json
├── INTEGRATION_DOCS.md
└── README.md
```

---

## 🎮 Escenarios de simulación

| # | Escenario | Objetivo del antagonista | Dificultad | Puntos base |
|---|---|---|---|---|
| 1 | Ingeniería Social | Número de teléfono | ⭐ | 180 |
| 2 | Suplantación Digital | Correo / contraseña | ⭐⭐ | 220 |
| 3 | Fuga de Datos | Dirección o datos personales | ⭐⭐⭐ | 240 |
| 4 | Pretextos Falsos | Nombre completo y edad | ⭐⭐⭐⭐ | 200 |
| 5 | Trampas Digitales | Credenciales de cuenta | ⭐⭐⭐⭐⭐ | 280 |
| 6 | Suplantación de Identidad | Usuario y contraseña | ⭐⭐⭐⭐⭐⭐ | 300 |

Cada partida tiene un **límite estricto de 12 mensajes** gestionado por el backend. El usuario gana si resiste 3 intentos del antagonista sin revelar datos sensibles.

---

## 📡 API Reference

### Autenticación

Todos los endpoints protegidos requieren `Authorization: Bearer <token>`.

### Simulación

```
POST /api/simulation/session/start-role/
Body:     { "scenario_id": 1 }
Response: { "session_id": 42, "initial_message": "...", "resumed": false }

GET /api/simulation/session/resume/
Response: { "session_id": 42, "messages": [...], "resumed": true }

POST /api/simulation/chat/
Body:     { "session_id": 42, "message": "Hola" }
Response: {
  "reply": "...",
  "session_id": 42,
  "disclosure": false,
  "antagonist_attempts": 1,
  "is_game_over": null,
  "outcome": null
}

GET /api/simulation/scenarios/
GET /api/simulation/scenarios/by_difficulty/
```

### Otros módulos

```
GET/POST  /api/quiz/
GET/POST  /api/onboarding/
GET/POST  /api/users/
GET/POST  /api/pets/
GET/POST  /api/progression/
```

---

## 🚀 Instalación y desarrollo local

### Requisitos previos

- Python 3.10+
- Node.js 18+
- Git

### Backend (Django)

```bash
# 1. Clonar el repositorio
git clone https://github.com/dev1d123/CyberDOJO.git
cd CyberDOJO/backend/cyberkids

# 2. Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno (ver sección Variables de entorno)
cp .env.example .env            # editar con tus valores

# 5. Ejecutar migraciones
python manage.py migrate

# 6. Cargar datos iniciales (escenarios + onboarding)
python manage.py populate_scenarios
python manage.py seed_initial_data

# 7. Levantar servidor de desarrollo
python manage.py runserver
```

### Frontend (Vue 3)

```bash
cd CyberDOJO/frontend/cyberKids

# 1. Instalar dependencias
npm install

# 2. Configurar variable de entorno (opcional, por defecto apunta a Railway)
# Crear .env.local con:
# VITE_API_BASE_URL=http://localhost:8000/api

# 3. Servidor de desarrollo
npm run dev

# 4. Build de producción
npm run build

# 5. Previsualización del build
npm run preview
```

### Poblar preguntas de onboarding (script frontend)

```bash
cd frontend/cyberKids
node scripts/populate-questions.js
```

---

## 🔑 Variables de entorno

### Backend (`backend/cyberkids/.env`)

| Variable | Descripción | Requerida |
|---|---|---|
| `GEMINI_API_KEY` | API Key de Google Gemini / OpenRouter | ✅ Sí |
| `DATABASE_URL` | URL de conexión PostgreSQL (Railway la inyecta automáticamente) | ✅ Producción |
| `SECRET_KEY` | Django secret key (cambiar en producción) | ✅ Sí |
| `CLOUDINARY_CLOUD_NAME` | Nombre del cloud en Cloudinary | ✅ Sí |
| `CLOUDINARY_API_KEY` | API Key de Cloudinary | ✅ Sí |
| `CLOUDINARY_API_SECRET` | API Secret de Cloudinary | ✅ Sí |

> Consulta [`backend/cyberkids/README_GEMINI_ENV.md`](backend/cyberkids/README_GEMINI_ENV.md) para instrucciones detalladas.

### Frontend (`frontend/cyberKids/.env.local`)

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `VITE_API_BASE_URL` | URL base del backend | `https://cyberdojo-production.up.railway.app/api` |

---

## 🏗 Arquitectura del sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                     USUARIO (Navegador)                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS
┌──────────────────────────▼──────────────────────────────────────┐
│              VERCEL — CDN Global (Frontend)                     │
│         Vue 3 + TypeScript + Vite  ·  cyber-dojo-flame.vercel.app│
└──────────────┬──────────────────────────────┬───────────────────┘
               │ REST API (JWT)               │ POST /llm/chat
               │                             │
┌──────────────▼──────────────┐  ┌───────────▼───────────────────┐
│  RAILWAY — Backend Django   │  │  VERCEL — LLM API Serverless  │
│  cyberdojo-production       │  │  (timeout: 10-15s plan free)  │
│  .up.railway.app            │  └───────────┬───────────────────┘
│                             │              │
│  ┌─────────────────────┐    │  ┌───────────▼───────────────────┐
│  │ apps/simulation     │    │  │      OPENROUTER API           │
│  │ apps/quiz           │    │  │  ┌────────────────────────┐   │
│  │ apps/cyberUser      │    │  │  │ Bytedance Seed 1.6 Flash│   │
│  │ apps/pets           │    │  │  │ (Gratuito: $0.0036/par.)│   │
│  │ apps/onboarding     │    │  │  ├────────────────────────┤   │
│  │ apps/progression    │    │  │  │ Google Gemini 2.5 Flash │   │
│  └─────────────────────┘    │  │  │ (Premium: $0.019/par.)  │   │
│                             │  │  └────────────────────────┘   │
│  ┌─────────────────────┐    │  └───────────────────────────────┘
│  │ PostgreSQL (Railway)│    │
│  │ SSL required        │    │  ┌───────────────────────────────┐
│  └─────────────────────┘    │  │    CLOUDINARY CDN             │
└─────────────────────────────┘  │    Avatares · Mascotas · Media│
                                 └───────────────────────────────┘
```

---

## 💰 Modelo económico (Unit Economics)

Datos reales de producción:

| Métrica | Valor |
|---|---|
| Límite de mensajes por partida | 12 mensajes |
| Tokens input promedio / petición | 2.200 tokens |
| Tokens output promedio / petición | 450 tokens |
| Infraestructura fija (Railway) | $5.00 USD/mes |
| **CPUM usuario gratuito** (20 partidas/mes) | **$0.077 USD** |
| **CPUM usuario premium** (50 partidas/mes) | **$0.955 USD** |
| Precio plan Pro | $4.99 USD/mes |
| **Margen bruto plan Pro** | **80.7%** |

> 1.000 usuarios gratuitos activos cuestan menos de **$80 USD/mes** en total.

---

## 🗺 Roadmap

```
✅ Fase 1 — MVP (Feb 2026)
   Simulación IA · Quiz · Onboarding · Mascotas · JWT · Railway + Vercel

🔄 Fase 2 — Monetización (Meses 1–3)
   Plan CyberDOJO Pro · Gemini 2.5 Flash · Panel para padres · Pasarela de pago

📋 Fase 3 — Institucional (Meses 4–8)
   Dashboard docentes · Seguimiento alumnos · Licencias B2B · Integración Moodle

🌍 Fase 4 — Escalado Global (Meses 9–18)
   Multiidioma · API pública · Acuerdos B2G (INCIBE, ENISA) · Nuevos escenarios
```

---

## 🤝 Contribución

```bash
# 1. Haz fork del repositorio
# 2. Crea una rama para tu cambio
git checkout -b feature/nombre-descriptivo

# 3. Realiza tus cambios y commitea
git commit -m "feat: descripción del cambio"

# 4. Verifica que el build funcione
cd backend/cyberkids && python manage.py test
cd frontend/cyberKids && npm run build

# 5. Abre un Pull Request describiendo el cambio
```

---

## 🛟 Solución de problemas frecuentes

| Error | Causa | Solución |
|---|---|---|
| `401 Unauthorized` en `/start-role/` | Token JWT ausente o expirado | Verificar `token` en `localStorage`; re-autenticarse |
| `Chat no responde` | API key de OpenRouter/Gemini inválida | Revisar `GEMINI_API_KEY` en variables de entorno del backend |
| `504 Gateway Timeout` | Respuesta de Gemini 2.5 supera 10s en Vercel serverless | Migrar microservicio LLM a Railway |
| `Error de conexión al API` | `VITE_API_BASE_URL` apunta a localhost en producción | Verificar variables de entorno en Vercel dashboard |
| `Escenarios no aparecen` | No se ejecutó `populate_scenarios` | Ejecutar `python manage.py populate_scenarios` |
| `fetch is not defined` (script onboarding) | Node.js < 18 | Actualizar a Node.js 18+ |

---

## 📄 Licencia

```
MIT License — Copyright (c) 2026 dev1d123 Team
```

Consulta el archivo [`LICENSE`](LICENSE) para el texto completo.
