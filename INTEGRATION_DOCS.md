# Integración Frontend-Backend: Sistema de Simulación

## 🎯 Flujo Completo

### 1. Selección de Escenario (History Mode)
- Usuario navega a `/history`
- Ve 6 islas con los siguientes escenarios:
  1. Ingeniería Social
  2. Suplantación Digital
  3. Fuga de Datos
  4. Pretextos Falsos
  5. Trampas Digitales
  6. Suplantación de Identidad

### 2. Inicio de Sesión
- Usuario hace click en una isla
- Se muestra información del nivel en el panel inferior
- Al presionar "Acceder a este nivel":
  - Frontend llama a `POST /api/simulation/session/start-role/`
  - Backend crea GameSession con el scenario_id correspondiente
  - IA (Gemini) genera mensaje inicial
  - Usuario es redirigido a `/simulation/{scenario_id}`

### 3. Chat con Antagonista
**SimulationPage.vue** maneja:
- Inicialización de sesión
- Envío/recepción de mensajes
- Visualización del chat en tiempo real
- Contador de intentos del antagonista (máx 3)

**Cada mensaje del usuario:**
1. Se envía a `POST /api/simulation/chat/`
2. Backend procesa con IA
3. Detecta:
   - Si usuario reveló datos sensibles (`disclosure`)
   - Si antagonista intentó solicitar datos (`attempted`)
   - Estado del juego (`is_game_over`, `outcome`)
4. Responde con mensaje de IA y metadatos

### 4. Condiciones de Fin de Juego

**Usuario PIERDE** si:
- Revela información sensible
- `disclosure: true` detectado por IA o regex patterns
- `outcome: "failed"`
- `is_game_over: true`

**Usuario GANA** si:
- Resiste 3 intentos del antagonista sin revelar datos
- `antagonist_attempts >= 3` sin ningún `disclosure`
- `outcome: "won"`
- `is_game_over: false`
- Recibe puntos base del escenario

### 5. Game Over
- Overlay se muestra con resultado
- Opciones:
  - **Ganó**: Volver al mapa, ver puntos ganados
  - **Perdió**: Volver al mapa o reintentar nivel

---

## 📁 Archivos Clave

### Frontend
- **`SimulationService.ts`**: Llamadas API (start, resume, sendMessage)
- **`SimulationPage.vue`**: UI del chat y lógica de juego
- **`HistoryModePage.vue`**: Selección de islas y redirección
- **`router/index.ts`**: Ruta `/simulation/:scenarioId`

### Backend
- **`views.py`**:
  - `start_with_role`: Inicia sesión con scenario
  - `chat`: Procesa mensajes y lógica de juego
  - `resume_session`: Recupera sesión activa
- **`models.py`**: GameSession, ChatMessage, Scenario, SensitivePattern

---

## 🔄 API Endpoints Utilizados

```
POST /api/simulation/session/start-role/
Body: { "scenario_id": 1 }
Response: { "session_id": 42, "initial_message": "...", "resumed": false }

GET /api/simulation/session/resume/
Response: { "session_id": 42, "messages": [...], "resumed": true }

POST /api/simulation/chat/
Body: { "session_id": 42, "message": "Hola" }
Response: {
  "reply": "...",
  "session_id": 42,
  "disclosure": false,
  "antagonist_attempts": 1,
  "is_game_over": null,
  "outcome": null
}
```

---

## ✅ Estado Actual

- ✓ Backend API completa y funcional
- ✓ Frontend integrado con backend
- ✓ Chat en tiempo real
- ✓ Detección de divulgación
- ✓ Sistema de puntos
- ✓ Game over con resultados
- ✓ Reintentar niveles
- ✓ Rutas protegidas con auth

---

## 🚀 Para Probar

1. **Crear escenarios** (si no existen):
   - Ir a https://juliojc.pythonanywhere.com/admin/
   - Login: admin/admin
   - Crear 6 escenarios usando datos de `ESCENARIOS_MANUAL.txt`

2. **Probar el flujo**:
   - Login en el frontend
   - Ir a "Modo Historia"
   - Seleccionar una isla
   - Conversar con el antagonista
   - Probar ganar (resistir 3 intentos) y perder (revelar datos)

---

## 🐛 Troubleshooting

**Error 401 en start-role:**
- Verificar que el token JWT esté en localStorage como `token`
- Revisar que el usuario esté autenticado

**No se crean escenarios:**
- Los escenarios deben crearse manualmente en Django Admin
- Verificar que `is_active = True`

**Chat no responde:**
- Verificar API key de Gemini en backend
- Revisar logs del backend en PythonAnywhere
