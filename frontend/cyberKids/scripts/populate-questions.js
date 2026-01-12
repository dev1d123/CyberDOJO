/**
 * Script para poblar las preguntas de onboarding
 * Elimina todas las preguntas y opciones existentes y crea nuevas
 */

const API_BASE_URL = 'https://juliojc.pythonanywhere.com/api/onboarding';

const questions = [
  {
    "question_id": 1,
    "content": "Cuando alguien que no conoces te envía solicitud de amistad, ¿qué haces normalmente?",
    "response_type": "multiple_choice",
    "risk_weight": 3,
    "display_order": 1,
    "is_active": true,
    "options": [
      { "option_id": 1, "content": "La rechazo", "risk_value": 1, "display_order": 1 },
      { "option_id": 2, "content": "A veces acepto", "risk_value": 3, "display_order": 2 },
      { "option_id": 3, "content": "Casi siempre acepto", "risk_value": 5, "display_order": 3 }
    ]
  },
  {
    "question_id": 2,
    "content": "¿Alguna vez has compartido tu número, dirección o datos de tu familia con alguien de internet?",
    "response_type": "yes_no",
    "risk_weight": 3,
    "display_order": 2,
    "is_active": true,
    "options": [
      { "option_id": 4, "content": "No", "risk_value": 1, "display_order": 1 },
      { "option_id": 5, "content": "Sí", "risk_value": 5, "display_order": 2 }
    ]
  },
  {
    "question_id": 3,
    "content": "Del 1 al 5, ¿qué tanto confías en que las personas en internet dicen la verdad sobre quiénes son?",
    "response_type": "scale",
    "risk_weight": 2,
    "display_order": 3,
    "is_active": true,
    "options": [
      { "option_id": 6, "content": "1 - No confío nada", "risk_value": 1, "display_order": 1 },
      { "option_id": 7, "content": "2", "risk_value": 2, "display_order": 2 },
      { "option_id": 8, "content": "3", "risk_value": 3, "display_order": 3 },
      { "option_id": 9, "content": "4", "risk_value": 4, "display_order": 4 },
      { "option_id": 10, "content": "5 - Confío mucho", "risk_value": 5, "display_order": 5 }
    ]
  },
  {
    "question_id": 4,
    "content": "¿Alguna vez te han pedido que envíes fotos o videos personales?",
    "response_type": "yes_no",
    "risk_weight": 3,
    "display_order": 4,
    "is_active": true,
    "options": [
      { "option_id": 11, "content": "No", "risk_value": 1, "display_order": 1 },
      { "option_id": 12, "content": "Sí", "risk_value": 5, "display_order": 2 }
    ]
  },
  {
    "question_id": 5,
    "content": "Si alguien te envía mensajes que te hacen sentir incómodo, ¿qué haces?",
    "response_type": "multiple_choice",
    "risk_weight": 3,
    "display_order": 5,
    "is_active": true,
    "options": [
      { "option_id": 13, "content": "Bloqueo y aviso a un adulto", "risk_value": 1, "display_order": 1 },
      { "option_id": 14, "content": "Solo lo ignoro", "risk_value": 3, "display_order": 2 },
      { "option_id": 15, "content": "Sigo respondiendo", "risk_value": 5, "display_order": 3 }
    ]
  },
  {
    "question_id": 6,
    "content": "¿Alguna vez alguien de internet te ha invitado a reunirte en persona o hacer un reto peligroso?",
    "response_type": "yes_no",
    "risk_weight": 4,
    "display_order": 6,
    "is_active": true,
    "options": [
      { "option_id": 16, "content": "No", "risk_value": 1, "display_order": 1 },
      { "option_id": 17, "content": "Sí", "risk_value": 5, "display_order": 2 }
    ]
  }
];

async function deleteAllQuestions() {
  console.log('🗑️  Eliminando todas las preguntas existentes...\n');
  
  try {
    // Obtener todas las preguntas
    const response = await fetch(`${API_BASE_URL}/questions/`);
    if (!response.ok) {
      throw new Error(`Error al obtener preguntas: ${response.status}`);
    }
    
    const responseData = await response.json();
    
    // Manejar respuesta paginada de Django REST Framework o array directo
    const existingQuestions = Array.isArray(responseData) 
      ? responseData 
      : (responseData.results || []);
    
    console.log(`   Encontradas ${existingQuestions.length} preguntas para eliminar`);
    
    if (existingQuestions.length === 0) {
      console.log('   No hay preguntas para eliminar\n');
      return;
    }
    
    // Eliminar cada pregunta (esto eliminará las opciones en cascada)
    for (const question of existingQuestions) {
      const deleteResponse = await fetch(`${API_BASE_URL}/questions/${question.question_id}/`, {
        method: 'DELETE'
      });
      
      if (deleteResponse.ok) {
        console.log(`   ✓ Pregunta ${question.question_id} eliminada`);
      } else {
        console.error(`   ✗ Error al eliminar pregunta ${question.question_id}`);
      }
    }
    
    console.log('\n✅ Todas las preguntas eliminadas correctamente\n');
  } catch (error) {
    console.error('❌ Error al eliminar preguntas:', error.message);
    throw error;
  }
}

async function createQuestion(questionData) {
  const { options, question_id, ...questionPayload } = questionData;
  
  try {
    // Crear la pregunta
    const response = await fetch(`${API_BASE_URL}/questions/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(questionPayload)
    });
    
    if (!response.ok) {
      const errorData = await response.text();
      throw new Error(`Error ${response.status}: ${errorData}`);
    }
    
    const createdQuestion = await response.json();
    console.log(`   ✓ Pregunta ${question_id} creada con ID ${createdQuestion.question_id}`);
    
    // Crear las opciones asociadas
    for (const option of options) {
      const { option_id, ...optionPayload } = option;
      optionPayload.question = createdQuestion.question_id;
      
      const optionResponse = await fetch(`${API_BASE_URL}/options/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(optionPayload)
      });
      
      if (!optionResponse.ok) {
        const errorData = await optionResponse.text();
        throw new Error(`Error al crear opción: ${errorData}`);
      }
      
      const createdOption = await optionResponse.json();
      console.log(`     • Opción ${option_id} creada: "${option.content}"`);
    }
    
    return createdQuestion;
  } catch (error) {
    console.error(`❌ Error al crear pregunta ${question_id}:`, error.message);
    throw error;
  }
}

async function createAllQuestions() {
  console.log('📝 Creando nuevas preguntas...\n');
  
  for (const question of questions) {
    await createQuestion(question);
    console.log('');
  }
  
  console.log('✅ Todas las preguntas creadas correctamente\n');
}

async function main() {
  console.log('🚀 Iniciando población de preguntas de onboarding\n');
  console.log('━'.repeat(60));
  console.log('');
  
  try {
    // Paso 1: Eliminar preguntas existentes
    await deleteAllQuestions();
    
    // Paso 2: Crear nuevas preguntas
    await createAllQuestions();
    
    console.log('━'.repeat(60));
    console.log('🎉 ¡Proceso completado exitosamente!\n');
    console.log(`   Total de preguntas creadas: ${questions.length}`);
    const totalOptions = questions.reduce((sum, q) => sum + q.options.length, 0);
    console.log(`   Total de opciones creadas: ${totalOptions}\n`);
    
  } catch (error) {
    console.error('\n❌ Error durante el proceso:', error.message);
    process.exit(1);
  }
}

// Ejecutar el script
main();
