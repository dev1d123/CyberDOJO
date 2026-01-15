# Configuración de la variable de entorno para Gemini API Key

Para que el backend funcione correctamente con Gemini, necesitas definir la variable de entorno `GEMINI_API_KEY` con tu clave de API de Google Gemini.

## Pasos para configurar la variable de entorno

### 1. Obtener tu API Key de Gemini
- Ve a [Google AI Studio](https://aistudio.google.com/) y genera tu clave de API.

### 2. Crear el archivo `.env`
En la raíz del proyecto backend (donde está `manage.py`), crea un archivo llamado `.env` si no existe.

```
GEMINI_API_KEY=tu_clave_aqui
```

Reemplaza `tu_clave_aqui` por tu clave real.

### 3. Verifica la carga de la variable
El backend está configurado para leer la clave desde `.env` automáticamente. No necesitas modificar el código.

### 4. Reinicia el servidor
Después de agregar o cambiar la clave, reinicia el servidor Django para que tome la nueva variable.

## Ejemplo de archivo `.env`
```
GEMINI_API_KEY=AIzaSyD...tu_clave...
```

## Notas
- Nunca compartas tu clave de API públicamente.
- Si usas despliegue en producción, configura la variable en el entorno del servidor.

---

¿Tienes dudas? Consulta la documentación oficial de Gemini o pregunta al equipo de desarrollo.
