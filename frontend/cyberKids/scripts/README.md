# Scripts de Onboarding

## populate-questions.js

Script para poblar la base de datos con las preguntas de onboarding iniciales.

### ¿Qué hace?

1. **Elimina** todas las preguntas y opciones existentes en la base de datos
2. **Crea** 6 nuevas preguntas de onboarding con sus respectivas opciones
3. Muestra el progreso en consola con emojis y colores

### Requisitos previos

- Node.js versión 18 o superior (para soporte nativo de `fetch`)
- El servidor Django debe estar corriendo en `http://localhost:8000`

### Instrucciones de ejecución

#### 1. Asegúrate de que el backend esté corriendo

```powershell
# En una terminal, ve a la carpeta del backend
cd backend\cyberkids

# Inicia el servidor Django
python manage.py runserver
```

#### 2. Ejecuta el script

```powershell
# Desde la carpeta raíz del frontend
cd frontend\cyberKids

# Ejecuta el script
node scripts/populate-questions.js
```

### Salida esperada

```
🚀 Iniciando población de preguntas de onboarding

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🗑️  Eliminando todas las preguntas existentes...

   Encontradas X preguntas para eliminar
   ✓ Pregunta 1 eliminada
   ✓ Pregunta 2 eliminada
   ...

✅ Todas las preguntas eliminadas correctamente

📝 Creando nuevas preguntas...

   ✓ Pregunta 1 creada con ID 1
     • Opción 1 creada: "La rechazo"
     • Opción 2 creada: "A veces acepto"
     • Opción 3 creada: "Casi siempre acepto"

   ✓ Pregunta 2 creada con ID 2
     • Opción 4 creada: "No"
     • Opción 5 creada: "Sí"
   
   ... (continúa con todas las preguntas)

✅ Todas las preguntas creadas correctamente

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 ¡Proceso completado exitosamente!

   Total de preguntas creadas: 6
   Total de opciones creadas: 17
```

### Modificar la URL del API

Si tu backend está en una URL diferente, edita la constante `API_BASE_URL` en el archivo:

```javascript
const API_BASE_URL = 'http://localhost:8000/api/onboarding';
```

### Preguntas incluidas

1. **Solicitudes de amistad** (multiple_choice) - 3 opciones
2. **Compartir información personal** (yes_no) - 2 opciones
3. **Confianza en internet** (scale) - 5 opciones
4. **Solicitud de fotos/videos** (yes_no) - 2 opciones
5. **Mensajes incómodos** (multiple_choice) - 3 opciones
6. **Invitaciones peligrosas** (yes_no) - 2 opciones

### Solución de problemas

**Error: "fetch is not defined"**
- Asegúrate de usar Node.js 18 o superior
- Verifica con: `node --version`

**Error de conexión al API**
- Verifica que el servidor Django esté corriendo
- Confirma la URL en la constante `API_BASE_URL`

**Error 404 o 500**
- Revisa los logs del servidor Django
- Verifica que las migraciones estén aplicadas: `python manage.py migrate`
