export interface QuizProgressData {
  quizId: number
  sessionId: number | null
  currentQuestionIndex: number
  answers: Array<{
    questionId: number
    selectedAlternativeId: number
    isCorrect: boolean
    timeSpent: number
  }>
  totalPoints: number
  startedAt: string
  lastUpdatedAt: string
}

const STORAGE_KEY_PREFIX = 'quiz_progress_'

export function useQuizProgress() {
  /**
   * Guardar progreso del quiz en localStorage
   */
  const saveProgress = (data: QuizProgressData) => {
    try {
      const key = `${STORAGE_KEY_PREFIX}${data.quizId}`
      localStorage.setItem(key, JSON.stringify(data))
      console.log('✅ Progreso guardado para quiz', data.quizId)
    } catch (error) {
      console.error('❌ Error guardando progreso:', error)
    }
  }

  /**
   * Cargar progreso guardado de un quiz
   */
  const loadProgress = (quizId: number): QuizProgressData | null => {
    try {
      const key = `${STORAGE_KEY_PREFIX}${quizId}`
      const stored = localStorage.getItem(key)
      if (!stored) return null
      
      const data = JSON.parse(stored) as QuizProgressData
      console.log('📖 Progreso cargado para quiz', quizId, data)
      return data
    } catch (error) {
      console.error('❌ Error cargando progreso:', error)
      return null
    }
  }

  /**
   * Eliminar progreso guardado de un quiz
   */
  const clearProgress = (quizId: number) => {
    try {
      const key = `${STORAGE_KEY_PREFIX}${quizId}`
      localStorage.removeItem(key)
      console.log('🗑️ Progreso eliminado para quiz', quizId)
    } catch (error) {
      console.error('❌ Error eliminando progreso:', error)
    }
  }

  /**
   * Verificar si existe progreso guardado
   */
  const hasProgress = (quizId: number): boolean => {
    const key = `${STORAGE_KEY_PREFIX}${quizId}`
    return localStorage.getItem(key) !== null
  }

  /**
   * Obtener todos los quizzes con progreso guardado
   */
  const getAllProgressQuizzes = (): number[] => {
    const quizIds: number[] = []
    try {
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i)
        if (key?.startsWith(STORAGE_KEY_PREFIX)) {
          const quizId = parseInt(key.replace(STORAGE_KEY_PREFIX, ''))
          if (!isNaN(quizId)) {
            quizIds.push(quizId)
          }
        }
      }
    } catch (error) {
      console.error('❌ Error obteniendo quizzes con progreso:', error)
    }
    return quizIds
  }

  /**
   * Actualizar respuesta en el progreso
   */
  const updateAnswer = (
    progress: QuizProgressData,
    questionId: number,
    selectedAlternativeId: number,
    isCorrect: boolean,
    timeSpent: number
  ): QuizProgressData => {
    const updatedProgress = {
      ...progress,
      answers: [
        ...progress.answers,
        {
          questionId,
          selectedAlternativeId,
          isCorrect,
          timeSpent
        }
      ],
      lastUpdatedAt: new Date().toISOString()
    }
    
    saveProgress(updatedProgress)
    return updatedProgress
  }

  return {
    saveProgress,
    loadProgress,
    clearProgress,
    hasProgress,
    getAllProgressQuizzes,
    updateAnswer
  }
}
