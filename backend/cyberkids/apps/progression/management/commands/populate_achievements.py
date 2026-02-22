"""
Comando para poblar la base de datos con logros iniciales.
Ejecutar: python manage.py populate_achievements
"""

from django.core.management.base import BaseCommand
from apps.progression.models import Achievement


class Command(BaseCommand):
    help = 'Pobla la base de datos con logros iniciales'

    ACHIEVEMENTS = [
        # ==================== SIMULACIÓN ====================
        {
            'name': 'Primera Simulación',
            'description': 'Completa tu primera simulación de ciberseguridad',
            'category': 'simulation',
            'cybercreds_reward': 50,
            'xp_reward': 100,
            'requirement_type': 'first_simulation',
            'requirement_value': 1,
            'is_hidden': False,
        },
        {
            'name': 'Veterano de Simulaciones',
            'description': 'Completa 5 simulaciones de ciberseguridad',
            'category': 'simulation',
            'cybercreds_reward': 100,
            'xp_reward': 250,
            'requirement_type': 'simulation_veteran',
            'requirement_value': 5,
            'is_hidden': False,
        },
        {
            'name': 'Maestro de Simulaciones',
            'description': 'Completa 10 simulaciones de ciberseguridad',
            'category': 'simulation',
            'cybercreds_reward': 200,
            'xp_reward': 500,
            'requirement_type': 'simulation_master',
            'requirement_value': 10,
            'is_hidden': False,
        },
        {
            'name': 'Héroe Cibernético',
            'description': 'Gana tu primera simulación sin caer en trampas',
            'category': 'simulation',
            'cybercreds_reward': 75,
            'xp_reward': 150,
            'requirement_type': 'simulation_hero',
            'requirement_value': 1,
            'is_hidden': False,
        },
        {
            'name': 'Invencible',
            'description': 'Gana 5 simulaciones sin caer en ninguna trampa',
            'category': 'simulation',
            'cybercreds_reward': 250,
            'xp_reward': 500,
            'requirement_type': 'undefeatable',
            'requirement_value': 5,
            'is_hidden': False,
        },
        
        # ==================== QUIZ ====================
        {
            'name': 'Primer Quiz',
            'description': 'Completa tu primer quiz de ciberseguridad',
            'category': 'quiz',
            'cybercreds_reward': 50,
            'xp_reward': 100,
            'requirement_type': 'first_quiz',
            'requirement_value': 1,
            'is_hidden': False,
        },
        {
            'name': 'Estudiante Aplicado',
            'description': 'Completa 5 quizzes',
            'category': 'quiz',
            'cybercreds_reward': 100,
            'xp_reward': 250,
            'requirement_type': 'quiz_student',
            'requirement_value': 5,
            'is_hidden': False,
        },
        {
            'name': 'Experto en Quizzes',
            'description': 'Completa 10 quizzes',
            'category': 'quiz',
            'cybercreds_reward': 200,
            'xp_reward': 500,
            'requirement_type': 'quiz_master',
            'requirement_value': 10,
            'is_hidden': False,
        },
        {
            'name': 'Puntuación Perfecta',
            'description': 'Obtén todas las respuestas correctas en un quiz',
            'category': 'quiz',
            'cybercreds_reward': 150,
            'xp_reward': 300,
            'requirement_type': 'perfect_score',
            'requirement_value': 1,
            'is_hidden': False,
        },
        
        # ==================== COLECCIÓN ====================
        {
            'name': 'Primera Mascota',
            'description': 'Adopta tu primera mascota virtual',
            'category': 'collection',
            'cybercreds_reward': 25,
            'xp_reward': 50,
            'requirement_type': 'first_pet',
            'requirement_value': 1,
            'is_hidden': False,
        },
        {
            'name': 'Coleccionista de Mascotas',
            'description': 'Adopta 3 mascotas virtuales',
            'category': 'collection',
            'cybercreds_reward': 75,
            'xp_reward': 150,
            'requirement_type': 'pet_collector',
            'requirement_value': 3,
            'is_hidden': False,
        },
        {
            'name': 'Santuario de Mascotas',
            'description': 'Adopta 5 mascotas virtuales',
            'category': 'collection',
            'cybercreds_reward': 150,
            'xp_reward': 300,
            'requirement_type': 'pet_master',
            'requirement_value': 5,
            'is_hidden': True,  # Logro secreto
        },
        
        # ==================== PROGRESIÓN ====================
        {
            'name': 'Primeros Créditos',
            'description': 'Gana un total de 100 CyberCredits',
            'category': 'progression',
            'cybercreds_reward': 20,
            'xp_reward': 50,
            'requirement_type': 'first_credits',
            'requirement_value': 100,
            'is_hidden': False,
        },
        {
            'name': 'Ahorrador',
            'description': 'Gana un total de 500 CyberCredits',
            'category': 'progression',
            'cybercreds_reward': 50,
            'xp_reward': 150,
            'requirement_type': 'credit_collector',
            'requirement_value': 500,
            'is_hidden': False,
        },
        {
            'name': 'Cyber Millonario',
            'description': 'Gana un total de 1000 CyberCredits',
            'category': 'progression',
            'cybercreds_reward': 100,
            'xp_reward': 300,
            'requirement_type': 'cyber_rich',
            'requirement_value': 1000,
            'is_hidden': True,  # Logro secreto
        },
        {
            'name': 'Subiendo de Nivel',
            'description': 'Alcanza el nivel 2',
            'category': 'progression',
            'cybercreds_reward': 50,
            'xp_reward': 100,
            'requirement_type': 'level_up',
            'requirement_value': 2,
            'is_hidden': False,
        },
        {
            'name': 'Aprendiz Avanzado',
            'description': 'Alcanza el nivel 5',
            'category': 'progression',
            'cybercreds_reward': 100,
            'xp_reward': 300,
            'requirement_type': 'advanced_learner',
            'requirement_value': 5,
            'is_hidden': False,
        },
        {
            'name': 'Experto Cibernético',
            'description': 'Alcanza el nivel 10',
            'category': 'progression',
            'cybercreds_reward': 250,
            'xp_reward': 750,
            'requirement_type': 'cyber_expert',
            'requirement_value': 10,
            'is_hidden': True,  # Logro secreto
        },
    ]

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for achievement_data in self.ACHIEVEMENTS:
            achievement, created = Achievement.objects.update_or_create(
                requirement_type=achievement_data['requirement_type'],
                requirement_value=achievement_data['requirement_value'],
                defaults={
                    'name': achievement_data['name'],
                    'description': achievement_data['description'],
                    'category': achievement_data['category'],
                    'cybercreds_reward': achievement_data['cybercreds_reward'],
                    'xp_reward': achievement_data['xp_reward'],
                    'is_hidden': achievement_data.get('is_hidden', False),
                    'is_active': True,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Creado: {achievement.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'↻ Actualizado: {achievement.name}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'=== Resumen ==='))
        self.stdout.write(f'Logros creados: {created_count}')
        self.stdout.write(f'Logros actualizados: {updated_count}')
        self.stdout.write(f'Total de logros: {Achievement.objects.count()}')
