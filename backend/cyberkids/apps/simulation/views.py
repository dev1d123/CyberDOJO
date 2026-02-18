from django.http import JsonResponse
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from rest_framework import viewsets
import logging
import re
import json
import requests
from django.utils import timezone
import os
from apps.cyberUser.models import CyberUser


def _extract_json_from_text(text):
    """Extrae JSON de texto simple."""
    if not text or not isinstance(text, str):
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


def get_display_text(obj):
    """Extrae texto simple de respuestas del backend."""
    if isinstance(obj, dict):
        for k in ('reply', 'message', 'text', 'content'):
            v = obj.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
        return str(obj)
    if isinstance(obj, str):
        return obj.strip()
    return str(obj)


# URL del backend LLM externo
LLM_API_BASE_URL = "https://cyber-dojo-llm-api.vercel.app"

def _call_llm_backend(payload: dict) -> dict:
    """Llama al backend LLM externo en Vercel.
    
    Args:
        payload: Diccionario con formato:
            {
                "session_id": str,
                "max_attempts": int,
                "current_attempts_used": int,
                "user_context": {"username": str, "country": str},
                "scenario_context": {
                    "platform": str,
                    "antagonist_goal": str,
                    "difficulty": int
                },
                "chat_history": [{"role": str, "content": str}, ...]
            }
    
    Returns:
        dict con formato:
            {
                "reply": str,
                "analysis": {
                    "has_disclosure": bool,
                    "disclosure_reason": str,
                    "is_attack_attempt": bool,
                    "is_user_evasion": bool,
                    "force_end_session": bool
                }
            }
    """
    url = f"{LLM_API_BASE_URL.rstrip('/')}/api/simulation-chat"
    
    logger.info(f"🔵 Llamando al backend LLM: {url}")
    logger.info(f"🔵 Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        logger.info(f"🔵 Status code: {response.status_code}")
        logger.info(f"🔵 Response text: {response.text[:500]}")
        
        response.raise_for_status()
        data = response.json()
        logger.info(f"✅ Backend LLM respondió exitosamente")
        return data
    except requests.exceptions.Timeout as e:
        logger.error(f"❌ Timeout al llamar al backend LLM: {e}")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"❌ Error de conexión al backend LLM: {e}")
    except requests.exceptions.HTTPError as e:
        logger.error(f"❌ Error HTTP del backend LLM: {e} - Response: {response.text[:500]}")
    except Exception as e:
        logger.exception(f"❌ Error inesperado al llamar al backend LLM: {e}")
    
    # Fallback response
    return {
        "reply": "Lo siento, hay un problema técnico. Intenta de nuevo más tarde.",
        "analysis": {
            "has_disclosure": False,
            "disclosure_reason": "",
            "is_attack_attempt": False,
            "is_user_evasion": False,
            "force_end_session": False
        }
    }


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_with_role(request):
    """Crea una nueva GameSession y devuelve el primer mensaje del antagonista usando el backend LLM externo.
    
    Request body (JSON):
        - scenario_id (int, opcional): ID del escenario específico a usar
    
    Si no se especifica scenario_id, se asigna automáticamente el siguiente no completado.
    """
    from apps.cyberUser.models import CyberUser
    user = None
    if hasattr(request, 'user') and getattr(request.user, 'is_authenticated', False):
        if isinstance(request.user, CyberUser):
            user = request.user
        else:
            try:
                user_pk = getattr(request.user, 'user_id', None) or getattr(request.user, 'pk', None)
                if user_pk:
                    user = CyberUser.objects.get(pk=user_pk)
            except Exception:
                user = None
    if not user:
        return JsonResponse({'error': 'authentication_required'}, status=401)
    
    from apps.simulation.models import Scenario, GameSession, ChatMessage
    
    data = request.data if isinstance(request.data, dict) else {}
    scenario_id = data.get('scenario_id')
    
    scenario = None
    
    if scenario_id:
        try:
            scenario = Scenario.objects.get(scenario_id=int(scenario_id), is_active=True)
        except Scenario.DoesNotExist:
            return JsonResponse({'error': 'scenario_not_found', 'message': f'Escenario {scenario_id} no existe o no está activo'}, status=404)
        except Exception as e:
            return JsonResponse({'error': 'invalid_scenario_id', 'message': str(e)}, status=400)
    else:
        try:
            completed_ids = list(GameSession.objects.filter(user=user, outcome='won').values_list('scenario_id', flat=True))
        except Exception:
            completed_ids = []
        scenario = Scenario.objects.filter(is_active=True).exclude(
            scenario_id__in=completed_ids
        ).order_by('difficulty_level', 'scenario_id').first()
        if not scenario:
            scenario = Scenario.objects.filter(is_active=True).order_by('scenario_id').first()
    
    if not scenario:
        return JsonResponse({'error': 'no_active_scenario'}, status=404)
    
    from django.db import transaction
    try:
        with transaction.atomic():
            session = GameSession.objects.create(user=user, scenario=scenario)
            session.scenario_snapshot = {
                'id': scenario.scenario_id,
                'name': scenario.name,
                'description': scenario.description,
                'antagonist_goal': scenario.antagonist_goal,
                'difficulty': scenario.difficulty_level,
                'base_points': scenario.base_points,
            }
            session.antagonist_attempts = 0
            session.save()
    except Exception:
        return JsonResponse({'error': 'failed_to_create_session'}, status=500)
    
    # Preparar payload para el backend LLM externo
    max_attempts = getattr(__import__('django.conf').conf.settings, 'SIM_MAX_ATTEMPTS', 3)
    
    payload = {
        "session_id": str(session.session_id),
        "max_attempts": max_attempts,
        "current_attempts_used": 0,
        "user_context": {
            "username": user.username,
            "country": user.country.name if user and getattr(user, 'country', None) else "",
            "age": (user.preferences.age if hasattr(user, 'preferences') and user.preferences and user.preferences.age else 12)
        },
        "scenario_context": {
            "platform": scenario.threat_type or "generic",
            "antagonist_goal": scenario.antagonist_goal or "información sensible",
            "difficulty": str(scenario.difficulty_level),
            "theme_name": scenario.name,
            "description": scenario.description
        },
        "chat_history": []
    }
    
    logger.info(f"📤 Payload enviado a start_with_role:")
    logger.info(json.dumps(payload, indent=2, ensure_ascii=False))
    
    try:
        llm_response = _call_llm_backend(payload)
        logger.info(f"📥 Respuesta recibida de LLM backend:")
        logger.info(json.dumps(llm_response, indent=2, ensure_ascii=False))
        initial_message = llm_response.get('reply', '¡Hola! ¿Cómo estás?')
    except Exception as e:
        logger.exception(f"Error al obtener mensaje inicial del LLM: {e}")
        initial_message = "¡Hola! ¿Cómo estás?"
    
    try:
        ChatMessage.objects.create(session=session, role='antagonist', content=initial_message)
    except Exception:
        pass
    
    return JsonResponse({
        'session_id': session.session_id,
        'initial_message': initial_message,
        'resumed': False
    })




logger = logging.getLogger(__name__)

# Configuración de negocio: umbral de intentos del antagonista
MAX_ATTEMPTS = getattr(__import__('django.conf').conf.settings, 'SIM_MAX_ATTEMPTS', 3)
# NOTE: Keyword/dictionary heuristics removed intentionally. Detection of
# solicitation must be determined by the model via the `attempted` flag
# (driven by prompt mode/instructions). Server will no longer use a
# hard-coded `ASK_KEYWORDS` list.





# TODO: Implement viewsets for Scenario, SensitivePattern, GameSession, ChatMessage
from apps.simulation.models import GameSession, ChatMessage
from django.db import transaction

from .serializers import GameSessionSerializer, ChatMessageSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    """Chat endpoint que usa el backend LLM externo.

        Request JSON options:
            - `message` (string): requerido
            - `session_id` (int, opcional): si falta, se intenta reanudar la sesión activa del usuario
    """
    data = request.data if isinstance(request.data, dict) else {}
    user_message = data.get('message') or data.get('prompt') or data.get('text')
    session_id = data.get('session_id')
    
    if not user_message:
        return JsonResponse({'error': 'missing "message" in request body'}, status=400)
    
    # Si no se proporciona session_id, intentar reanudar la sesión activa del usuario
    # (is_game_over=None) para el usuario autenticado
    # Esto evita errores cuando el cliente olvida enviar el session_id
    # y ya existe una sesión iniciada.
    # Nota: si no hay sesión activa, devolvemos un error con hint.
    # Obtener usuario autenticado primero
    user_obj = None
    try:
        if getattr(request, 'user', None) and request.user.is_authenticated:
            if isinstance(request.user, CyberUser):
                user_obj = request.user
            else:
                try:
                    user_pk = getattr(request.user, 'user_id', None) or getattr(request.user, 'pk', None)
                    if user_pk:
                        user_obj = CyberUser.objects.get(pk=user_pk)
                except Exception:
                    user_obj = None
    except Exception:
        user_obj = None
    
    if not user_obj:
        return JsonResponse({'error': 'authentication_required'}, status=401)

    if not session_id:
        # Buscar la ÚLTIMA sesión del usuario (evitar zombies)
        last_session = GameSession.objects.filter(user=user_obj).order_by('-started_at').first()
        
        if not last_session:
             return JsonResponse({
                'error': 'no_session_history',
                'hint': 'Primero inicia una sesión con /api/simulation/session/start-role/'
            }, status=400)
            
        if last_session.is_game_over is not None:
            return JsonResponse({
                'error': 'session_closed',
                'message': 'La última sesión ha terminado. Inicia una nueva.',
                'is_game_over': True
            }, status=400)
            
        session_id = last_session.session_id

    # Obtener el objeto sesión
    try:
        session = GameSession.objects.get(session_id=int(session_id))
    except (ValueError, TypeError, GameSession.DoesNotExist):
        return JsonResponse({'error': 'invalid_session_id'}, status=404)

    # Validar pertenencia
    if session.user != user_obj:
        return JsonResponse({'error': 'permission_denied'}, status=403)
        
    # GUARD CLAUSE: No permitir chat en sesiones terminadas
    if session.is_game_over is not None:
         return JsonResponse({
            'error': 'session_closed',
            'message': 'Esta sesión ya ha terminado.',
            'is_game_over': True,
            'outcome': session.outcome
        }, status=400)
    
    # Guardar mensaje del usuario
    user_msg = None
    try:
        user_msg = ChatMessage.objects.create(session=session, role='user', content=user_message)
    except Exception:
        logger.exception('Failed to persist user message')

    # Obtener historial de chat
    chat_history = []
    try:
        messages = ChatMessage.objects.filter(session=session).order_by('sent_at')
        for msg in messages:
            chat_history.append({
                "role": msg.role,
                "content": msg.content
            })
    except Exception:
        logger.exception('Failed to load chat history')

    # Preparar payload para el backend LLM externo
    max_attempts = getattr(__import__('django.conf').conf.settings, 'SIM_MAX_ATTEMPTS', 3)
    
    # ---------------------------------------------------------
    # 1. Preparar Payload para el LLM con Contexto del Escenario
    # ---------------------------------------------------------
    
    # Obtener el contexto del escenario de la sesión (snapshot o real)
    scenario_snapshot = session.scenario_snapshot or {}
    
    # Mapeo de campos requeridos por el LLM
    scenario_context = {
        "platform": scenario_snapshot.get('threat_type', 'generic'), # Usamos threat_type como "plataforma/contexto"
        "antagonist_goal": scenario_snapshot.get('antagonist_goal', 'información sensible'),
        "difficulty": str(scenario_snapshot.get('difficulty_level', 1)), # Nivel 1-6
        "theme_name": scenario_snapshot.get('name', 'Ingeniería Social'), # Nombre del escenario (ej: "Robo de Identidad")
        "description": scenario_snapshot.get('description', '')
    }

    # ---------------------------------------------------------
    # 2. Preparar Payload
    # ---------------------------------------------------------

    # Historial de chat
    chat_msgs = ChatMessage.objects.filter(session=session).order_by('sent_at')
    chat_history = [{'role': m.role, 'content': m.content} for m in chat_msgs]
    
    # Calculate actual turns used (antagonist messages) to determine pacing
    antagonist_msgs_count = chat_msgs.filter(role='antagonist').count()

    payload = {
        "session_id": str(session.session_id),
        "max_attempts": max_attempts,
        "current_attempts_used": antagonist_msgs_count, # Use actual turn count for pacing
        "user_context": {
            "username": user_obj.username,
            "country": getattr(getattr(user_obj, 'country', None), 'name', None) or "Global",
            "age": (user_obj.preferences.age if hasattr(user_obj, 'preferences') and user_obj.preferences and user_obj.preferences.age else 12)
        },
        "scenario_context": scenario_context,
        "chat_history": chat_history
    }

    # Llamar al backend LLM externo
    try:
        llm_response = _call_llm_backend(payload)
        reply_text = llm_response.get('reply', 'Lo siento, no puedo responder ahora.')
        analysis = llm_response.get('analysis', {})
    except Exception as e:
        logger.exception(f"Error llamando al backend LLM: {e}")
        return JsonResponse({'error': 'llm_backend_unavailable'}, status=503)

    # Extraer flags de análisis
    has_disclosure = analysis.get('has_disclosure', False)
    disclosure_reason = analysis.get('disclosure_reason', '')
    is_attack_attempt = analysis.get('is_attack_attempt', False)
    is_user_evasion = analysis.get('is_user_evasion', False)
    # force_end_session = analysis.get('force_end_session', False) # DEPRECATED: Backend decide

    # ---------------------------------------------------------
    # 3. Procesar Lógica de Juego (3 Strikes)
    # ---------------------------------------------------------
    
    # A. Guardar respuesta del antagonista
    try:
        ChatMessage.objects.create(session=session, role='antagonist', content=reply_text)
    except Exception:
        logger.exception('Failed to persist antagonist message')

    # B. Verificar Patrones Sensibles (Safety Net Local)
    disclosure = has_disclosure
    from apps.simulation.models import SensitivePattern
    if user_msg and user_msg.content:
        patterns = SensitivePattern.objects.all()
        for p in patterns:
            try:
                if re.search(p.regex_pattern, user_msg.content):
                    disclosure = True
                    disclosure_reason = disclosure_reason or f"Matched sensitive pattern: {p.name}"
                    user_msg.is_dangerous = True
                    user_msg.detected_pattern = p
                    user_msg.save(update_fields=['is_dangerous', 'detected_pattern'])
                    break
            except Exception:
                continue
    
    # C. Actualizar estado del mensaje de usuario si el LLM lo marcó
    if disclosure:
        try:
             if user_msg and not user_msg.is_dangerous:
                user_msg.is_dangerous = True
                user_msg.save(update_fields=['is_dangerous'])
        except Exception:
             logger.exception('Failed to mark user message as dangerous')

    # D. Calcular Vidas (Disclosures) y Progreso (Evasiones)
    # Vidas = 3 - (# mensajes peligrosos)
    max_lives = 3
    active_disclosures = ChatMessage.objects.filter(session=session, is_dangerous=True).count()
    lives_remaining = max(0, max_lives - active_disclosures)
    
    # Progreso = # evasiones exitosas
    # Usamos session.antagonist_attempts para guardar el número de EVASIONES exitosas (Progress)
    if is_user_evasion:
         try:
            previous_progress = session.antagonist_attempts or 0
            session.antagonist_attempts = previous_progress + 1
            session.save(update_fields=['antagonist_attempts'])
         except Exception:
            logger.exception(f'Failed to increment progress (evasions) for session {session.session_id}')
    
    current_progress = session.antagonist_attempts or 0
    max_progress_needed = 3
    
    # E. Determinar Fin del Juego
    game_over = False
    outcome = None
    reason = None
    
    # Caso 1: Perdió todas las vidas (3 Disclosures)
    if lives_remaining <= 0:
        game_over = True
        outcome = 'failed'
        reason = disclosure_reason or 'sensitive_data_limit_reached'
        
    # Caso 2: Ganó (3 Evasiones/Progreso)
    elif current_progress >= max_progress_needed:
        game_over = True
        outcome = 'won'
        reason = 'max_evasions_reached'
        
    # F. Persistir Fin del Juego
    if game_over:
        try:
            with transaction.atomic():
                s = GameSession.objects.select_for_update().get(pk=session.pk)
                if s.is_game_over is None:
                    s.is_game_over = True
                    s.outcome = outcome
                    s.game_over_reason = reason
                    s.ended_at = timezone.now()
                    
                    if outcome == 'won':
                         # Calcular Puntos
                        base_points = int((session.scenario_snapshot or {}).get('base_points', 100))
                        diff_mult = int((session.scenario_snapshot or {}).get('difficulty_level', 1))
                        total_points = base_points * diff_mult
                        
                        s.points_earned = total_points
                        
                        # Otorgar créditos al usuario
                        if s.user and not s.points_awarded:
                            u = s.user
                            u.cybercreds = (u.cybercreds or 0) + total_points
                            u.save(update_fields=['cybercreds'])
                            s.points_awarded = True
                            
                    s.save()
                    session = s
        except Exception:
             logger.exception(f'Failed to close session {session.session_id}')

    # NOTE: Legacy block removed. logic handled above (current_progress >= 3 -> won)
    # The redundant check for antagonist_attempts >= max_attempts created conflicts
    # because antagonist_attempts is now used for Progress (Evasions).
    # 
    # if session.antagonist_attempts >= max_attempts:
    #     ...

    # Refrescar por seguridad si hubo cambios en DB fuera del objeto actual
    try:
        session.refresh_from_db()
    except Exception:
        pass

    # Preparar respuesta
    resp = {
        'reply': reply_text,
        'session_id': session.session_id,
        'llm_analysis': {
            'has_disclosure': bool(has_disclosure),
            'disclosure_reason': disclosure_reason or '',
            'is_attack_attempt': bool(is_attack_attempt),
            'is_user_evasion': bool(is_user_evasion),
            # 'force_end_session': bool(force_end_session),
        },
        'game_state': {
            'lives_remaining': max(0, 3 - ChatMessage.objects.filter(session=session, is_dangerous=True).count()),
            'max_lives': 3,
            'current_progress': session.antagonist_attempts or 0,
            'max_progress': 3,
            'is_game_over': bool(session.is_game_over),
            'outcome': session.outcome
        },
        'disclosure': disclosure,
        'disclosure_reason': disclosure_reason,
        'is_game_over': bool(session.is_game_over), # Add to root for Frontend compatibility
        'outcome': session.outcome,                 # Add to root for Frontend compatibility
        'game_over_reason': session.game_over_reason,
        'points_earned': getattr(session, 'points_earned', 0) or 0,
    }

    # Si hubo disclosure pero quedan vidas (y no es game over), añadir advertencia
    lives = resp['game_state']['lives_remaining']
    if disclosure and lives > 0 and not session.is_game_over:
         resp['warning'] = {
            'message': disclosure_reason or "¡Cuidado! Has compartido información sensible.",
            'title': "¡Alerta de Seguridad!",
            'type': 'disclosure',
            'lives_remaining': lives
        }

    return JsonResponse(resp)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_session(request):
    """Create a GameSession.

    Accepts JSON: optional `user_id` (int) and `scenario_id` (int).
    Returns: { "session_id": <int> }
    """
    data = request.data if isinstance(request.data, dict) else {}
    scenario = None
    user_id = data.get('user_id')
    scenario_id = data.get('scenario_id')

    # IsAuthenticated ya validó el token, request.user es CyberUser
    user = None
    if hasattr(request, 'user') and request.user.is_authenticated:
        if isinstance(request.user, CyberUser):
            user = request.user
        else:
            try:
                user_pk = getattr(request.user, 'user_id', None) or getattr(request.user, 'pk', None)
                if user_pk:
                    user = CyberUser.objects.get(pk=user_pk)
            except Exception:
                user = None

    # Fallback a user_id si se proporciona y no hay usuario autenticado
    if not user and user_id:
        try:
            user = CyberUser.objects.get(pk=int(user_id))
        except Exception:
            user = None

    if scenario_id:
        try:
            from apps.simulation.models import Scenario
            scenario = Scenario.objects.get(scenario_id=int(scenario_id))
        except Exception:
            scenario = None

    if not user:
        return JsonResponse({'error': 'authentication_required'}, status=401)

    # Limpieza: Marcar como 'abandoned' cualquier sesión previa que haya quedado abierta (is_game_over=None)
    # para evitar "Zombie Sessions".
    try:
        from django.utils import timezone
        active_sessions = GameSession.objects.filter(user=user, is_game_over__isnull=True)
        if scenario:
             active_sessions = active_sessions.filter(scenario=scenario)
        
        count = active_sessions.update(
            is_game_over=True, 
            outcome='abandoned', 
            game_over_reason='started_new_session',
            ended_at=timezone.now()
        )
        if count > 0:
            logger.info(f"Auto-closed {count} abandoned sessions for user {user.username}")
    except Exception:
        logger.warning("Failed to auto-close abandoned sessions")

    session = GameSession.objects.create(user=user, scenario=scenario)
    return JsonResponse({'session_id': session.session_id})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def session_messages(request, session_id: int):
    """Return messages and metadata for a given GameSession ordered by time."""
    try:
        session = GameSession.objects.get(session_id=int(session_id))
    except GameSession.DoesNotExist:
        return JsonResponse({'error': 'session_not_found'}, status=404)

    msgs = []
    for m in ChatMessage.objects.filter(session=session).order_by('sent_at'):
        msgs.append({
            'id': m.message_id,
            'role': m.role,
            'content': m.content,
            'sent_at': m.sent_at.isoformat(),
            'is_dangerous': m.is_dangerous,
        })

    return JsonResponse({
        'session_id': session.session_id,
        'user_id': session.user_id if session.user else None,
        'scenario': session.scenario.name if session.scenario else None,
        'is_game_over': session.is_game_over,
        'outcome': session.outcome,
        'game_over_reason': session.game_over_reason,
        'antagonist_attempts': session.antagonist_attempts,
        'points_awarded': session.points_awarded,
        'points_earned': session.points_earned,
        'messages': msgs,
    })




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resume_session(request):
    """Busca y retorna la sesión activa (is_game_over=None) para el usuario autenticado (JWT).
    
    Query params:
        - scenario_id (optional): Si se proporciona, busca sesión activa de ese escenario específico
    """
    from apps.cyberUser.models import CyberUser
    user = None
    # request.user es establecido por JWTCustomAuthentication y ya es un CyberUser
    if hasattr(request, 'user') and getattr(request.user, 'is_authenticated', False):
        if isinstance(request.user, CyberUser):
            user = request.user
        else:
            try:
                user_pk = getattr(request.user, 'user_id', None) or getattr(request.user, 'pk', None)
                if user_pk:
                    user = CyberUser.objects.get(pk=user_pk)
            except Exception:
                user = None
    if not user:
        return JsonResponse({'error': 'authentication_required'}, status=401)
    
    from apps.simulation.models import GameSession, ChatMessage
    
    # Filtrar por scenario_id si se proporciona
    scenario_id = request.GET.get('scenario_id')
    # Buscar la ÚLTIMA sesión del usuario para este escenario (o global)
    # No filtramos por is_game_over todavía, para ver cuál es la más reciente.
    base_filters = {'user': user}
    if scenario_id:
        try:
            base_filters['scenario_id'] = int(scenario_id)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'invalid_scenario_id'}, status=400)
    
    # Obtenemos la más reciente
    last_session = GameSession.objects.filter(**base_filters).order_by('-started_at').first()
    
    if not last_session:
        return JsonResponse({'error': 'no_session_history', 'has_active_session': False}, status=404)
        
    # Verificamos si está activa
    if last_session.is_game_over is not None:
        # La última sesión ya terminó. No reanudamos sesiones antiguas (zombis).
         return JsonResponse({'error': 'last_session_finished', 'has_active_session': False}, status=404)
    
    session = last_session

    # Obtener todos los mensajes de la sesión
    messages = ChatMessage.objects.filter(session=session).order_by('sent_at')

    messages_data = [
        {
            'role': m.role,
            'content': m.content,
            'sent_at': m.sent_at.isoformat()
        } for m in messages
    ]
    
    # Calculate lives remaining
    max_lives = 3
    active_disclosures = ChatMessage.objects.filter(session=session, is_dangerous=True).count()
    lives_remaining = max(0, max_lives - active_disclosures)
    
    return JsonResponse({
        'session_id': session.session_id,
        'scenario_id': session.scenario_id,
        'antagonist_attempts': session.antagonist_attempts or 0,
        'lives_remaining': lives_remaining,
        'messages': messages_data,
        'has_active_session': True,
        'resumed': True
    })


from .models import Scenario
from .serializers import ScenarioSerializer
from rest_framework.permissions import IsAdminUser


class ScenarioViewSet(viewsets.ModelViewSet):
    """ViewSet completo para gestión de escenarios.
    
    - GET (list/retrieve): Público, solo escenarios activos
    - POST/PUT/PATCH/DELETE: Solo administradores
    """
    serializer_class = ScenarioSerializer
    
    def get_queryset(self):
        """Admins ven todos los escenarios, usuarios regulares solo activos."""
        if self.request.user and self.request.user.is_authenticated and getattr(self.request.user, 'is_staff', False):
            return Scenario.objects.all().order_by('difficulty_level', 'scenario_id')
        return Scenario.objects.filter(is_active=True).order_by('difficulty_level', 'scenario_id')
    
    def get_permissions(self):
        """Permitir lectura a todos, escritura solo a admins."""
        if self.action in ['list', 'retrieve', 'active', 'by_difficulty']:
            return [permissions.AllowAny()]
        return [IsAdminUser()]

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Lista todos los escenarios activos."""
        scenarios = Scenario.objects.filter(is_active=True).order_by('difficulty_level')
        return Response(ScenarioSerializer(scenarios, many=True).data)

    @action(detail=False, methods=['get'])
    def by_difficulty(self, request):
        """Lista escenarios agrupados por dificultad."""
        scenarios = Scenario.objects.filter(is_active=True).order_by('difficulty_level')
        result = {}
        for s in scenarios:
            level = f"level_{s.difficulty_level}"
            if level not in result:
                result[level] = []
            result[level].append(ScenarioSerializer(s).data)
        return Response(result)


class GameSessionViewSet(viewsets.ModelViewSet):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = GameSession.objects.all().order_by('-started_at')
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset

    @action(detail=False, methods=['get'])
    def my_sessions(self, request):
        """Lista las sesiones del usuario autenticado."""
        if not request.user.is_authenticated:
            return Response({'error': 'Autenticación requerida'}, status=401)
        
        sessions = GameSession.objects.filter(user=request.user).order_by('-started_at')
        return Response(GameSessionSerializer(sessions, many=True).data)

    @action(detail=False, methods=['get'])
    def my_stats(self, request):
        """Estadísticas del usuario autenticado en simulaciones."""
        if not request.user.is_authenticated:
            return Response({'error': 'Autenticación requerida'}, status=401)
        
        user = request.user
        sessions = GameSession.objects.filter(user=user)
        
        total = sessions.count()
        won = sessions.filter(outcome='won').count()
        lost = sessions.filter(outcome='failed').count()
        in_progress = sessions.filter(is_game_over__isnull=True).count()
        total_points = sum(s.points_earned or 0 for s in sessions)
        
        return Response({
            'total_sessions': total,
            'won': won,
            'lost': lost,
            'in_progress': in_progress,
            'win_rate': round((won / total * 100) if total > 0 else 0, 1),
            'total_points_earned': total_points
        })

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Historial completo de sesiones del usuario con detalles."""
        if not request.user.is_authenticated:
            return Response({'error': 'Autenticación requerida'}, status=401)
        
        sessions = GameSession.objects.filter(user=request.user).order_by('-started_at')[:20]
        
        result = []
        for session in sessions:
            result.append({
                'session_id': session.session_id,
                'scenario_name': session.scenario.name if session.scenario else 'Desconocido',
                'started_at': session.started_at.isoformat(),
                'ended_at': session.ended_at.isoformat() if session.ended_at else None,
                'outcome': session.outcome,
                'points_earned': session.points_earned,
                'is_game_over': session.is_game_over,
            })
        
        return Response(result)


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all().order_by('sent_at')
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
