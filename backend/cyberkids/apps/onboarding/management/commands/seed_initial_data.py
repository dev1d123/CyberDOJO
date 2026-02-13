from django.core.management.base import BaseCommand
from django.db import transaction

from apps.onboarding.models import OnboardingQuestion, AnswerOption
from apps.simulation.models import Scenario


class Command(BaseCommand):
    help = 'Seed initial onboarding questions, answer options and simulation scenarios.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding initial data...')
        with transaction.atomic():
            self._seed_onboarding()
            self._seed_scenarios()
        self.stdout.write(self.style.SUCCESS('Seeding completed.'))

    def _seed_onboarding(self):
        questions = [
            {
                'display_order': 1,
                'content': '¿Compartes tu contraseña con amigos o familiares?',
                'response_type': 'yes_no',
                'risk_weight': 5,
                'options': [
                    {'content': 'Sí, la comparto', 'risk_value': 5, 'display_order': 1},
                    {'content': 'No, nunca la comparto', 'risk_value': 0, 'display_order': 2},
                ]
            },
            {
                'display_order': 2,
                'content': 'Si recibes un correo que pide tu contraseña, ¿qué haces?',
                'response_type': 'multiple_choice',
                'risk_weight': 5,
                'options': [
                    {'content': 'Responder con mi contraseña', 'risk_value': 5, 'display_order': 1},
                    {'content': 'Ignorarlo y avisar a un adulto', 'risk_value': 0, 'display_order': 2},
                    {'content': 'Reenviarlo a amigos', 'risk_value': 3, 'display_order': 3},
                    {'content': 'Hacer clic en un enlace adjunto', 'risk_value': 4, 'display_order': 4},
                ]
            },
            {
                'display_order': 3,
                'content': '¿Usas la misma contraseña en varios sitios?',
                'response_type': 'yes_no',
                'risk_weight': 4,
                'options': [
                    {'content': 'Sí, la misma contraseña', 'risk_value': 4, 'display_order': 1},
                    {'content': 'No, uso contraseñas distintas', 'risk_value': 0, 'display_order': 2},
                ]
            },
            {
                'display_order': 4,
                'content': '¿Con qué frecuencia actualizas tus contraseñas?',
                'response_type': 'multiple_choice',
                'risk_weight': 3,
                'options': [
                    {'content': 'Nunca', 'risk_value': 4, 'display_order': 1},
                    {'content': 'Rara vez (cada año)', 'risk_value': 3, 'display_order': 2},
                    {'content': 'A veces (cada 3-6 meses)', 'risk_value': 1, 'display_order': 3},
                    {'content': 'Frecuentemente (cada mes)', 'risk_value': 0, 'display_order': 4},
                ]
            },
            {
                'display_order': 5,
                'content': '¿Instalas aplicaciones desde fuentes desconocidas?',
                'response_type': 'yes_no',
                'risk_weight': 4,
                'options': [
                    {'content': 'Sí, algunas veces', 'risk_value': 4, 'display_order': 1},
                    {'content': 'No, solo desde tiendas oficiales', 'risk_value': 0, 'display_order': 2},
                ]
            },
        ]

        for q in questions:
            obj, created = OnboardingQuestion.objects.get_or_create(
                display_order=q['display_order'],
                defaults={
                    'content': q['content'],
                    'response_type': q['response_type'],
                    'risk_weight': q['risk_weight'],
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'  Created question #{obj.display_order}')
            else:
                # update content in case it changed
                obj.content = q['content']
                obj.response_type = q['response_type']
                obj.risk_weight = q['risk_weight']
                obj.is_active = True
                obj.save()
                self.stdout.write(f'  Updated question #{obj.display_order}')

            # options
            existing = {opt.display_order: opt for opt in obj.options.all()}
            for opt_data in q['options']:
                opt = existing.get(opt_data['display_order'])
                if opt:
                    opt.content = opt_data['content']
                    opt.risk_value = opt_data['risk_value']
                    opt.save()
                else:
                    AnswerOption.objects.create(
                        question=obj,
                        content=opt_data['content'],
                        risk_value=opt_data['risk_value'],
                        display_order=opt_data.get('display_order'),
                    )

    def _seed_scenarios(self):
        scenarios = [
            {
                'name': 'Correo de phishing escolar',
                'description': 'Un correo que finge ser de la escuela pidiendo credenciales.',
                'antagonist_goal': 'Obtener credenciales',
                'difficulty_level': 2,
                'base_points': 100,
                'threat_type': 'phishing',
            },
            {
                'name': 'Soporte técnico falso',
                'description': 'El antagonista se hace pasar por soporte técnico para pedir acceso remoto.',
                'antagonist_goal': 'Obtener acceso remoto',
                'difficulty_level': 3,
                'base_points': 150,
                'threat_type': 'social_engineering',
            },
            {
                'name': 'Enlace malicioso en red social',
                'description': 'Un mensaje con enlace que promete un premio, en redes sociales.',
                'antagonist_goal': 'Instalar malware',
                'difficulty_level': 2,
                'base_points': 120,
                'threat_type': 'malicious_link',
            },
            {
                'name': 'Estafa de tarjetas regalo',
                'description': 'Un mensaje solicitando recargas de tarjetas regalo a nombre de un superior.',
                'antagonist_goal': 'Obtener dinero/tarjeta',
                'difficulty_level': 1,
                'base_points': 80,
                'threat_type': 'scam',
            },
        ]

        for s in scenarios:
            obj, created = Scenario.objects.get_or_create(
                name=s['name'],
                defaults={
                    'description': s['description'],
                    'antagonist_goal': s['antagonist_goal'],
                    'difficulty_level': s['difficulty_level'],
                    'base_points': s['base_points'],
                    'threat_type': s['threat_type'],
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'  Created scenario: {obj.name}')
            else:
                # update existing
                obj.description = s['description']
                obj.antagonist_goal = s['antagonist_goal']
                obj.difficulty_level = s['difficulty_level']
                obj.base_points = s['base_points']
                obj.threat_type = s['threat_type']
                obj.is_active = True
                obj.save()
                self.stdout.write(f'  Updated scenario: {obj.name}')
