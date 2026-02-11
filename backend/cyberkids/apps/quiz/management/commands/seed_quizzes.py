from django.core.management.base import BaseCommand
from django.db import transaction
from apps.quiz.models import AudienceSegment, RiskCategory, Quiz, QuizQuestion, QuizAlternative, QuizHint


class Command(BaseCommand):
    help = 'Seed initial quiz data: segments, categories, quizzes, questions, alternatives, hints'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting quiz seeding...'))
        with transaction.atomic():
            self._seed_segments()
            self._seed_categories()
            self._seed_quizzes()
        self.stdout.write(self.style.SUCCESS('Quiz seeding completed.'))

    def _seed_segments(self):
        data = [
            {'name': 'Niños 6-8', 'min_age': 6, 'max_age': 8, 'display_order': 1},
            {'name': 'Niños 9-11', 'min_age': 9, 'max_age': 11, 'display_order': 2},
        ]
        for item in data:
            obj, created = AudienceSegment.objects.update_or_create(
                name=item['name'], defaults={
                    'min_age': item['min_age'], 'max_age': item['max_age'], 'display_order': item['display_order'], 'is_active': True
                }
            )
            self.stdout.write(f"Segment: {'created' if created else 'updated'} {obj}")

    def _seed_categories(self):
        data = [
            {'name': 'Phishing', 'icon': '📧', 'display_order': 1},
            {'name': 'Privacidad', 'icon': '🔒', 'display_order': 2},
            {'name': 'Grooming', 'icon': '⚠️', 'display_order': 3},
        ]
        for item in data:
            obj, created = RiskCategory.objects.update_or_create(
                name=item['name'], defaults={'icon': item['icon'], 'display_order': item['display_order'], 'is_active': True}
            )
            self.stdout.write(f"Category: {'created' if created else 'updated'} {obj}")

    def _seed_quizzes(self):
        # Simple example quizzes with questions and alternatives
        # Prefer the 9-11 segment if present, otherwise use the first available
        segment = AudienceSegment.objects.filter(name__icontains='9-11').first()
        if not segment:
            segment = AudienceSegment.objects.first()

        phishing_cat = RiskCategory.objects.filter(name='Phishing').first()
        privacy_cat = RiskCategory.objects.filter(name='Privacidad').first()

        quizzes_data = [
            {
                'title': 'Correo sospechoso',
                'description': 'Detecta si un correo es phishing',
                'category': phishing_cat,
                'questions': [
                    {
                        'content': 'Has recibido un correo que dice ser del banco y te pide contraseña. ¿Qué haces?',
                        'explanation': 'Los bancos nunca piden contraseñas por email.',
                        'points': 10,
                        'alternatives': [
                            {'content': 'Enviar la contraseña', 'is_correct': False, 'feedback': 'Nunca compartas tu contraseña.'},
                            {'content': 'Borrar y avisar a un adulto', 'is_correct': True, 'feedback': 'Buena decisión.'},
                            {'content': 'Hacer clic en el enlace', 'is_correct': False, 'feedback': 'Puede ser un enlace malicioso.'},
                        ],
                        'hints': [
                            {'content': 'Revisa el remitente y no compartas datos.'}
                        ]
                    }
                ]
            },
            {
                'title': 'Protege tu privacidad',
                'description': 'Consejos para proteger tu información personal',
                'category': privacy_cat,
                'questions': [
                    {
                        'content': '¿Debes compartir tu dirección en un chat con alguien que no conoces?',
                        'explanation': 'No compartas información personal con desconocidos.',
                        'points': 8,
                        'alternatives': [
                            {'content': 'Sí, para quedar mejor', 'is_correct': False, 'feedback': 'No es seguro.'},
                            {'content': 'No, nunca', 'is_correct': True, 'feedback': 'Correcto.'},
                        ],
                        'hints': [{'content': 'Piensa en quién puede ver esa información.'}]
                    }
                ]
            }
        ]

        for qz in quizzes_data:
            quiz_obj, created = Quiz.objects.update_or_create(
                title=qz['title'], defaults={
                    'segment': segment, 'category': qz['category'], 'description': qz.get('description',''), 'is_active': True
                }
            )
            self.stdout.write(f"Quiz: {'created' if created else 'updated'} {quiz_obj}")

            for qi, qd in enumerate(qz['questions'], start=1):
                q_obj, qcreated = QuizQuestion.objects.update_or_create(
                    quiz=quiz_obj, display_order=qi,
                    defaults={
                        'content': qd['content'], 'explanation': qd.get('explanation',''), 'points': qd.get('points',10), 'image_url': qd.get('image_url', None)
                    }
                )
                self.stdout.write(f"  Question: {'created' if qcreated else 'updated'} Q{q_obj.display_order}")

                # alternatives
                for ai, alt in enumerate(qd.get('alternatives',[]), start=1):
                    a_obj, acreated = QuizAlternative.objects.update_or_create(
                        question=q_obj, display_order=ai,
                        defaults={
                            'content': alt['content'], 'is_correct': alt.get('is_correct', False), 'feedback': alt.get('feedback','')
                        }
                    )
                    self.stdout.write(f"    Alt: {'created' if acreated else 'updated'} {a_obj.content[:40]}")

                # hints
                for hi, hint in enumerate(qd.get('hints',[]), start=1):
                    h_obj, hcreated = QuizHint.objects.update_or_create(
                        question=q_obj, display_order=hi,
                        defaults={'content': hint.get('content',''), 'cost_points': hint.get('cost_points',5)}
                    )
                    self.stdout.write(f"    Hint: {'created' if hcreated else 'updated'} {h_obj.content[:40]}")
