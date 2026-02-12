"""
Script para llenar todas las tablas del app quiz con datos de prueba.
Uso: python manage.py populate_quiz
"""

from django.core.management.base import BaseCommand
from apps.quiz.models import (
    AudienceSegment, RiskCategory, Quiz, QuizQuestion, 
    QuizAlternative, QuizHint
)


class Command(BaseCommand):
    help = "Popula todas las tablas del quiz con datos de prueba"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Iniciando población de tablas quiz..."))
        
        # 1. AUDIENCE SEGMENTS
        self._create_audience_segments()
        
        # 2. RISK CATEGORIES
        self._create_risk_categories()
        
        # 3. QUIZZES
        self._create_quizzes()
        
        # 4. QUESTIONS, ALTERNATIVES Y HINTS
        self._create_questions_and_alternatives()
        
        self.stdout.write(self.style.SUCCESS("\n✓ ¡Todas las tablas han sido populadas correctamente!"))

    def _create_audience_segments(self):
        """Crear segmentos de audiencia por edad"""
        self.stdout.write("Creando Audience Segments...")
        
        segments = [
            {"name": "Niños 7-10", "description": "Contenido básico para niños (junior)", "min_age": 7, "max_age": 10, "display_order": 1},
            {"name": "Niños 11-14", "description": "Contenido intermedio para niños (middle)", "min_age": 11, "max_age": 14, "display_order": 2},
            {"name": "Adolescentes 15+", "description": "Contenido avanzado para adolescentes (senior)", "min_age": 15, "max_age": 150, "display_order": 3},
        ]
        
        for seg in segments:
            obj, created = AudienceSegment.objects.get_or_create(
                name=seg["name"],
                defaults={
                    "description": seg["description"],
                    "min_age": seg["min_age"],
                    "max_age": seg["max_age"],
                    "display_order": seg["display_order"]
                }
            )
            if created:
                self.stdout.write(f"  ✓ {seg['name']}")
        
        self.stdout.write(self.style.SUCCESS(f"  Total: {AudienceSegment.objects.count()} segmentos\n"))

    def _create_risk_categories(self):
        """Crear categorías de riesgo cibernético"""
        self.stdout.write("Creando Risk Categories...")
        
        categories = [
            {
                "name": "Phishing",
                "description": "Técnicas de engaño para robar información personal",
                "icon": "🎣",
                "display_order": 1
            },
            {
                "name": "Grooming",
                "description": "Manipulación y acoso en línea de menores",
                "icon": "🚨",
                "display_order": 2
            },
            {
                "name": "Privacidad",
                "description": "Protección de datos personales en internet",
                "icon": "🔒",
                "display_order": 3
            },
            {
                "name": "Contraseñas",
                "description": "Seguridad de contraseñas y autenticación",
                "icon": "🔑",
                "display_order": 4
            },
            {
                "name": "Ciberacoso",
                "description": "Acoso y bullying en redes sociales",
                "icon": "💔",
                "display_order": 5
            },
            {
                "name": "Descargas Seguras",
                "description": "Identificar descargas maliciosas",
                "icon": "📥",
                "display_order": 6
            },
        ]
        
        for cat in categories:
            obj, created = RiskCategory.objects.get_or_create(
                name=cat["name"],
                defaults={
                    "description": cat["description"],
                    "icon": cat["icon"],
                    "display_order": cat["display_order"]
                }
            )
            if created:
                self.stdout.write(f"  ✓ {cat['name']}")
        
        self.stdout.write(self.style.SUCCESS(f"  Total: {RiskCategory.objects.count()} categorías\n"))

    def _create_quizzes(self):
        """Crear quizzes para diferentes segmentos y categorías"""
        self.stdout.write("Creando Quizzes...")
        
        segments = AudienceSegment.objects.all()
        categories = RiskCategory.objects.all()
        
        quiz_data = [
            # Niños 7-10
            {
                "segment_name": "Niños 7-10",
                "category_name": "Phishing",
                "title": "¿Es este email de verdad?",
                "description": "Aprende a identificar emails falsos",
                "difficulty_level": 1,
                "base_points": 50,
                "time_limit_seconds": 300
            },
            {
                "segment_name": "Niños 7-10",
                "category_name": "Privacidad",
                "title": "Mi información es privada",
                "description": "Qué información no debes compartir en internet",
                "difficulty_level": 1,
                "base_points": 50,
                "time_limit_seconds": 300
            },
            {
                "segment_name": "Niños 7-10",
                "category_name": "Contraseñas",
                "title": "Contraseñas fuertes",
                "description": "Cómo crear contraseñas seguras",
                "difficulty_level": 1,
                "base_points": 50,
                "time_limit_seconds": 300
            },
            # Niños 11-14
            {
                "segment_name": "Niños 11-14",
                "category_name": "Phishing",
                "title": "Detecta el Phishing",
                "description": "Técnicas avanzadas de phishing",
                "difficulty_level": 3,
                "base_points": 100,
                "time_limit_seconds": 600
            },
            {
                "segment_name": "Niños 11-14",
                "category_name": "Grooming",
                "title": "Extraños en línea",
                "description": "Cómo reconocer a depredadores online",
                "difficulty_level": 3,
                "base_points": 100,
                "time_limit_seconds": 600
            },
            {
                "segment_name": "Niños 11-14",
                "category_name": "Ciberacoso",
                "title": "No al Ciberacoso",
                "description": "Cómo enfrentar el bullying digital",
                "difficulty_level": 3,
                "base_points": 100,
                "time_limit_seconds": 600
            },
            # Adolescentes 15+
            {
                "segment_name": "Adolescentes 15+",
                "category_name": "Phishing",
                "title": "Ingeniería Social",
                "description": "Técnicas sofisticadas de phishing",
                "difficulty_level": 5,
                "base_points": 150,
                "time_limit_seconds": 900
            },
            {
                "segment_name": "Adolescentes 15+",
                "category_name": "Privacidad",
                "title": "Privacidad en Redes Sociales",
                "description": "Configuración de privacidad en redes",
                "difficulty_level": 5,
                "base_points": 150,
                "time_limit_seconds": 900
            },
            {
                "segment_name": "Adolescentes 15+",
                "category_name": "Contraseñas",
                "title": "Gestión de Contraseñas",
                "description": "Mejores prácticas en seguridad de contraseñas",
                "difficulty_level": 5,
                "base_points": 200,
                "time_limit_seconds": 1200
            },
        ]
        
        for i, quiz_info in enumerate(quiz_data, 1):
            segment = AudienceSegment.objects.get(name=quiz_info["segment_name"])
            category = RiskCategory.objects.get(name=quiz_info["category_name"])
            
            obj, created = Quiz.objects.get_or_create(
                title=quiz_info["title"],
                segment=segment,
                category=category,
                defaults={
                    "description": quiz_info["description"],
                    "difficulty_level": quiz_info["difficulty_level"],
                    "base_points": quiz_info["base_points"],
                    "time_limit_seconds": quiz_info["time_limit_seconds"],
                    "display_order": i
                }
            )
            if created:
                self.stdout.write(f"  ✓ {quiz_info['title']}")
        
        self.stdout.write(self.style.SUCCESS(f"  Total: {Quiz.objects.count()} quizzes\n"))

    def _create_questions_and_alternatives(self):
        """Crear preguntas, alternativas e indicios para cada quiz"""
        self.stdout.write("Creando Questions, Alternatives e Hints...")
        
        quizzes = Quiz.objects.all()
        question_count = 0
        alternative_count = 0
        hint_count = 0
        
        for quiz in quizzes:
            # Determinar número de preguntas según dificultad
            num_questions = 6 if quiz.difficulty_level in [1, 2] else 10
            
            for q_idx in range(1, num_questions + 1):
                question, q_created = QuizQuestion.objects.get_or_create(
                    quiz=quiz,
                    display_order=q_idx,
                    defaults={
                        "content": f"Pregunta {q_idx} de {quiz.title}: ¿Cuál es la respuesta correcta?",
                        "explanation": f"Explicación detallada para la pregunta {q_idx} del quiz {quiz.title}. Esta es una pregunta importante para entender ciberseguridad.",
                        "points": 10 if quiz.difficulty_level < 3 else 15,
                        "image_url": None
                    }
                )
                
                if q_created:
                    question_count += 1
                
                # Crear 4 alternativas por pregunta (solo si faltan)
                if not question.alternatives.exists():
                    alternatives_data = [
                        {"content": "Respuesta Correcta", "is_correct": True, "feedback": "¡Excelente! Esta es la respuesta correcta."},
                        {"content": "Respuesta Incorrecta 1", "is_correct": False, "feedback": "No, esta no es la respuesta correcta. Intenta de nuevo."},
                        {"content": "Respuesta Incorrecta 2", "is_correct": False, "feedback": "No, esta tampoco es correcta. Recuerda..."},
                        {"content": "Respuesta Incorrecta 3", "is_correct": False, "feedback": "Incorrecto. La respuesta correcta es otra."},
                    ]

                    alternatives = [
                        QuizAlternative(
                            question=question,
                            display_order=alt_idx,
                            content=alt_data["content"],
                            is_correct=alt_data["is_correct"],
                            feedback=alt_data["feedback"],
                        )
                        for alt_idx, alt_data in enumerate(alternatives_data, 1)
                    ]
                    QuizAlternative.objects.bulk_create(alternatives)
                    alternative_count += len(alternatives)

                # Crear 2 pistas por pregunta (solo si faltan)
                if not question.hints.exists():
                    hints_data = [
                        {"content": "Pista 1: Piensa en las características principales de un ataque de phishing.", "cost_points": 5},
                        {"content": "Pista 2: Busca detalles sospechosos en el mensaje.", "cost_points": 5},
                    ]

                    hints = [
                        QuizHint(
                            question=question,
                            display_order=hint_idx,
                            content=hint_data["content"],
                            cost_points=hint_data["cost_points"],
                        )
                        for hint_idx, hint_data in enumerate(hints_data, 1)
                    ]
                    QuizHint.objects.bulk_create(hints)
                    hint_count += len(hints)
        
        self.stdout.write(self.style.SUCCESS(
            f"  Total: {question_count} preguntas, {alternative_count} alternativas, {hint_count} pistas\n"
        ))

