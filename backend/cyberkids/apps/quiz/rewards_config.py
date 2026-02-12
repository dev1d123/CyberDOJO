"""
Configuración flexible de rewards para Quiz System.
Facilita cambiar puntos, monedas y cantidad de preguntas.
"""

# Mapeo de niveles de dificultad a configuración de rewards
DIFFICULTY_LEVELS = {
    1: {
        'name': 'Fácil',
        'coins': 10,
        'points': 10,
        'num_questions': 6,
        'segment': 'junior'  # 7-10 años
    },
    2: {
        'name': 'Fácil',
        'coins': 10,
        'points': 10,
        'num_questions': 6,
        'segment': 'junior'  # 7-10 años
    },
    3: {
        'name': 'Medio',
        'coins': 15,
        'points': 15,
        'num_questions': 10,
        'segment': 'middle'  # 11-14 años
    },
    4: {
        'name': 'Medio',
        'coins': 15,
        'points': 15,
        'num_questions': 10,
        'segment': 'middle'  # 11-14 años
    },
    5: {
        'name': 'Difícil',
        'coins': 20,
        'points': 20,
        'num_questions': 12,
        'segment': 'senior'  # 15+ años
    },
    6: {
        'name': 'Difícil',
        'coins': 20,
        'points': 20,
        'num_questions': 12,
        'segment': 'senior'  # 15+ años
    }
}

# Rango de edad por segmento (en años)
AGE_SEGMENTS = {
    'junior': (7, 10),      # 7-10 años
    'middle': (11, 14),     # 11-14 años
    'senior': (15, 150)     # 15+ años
}

def get_reward_config(difficulty_level: int) -> dict:
    """Obtiene configuración de recompensas para un nivel de dificultad."""
    return DIFFICULTY_LEVELS.get(difficulty_level, DIFFICULTY_LEVELS[3])

def get_segment_for_age(age: int) -> str:
    """Retorna el segmento basado en la edad."""
    for segment, (min_age, max_age) in AGE_SEGMENTS.items():
        if min_age <= age <= max_age:
            return segment
    return 'middle'  # Valor por defecto

def get_coins_reward(difficulty_level: int) -> int:
    """Retorna monedas para un nivel de dificultad."""
    return get_reward_config(difficulty_level)['coins']

def get_points_reward(difficulty_level: int) -> int:
    """Retorna puntos para un nivel de dificultad."""
    return get_reward_config(difficulty_level)['points']

def get_expected_questions(difficulty_level: int) -> int:
    """Retorna cantidad esperada de preguntas para el nivel."""
    return get_reward_config(difficulty_level)['num_questions']
