"""
Servicio para gestionar el sistema de logros.
Maneja la verificación y desbloqueo automático de logros.
"""

from django.db import transaction
from django.db.models import Count
from .models import Achievement, UserAchievement, UserProgress, CreditTransaction
from apps.simulation.models import GameSession
from apps.quiz.models import QuizSession
from apps.pets.models import UserPet


class AchievementService:
    """Servicio central para gestionar logros."""

    # Definición de requisitos de logros
    ACHIEVEMENT_DEFINITIONS = {
        # Simulaciones
        'first_simulation': {
            'check': 'check_simulations_completed',
            'value': 1,
        },
        'simulation_veteran': {
            'check': 'check_simulations_completed',
            'value': 5,
        },
        'simulation_master': {
            'check': 'check_simulations_completed',
            'value': 10,
        },
        'simulation_hero': {
            'check': 'check_simulations_won',
            'value': 1,
        },
        'undefeatable': {
            'check': 'check_simulations_won',
            'value': 5,
        },
        # Quiz
        'first_quiz': {
            'check': 'check_quizzes_completed',
            'value': 1,
        },
        'quiz_student': {
            'check': 'check_quizzes_completed',
            'value': 5,
        },
        'quiz_master': {
            'check': 'check_quizzes_completed',
            'value': 10,
        },
        'perfect_score': {
            'check': 'check_perfect_quiz',
            'value': 1,
        },
        # Colección
        'first_pet': {
            'check': 'check_pets_owned',
            'value': 1,
        },
        'pet_collector': {
            'check': 'check_pets_owned',
            'value': 3,
        },
        'pet_master': {
            'check': 'check_pets_owned',
            'value': 5,
        },
        # Progresión
        'first_credits': {
            'check': 'check_total_credits_earned',
            'value': 100,
        },
        'credit_collector': {
            'check': 'check_total_credits_earned',
            'value': 500,
        },
        'cyber_rich': {
            'check': 'check_total_credits_earned',
            'value': 1000,
        },
        'level_up': {
            'check': 'check_level_reached',
            'value': 2,
        },
        'advanced_learner': {
            'check': 'check_level_reached',
            'value': 5,
        },
        'cyber_expert': {
            'check': 'check_level_reached',
            'value': 10,
        },
    }

    @classmethod
    def check_and_unlock_achievements(cls, user):
        """
        Verifica todos los logros para un usuario y desbloquea los que correspondan.
        Retorna lista de logros recién desbloqueados.
        """
        unlocked = []
        achievements = Achievement.objects.filter(is_active=True)
        
        for achievement in achievements:
            # Verificar si ya tiene el logro
            if UserAchievement.objects.filter(user=user, achievement=achievement).exists():
                continue
            
            # Obtener la definición del logro
            definition = cls.ACHIEVEMENT_DEFINITIONS.get(achievement.requirement_type)
            if not definition:
                continue
            
            # Ejecutar la verificación
            check_method = getattr(cls, definition['check'], None)
            if not check_method:
                continue
            
            current_progress = check_method(user)
            required_value = achievement.requirement_value
            
            # Si cumple el requisito, desbloquear
            if current_progress >= required_value:
                user_achievement = cls._unlock_achievement(user, achievement, current_progress)
                unlocked.append({
                    'achievement': achievement,
                    'user_achievement': user_achievement
                })
        
        return unlocked

    @classmethod
    def update_progress(cls, user, achievement_type):
        """
        Actualiza el progreso de un tipo específico de logro.
        Útil para actualizar progreso sin desbloquear.
        """
        achievements = Achievement.objects.filter(
            is_active=True,
            requirement_type=achievement_type
        )
        
        definition = cls.ACHIEVEMENT_DEFINITIONS.get(achievement_type)
        if not definition:
            return []
        
        check_method = getattr(cls, definition['check'], None)
        if not check_method:
            return []
        
        current_progress = check_method(user)
        
        # Actualizar progreso en logros existentes (no desbloqueados)
        for achievement in achievements:
            user_ach, created = UserAchievement.objects.get_or_create(
                user=user,
                achievement=achievement,
                defaults={'progress': min(current_progress, achievement.requirement_value)}
            )
            if not created and current_progress >= achievement.requirement_value:
                # Si aún no está completamente desbloqueado, actualizamos
                user_ach.progress = achievement.requirement_value
                user_ach.save(update_fields=['progress'])

    @classmethod
    @transaction.atomic
    def _unlock_achievement(cls, user, achievement, progress):
        """Desbloquea un logro para el usuario."""
        user_achievement, created = UserAchievement.objects.get_or_create(
            user=user,
            achievement=achievement,
            defaults={'progress': progress}
        )
        
        if not created:
            user_achievement.progress = progress
            user_achievement.save(update_fields=['progress'])
        
        return user_achievement

    # ==================== MÉTODOS DE VERIFICACIÓN ====================

    @classmethod
    def check_simulations_completed(cls, user):
        """Cuenta simulaciones completadas (terminadas)."""
        return GameSession.objects.filter(
            user=user,
            status='completed'
        ).count()

    @classmethod
    def check_simulations_won(cls, user):
        """Cuenta simulaciones ganadas."""
        return GameSession.objects.filter(
            user=user,
            outcome='won'
        ).count()

    @classmethod
    def check_quizzes_completed(cls, user):
        """Cuenta quizzes completados."""
        return QuizSession.objects.filter(
            user=user,
            status='completed'
        ).count()

    @classmethod
    def check_perfect_quiz(cls, user):
        """Cuenta quizzes con puntuación perfecta."""
        perfect_count = 0
        sessions = QuizSession.objects.filter(
            user=user,
            status='completed'
        ).select_related('quiz')
        
        for session in sessions:
            total_questions = session.quiz.questions.count()
            if total_questions > 0 and session.total_correct == total_questions:
                perfect_count += 1
        
        return perfect_count

    @classmethod
    def check_pets_owned(cls, user):
        """Cuenta mascotas que tiene el usuario."""
        return UserPet.objects.filter(user=user).count()

    @classmethod
    def check_total_credits_earned(cls, user):
        """Suma total de créditos ganados (solo positivos)."""
        from django.db.models import Sum
        result = CreditTransaction.objects.filter(
            user=user,
            amount__gt=0
        ).aggregate(total=Sum('amount'))
        return result['total'] or 0

    @classmethod
    def check_level_reached(cls, user):
        """Obtiene el nivel actual del usuario."""
        try:
            progress = UserProgress.objects.get(user=user)
            return progress.current_level.level_number if progress.current_level else 1
        except UserProgress.DoesNotExist:
            return 1

    # ==================== TRIGGERS POR EVENTO ====================

    @classmethod
    def on_simulation_completed(cls, user, session):
        """Llamar cuando se completa una simulación."""
        unlocked = cls.check_and_unlock_achievements(user)
        return unlocked

    @classmethod
    def on_quiz_completed(cls, user, session):
        """Llamar cuando se completa un quiz."""
        unlocked = cls.check_and_unlock_achievements(user)
        return unlocked

    @classmethod
    def on_pet_purchased(cls, user):
        """Llamar cuando se compra una mascota."""
        unlocked = cls.check_and_unlock_achievements(user)
        return unlocked

    @classmethod
    def on_credits_earned(cls, user, amount):
        """Llamar cuando se ganan créditos."""
        unlocked = cls.check_and_unlock_achievements(user)
        return unlocked

    @classmethod
    def on_level_up(cls, user):
        """Llamar cuando el usuario sube de nivel."""
        unlocked = cls.check_and_unlock_achievements(user)
        return unlocked
