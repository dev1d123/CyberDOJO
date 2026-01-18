# API de Simulación - Ejemplos de Uso

## 1. Crear un Nuevo Escenario

**Endpoint:** `POST /api/simulation/scenarios/`

**Permisos:** Solo administradores

**Request Body:**
```json
{
  "name": "Phishing por WhatsApp",
  "description": "Un desconocido te contacta ofreciendo premios gratuitos",
  "antagonist_goal": "número de teléfono",
  "difficulty_level": 2,
  "base_points": 150,
  "threat_type": "phishing",
  "is_active": true
}
```

**Response:**
```json
{
  "scenario_id": 5,
  "name": "Phishing por WhatsApp",
  "description": "Un desconocido te contacta ofreciendo premios gratuitos",
  "antagonist_goal": "número de teléfono",
  "difficulty_level": 2,
  "base_points": 150,
  "threat_type": "phishing",
  "is_active": true
}
```

## 2. Listar Escenarios Disponibles

**Endpoint:** `GET /api/simulation/scenarios/`

**Permisos:** Público

**Response:**
```json
[
  {
    "scenario_id": 1,
    "name": "Robo de Identidad",
    "description": "...",
    "antagonist_goal": "correo electrónico",
    "difficulty_level": 1,
    "base_points": 100,
    "threat_type": "social_engineering",
    "is_active": true
  },
  ...
]
```

## 3. Iniciar Sesión con Escenario Específico

**Endpoint:** `POST /api/simulation/session/start-role/`

**Permisos:** Usuario autenticado

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Request Body (con escenario específico):**
```json
{
  "scenario_id": 3
}
```

**Request Body (selección automática):**
```json
{}
```

**Response:**
```json
{
  "session_id": 42,
  "initial_message": "¡Hola! ¿Cómo estás hoy?",
  "resumed": false
}
```

## 4. Actualizar un Escenario

**Endpoint:** `PATCH /api/simulation/scenarios/{scenario_id}/`

**Permisos:** Solo administradores

**Request Body:**
```json
{
  "base_points": 200,
  "is_active": false
}
```

## 5. Eliminar un Escenario

**Endpoint:** `DELETE /api/simulation/scenarios/{scenario_id}/`

**Permisos:** Solo administradores

**Response:** `204 No Content`

## 6. Obtener Escenarios Agrupados por Dificultad

**Endpoint:** `GET /api/simulation/scenarios/by_difficulty/`

**Permisos:** Público

**Response:**
```json
{
  "level_1": [
    {"scenario_id": 1, "name": "...", ...}
  ],
  "level_2": [
    {"scenario_id": 2, "name": "...", ...}
  ],
  "level_3": [
    {"scenario_id": 3, "name": "...", ...}
  ]
}
```

## 7. Chat con el Antagonista

**Endpoint:** `POST /api/simulation/chat/`

**Permisos:** Usuario autenticado

**Request Body:**
```json
{
  "session_id": 42,
  "message": "Hola, ¿quién eres?"
}
```

**Response:**
```json
{
  "reply": "Soy María, trabajo en el equipo de soporte técnico. ¿Tienes algún problema?",
  "session_id": 42,
  "disclosure": false,
  "disclosure_reason": null,
  "antagonist_attempts": 0,
  "is_game_over": null,
  "outcome": null,
  "game_over_reason": null
}
```

## Errores Comunes

### Error 401: Authentication Required
```json
{
  "error": "authentication_required"
}
```
**Solución:** Incluir token JWT válido en el header Authorization.

### Error 404: Scenario Not Found
```json
{
  "error": "scenario_not_found",
  "message": "Escenario 99 no existe o no está activo"
}
```
**Solución:** Verificar que el scenario_id existe y está activo.

### Error 403: Permission Denied
```json
{
  "detail": "You do not have permission to perform this action."
}
```
**Solución:** Solo administradores pueden crear/editar/eliminar escenarios.
