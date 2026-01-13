from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import OnboardingQuestion, AnswerOption, OnboardingResponse, UserStatistic, GlobalStatistic
from .serializers import (
    OnboardingQuestionSerializer,
    AnswerOptionSerializer,
    OnboardingResponseSerializer,
    UserStatisticSerializer,
    GlobalStatisticSerializer
)
from apps.cyberUser.models import CyberUser, RiskLevel
from apps.llm.service import generate_onboarding_analysis


class OnboardingQuestionViewSet(viewsets.ModelViewSet):
    queryset = OnboardingQuestion.objects.prefetch_related('options').order_by('display_order')
    serializer_class = OnboardingQuestionSerializer

    @action(detail=False, methods=['get'])
    def active(self, request):
        questions = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(questions, many=True)
        return Response(serializer.data)


class AnswerOptionViewSet(viewsets.ModelViewSet):
    queryset = AnswerOption.objects.all()
    serializer_class = AnswerOptionSerializer

    def get_queryset(self):
        queryset = AnswerOption.objects.all()
        question_id = self.request.query_params.get('question_id')
        if question_id:
            queryset = queryset.filter(question_id=question_id)
        return queryset


class OnboardingResponseViewSet(viewsets.ModelViewSet):
    queryset = OnboardingResponse.objects.all()
    serializer_class = OnboardingResponseSerializer

    def get_queryset(self):
        queryset = OnboardingResponse.objects.all()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset

    @action(detail=False, methods=['get'], url_path='calculate_risk/(?P<user_id>[^/.]+)')
    def calculate_risk(self, request, user_id=None):
        user = get_object_or_404(CyberUser, pk=user_id)
        
        responses = OnboardingResponse.objects.filter(
            user_id=user_id,
            option__isnull=False
        ).select_related('question', 'option')
        
        total_risk_score = sum(
            r.option.risk_value * r.question.risk_weight for r in responses
        )
        
        total_questions = OnboardingQuestion.objects.filter(is_active=True).count()
        questions_answered = responses.count()
        
        max_weights = sum(r.question.risk_weight for r in responses)
        max_possible_score = max_weights * 5 if max_weights > 0 else 1
        
        risk_percentage = (total_risk_score / max_possible_score * 100) if max_possible_score > 0 else 0
        
        if risk_percentage <= 33:
            risk_level_name = 'Low'
        elif risk_percentage <= 66:
            risk_level_name = 'Medium'
        else:
            risk_level_name = 'High'
        
        risk_level = RiskLevel.objects.filter(name=risk_level_name).first()
        if risk_level:
            user.risk_level = risk_level
            user.save()
        
        UserStatistic.objects.update_or_create(
            user=user,
            metric='onboarding_risk_score',
            defaults={'value': risk_percentage}
        )
        
        # Generar análisis con LLM
        responses_data = [
            {
                'question': r.question.content,
                'answer': r.option.content if r.option else r.open_answer,
                'risk_value': r.option.risk_value if r.option else 0
            }
            for r in responses
        ]
        
        llm_analysis = generate_onboarding_analysis(responses_data, risk_percentage)
        
        # Guardar configuración en preferencias del usuario
        if user.preferences:
            user.preferences.base_content = llm_analysis.get('base_content', '')
            user.preferences.tone_instructions = llm_analysis.get('tone_instructions', '')
            user.preferences.save()
        
        return Response({
            'user_id': user.user_id,
            'total_risk_score': total_risk_score,
            'max_possible_score': max_possible_score,
            'risk_percentage': round(risk_percentage, 2),
            'risk_level': risk_level_name,
            'questions_answered': questions_answered,
            'total_questions': total_questions,
            'llm_analysis': llm_analysis
        })

    @action(detail=False, methods=['get'], url_path='status/(?P<user_id>[^/.]+)')
    def onboarding_status(self, request, user_id=None):
        total_questions = OnboardingQuestion.objects.filter(is_active=True).count()
        answered_questions = OnboardingResponse.objects.filter(user_id=user_id).count()
        
        return Response({
            'user_id': int(user_id),
            'total_questions': total_questions,
            'answered_questions': answered_questions,
            'is_complete': answered_questions >= total_questions,
            'progress_percentage': round(
                (answered_questions / total_questions * 100) if total_questions > 0 else 0, 2
            )
        })


class UserStatisticViewSet(viewsets.ModelViewSet):
    queryset = UserStatistic.objects.all()
    serializer_class = UserStatisticSerializer

    def get_queryset(self):
        queryset = UserStatistic.objects.all()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset


class GlobalStatisticViewSet(viewsets.ModelViewSet):
    queryset = GlobalStatistic.objects.all()
    serializer_class = GlobalStatisticSerializer

    def get_queryset(self):
        queryset = GlobalStatistic.objects.all()
        country_id = self.request.query_params.get('country_id')
        if country_id:
            queryset = queryset.filter(country_id=country_id)
        return queryset
