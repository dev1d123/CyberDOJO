// Configuración centralizada de la API
export const API_CONFIG = {
  BASE_URL: (() => {
    const fromEnv = (import.meta as any)?.env?.VITE_API_BASE_URL as string | undefined;
    if (fromEnv && fromEnv.trim()) return fromEnv.trim();

    // Default: backend deploy (prod). For local backend, set VITE_API_BASE_URL.
    return 'http:localhost:8000';
  })(),
} as const;
