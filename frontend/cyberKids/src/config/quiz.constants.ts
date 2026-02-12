/**
 * Configuración flexible de rewards para Quiz System
 * Facilita cambiar puntos, monedas y cantidad esperada de preguntas
 */

export interface DifficultyConfig {
  name: string;
  coins: number;           // Monedas por completar
  points: number;          // Puntos por respuesta correcta
  numQuestions: number;    // Cantidad esperada de preguntas
  segment: string;         // Segmento de edad: 'junior' | 'middle' | 'senior'
}

export interface AgeSegment {
  minAge: number;
  maxAge: number;
  segment: string;
}

export const DIFFICULTY_LEVELS: Record<number, DifficultyConfig> = {
  1: {
    name: 'Fácil',
    coins: 10,
    points: 10,
    numQuestions: 6,
    segment: 'junior'  // 7-10 años
  },
  2: {
    name: 'Fácil',
    coins: 10,
    points: 10,
    numQuestions: 6,
    segment: 'junior'  // 7-10 años
  },
  3: {
    name: 'Medio',
    coins: 15,
    points: 15,
    numQuestions: 10,
    segment: 'middle'  // 11-14 años
  },
  4: {
    name: 'Medio',
    coins: 15,
    points: 15,
    numQuestions: 10,
    segment: 'middle'  // 11-14 años
  },
  5: {
    name: 'Difícil',
    coins: 20,
    points: 20,
    numQuestions: 12,
    segment: 'senior'  // 15+ años
  },
  6: {
    name: 'Difícil',
    coins: 20,
    points: 20,
    numQuestions: 12,
    segment: 'senior'  // 15+ años
  }
};

// Rango de edad por segmento (en años)
export const AGE_SEGMENTS: Record<string, AgeSegment> = {
  junior: { minAge: 7, maxAge: 10, segment: 'junior' },
  middle: { minAge: 11, maxAge: 14, segment: 'middle' },
  senior: { minAge: 15, maxAge: 150, segment: 'senior' }
};

/**
 * Obtiene configuración de rewards para un nivel de dificultad
 */
export function getRewardConfig(difficultyLevel: number): DifficultyConfig {
  return DIFFICULTY_LEVELS[difficultyLevel] || DIFFICULTY_LEVELS[3];
}

/**
 * Obtiene monedas para un nivel de dificultad
 */
export function getCoinsReward(difficultyLevel: number): number {
  return getRewardConfig(difficultyLevel).coins;
}

/**
 * Obtiene puntos para un nivel de dificultad
 */
export function getPointsReward(difficultyLevel: number): number {
  return getRewardConfig(difficultyLevel).points;
}

/**
 * Obtiene cantidad esperada de preguntas para el nivel
 */
export function getExpectedQuestions(difficultyLevel: number): number {
  return getRewardConfig(difficultyLevel).numQuestions;
}

/**
 * Obtiene el nombre legible del nivel de dificultad
 */
export function getDifficultyName(difficultyLevel: number): string {
  return getRewardConfig(difficultyLevel).name;
}
