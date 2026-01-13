
import httpx
import json
from typing import Optional
from .config import get_openrouter_url, get_openrouter_api_key


def call_llm_sync(prompt: str, model: str = "gpt-4o-mini") -> Optional[str]:
    api_key = get_openrouter_api_key()
    if not api_key:
        return None
    
    with httpx.Client(timeout=30) as client:
        response = client.post(
            get_openrouter_url(),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 800
            }
        )
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
    return None

# Onboarding: Generate onboarding analysis using LLM
def generate_onboarding_analysis(responses_data: list, risk_percentage: float) -> dict:
    # Determinar dificultad inicial basada en qué tan bien respondió
    if risk_percentage <= 25:
        difficulty = "alta"
        difficulty_level = 3
    elif risk_percentage <= 50:
        difficulty = "media-alta"
        difficulty_level = 2
    elif risk_percentage <= 75:
        difficulty = "media"
        difficulty_level = 2
    else:
        difficulty = "baja"
        difficulty_level = 1

    # Construir resumen de respuestas
    responses_summary = "\n".join([
        f"- Pregunta: {r['question']}\n  Respuesta: {r['answer']} (riesgo: {r['risk_value']}/5)"
        for r in responses_data
    ])

    prompt = f"""Eres un asistente de ciberseguridad para niños. Analiza las respuestas del onboarding y genera una configuración personalizada.

RESPUESTAS DEL USUARIO:
{responses_summary}

NIVEL DE RIESGO: {risk_percentage:.1f}% (dificultad asignada: {difficulty})

Genera un JSON con exactamente esta estructura (sin markdown, solo JSON puro):
{{
    "conclusions": "Resumen breve (2-3 oraciones) de los conocimientos del usuario sobre ciberseguridad",
    "tone_instructions": "Instrucciones de tono para la mascota virtual (amigable, paciente, o desafiante según nivel)",
    "base_content": "Contexto base para futuras interacciones con el usuario",
    "initial_difficulty": {difficulty_level}
}}

La dificultad va de 1 (principiante) a 3 (avanzado). Si respondió muy bien (bajo riesgo), asigna dificultad alta."""

    result = call_llm_sync(prompt)
    
    if result:
        try:
            clean = result.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(clean)
        except json.JSONDecodeError:
            pass
    
    return {
        "conclusions": f"Usuario con conocimiento {'avanzado' if risk_percentage < 50 else 'básico'} de ciberseguridad.",
        "tone_instructions": f"Sé {'desafiante y directo' if difficulty_level >= 2 else 'amigable y paciente'}.",
        "base_content": f"Nivel de riesgo: {risk_percentage:.0f}%. Ajustar contenido según dificultad {difficulty}.",
        "initial_difficulty": difficulty_level
    }

# Pets: Generate pet interaction response using LLM
# Nada aun
