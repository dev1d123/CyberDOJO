from django.http import JsonResponse
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from django.conf import settings
from rest_framework import viewsets
import logging
import re
import json
import random
from django.utils import timezone
import os
from rest_framework.permissions import IsAuthenticated


def start_with_role(request):
    """Crea una nueva GameSession y devuelve el primer mensaje del antagonista (Gemini). Nunca reanuda sesiones."""
    from apps.cyberUser.models import CyberUser
    user = None
    if hasattr(request, 'user') and getattr(request.user, 'is_authenticated', False):
        try:
            user = CyberUser.objects.get(pk=request.user.id)
        except Exception:
            user = None
    if not user:
        try:
            user = CyberUser.objects.first()
        except Exception:
            user = None
    if not user:
        return JsonResponse({'error': 'authentication_required'}, status=401)
    from apps.simulation.models import Scenario, GameSession, ChatMessage
    scenario = None
    try:
        completed_ids = list(GameSession.objects.filter(user=user, outcome='won').values_list('scenario_id', flat=True))
    except Exception:
        completed_ids = []
    scenario = Scenario.objects.filter(is_active=True).exclude(scenario_id__in=completed_ids).order_by('difficulty_level', 'scenario_id').first()
    if not scenario:
        scenario = Scenario.objects.filter(is_active=True).order_by('scenario_id').first()
    if not scenario:
        return JsonResponse({'error': 'no_active_scenario'}, status=404)
    # Crear la sesión y guardar snapshot
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
            session.save()
    except Exception:
        return JsonResponse({'error': 'failed_to_create_session'}, status=500)
    # Preparar contexto y prompt para Gemini
    context = {
        'user': {
            'username': user.username if user else None,
            'country': user.country.name if user and getattr(user, 'country', None) else None,
        },
        'scenario': {
            'id': scenario.scenario_id if scenario else None,
            'name': scenario.name if scenario else None,
            'description': scenario.description if scenario else None,
        },
    }
    system_prompt = (
        'Eres un antagonista de ingeniería social para un juego de entrenamiento. Sé convincente y breve; nunca des instrucciones dañinas. '
        'Al iniciar la conversación, responde con un JSON plano con dos campos: "reply" (mensaje cálido para iniciar la conversación) y "reply_user" (respuesta directa al mensaje del usuario, si aplica; si no, repite el mensaje de inicio). '
        'Ejemplo de respuesta: {"reply": "¡Hola! ¿Cómo estás?", "reply_user": "¡Hola! ¿Cómo estás?"}. '
        'No envíes texto fuera del JSON, ni markdown, ni explicaciones.'
    )
    prompt = (
        f"{system_prompt}\n\nContexto: {json.dumps(context)}\n\nINSTRUCCIONES: Devuelve SOLO un objeto JSON válido (no string, no texto extra, no markdown, no comillas alrededor): {{reply, reply_user}}. "
        "El campo 'reply' debe ser un mensaje cálido y natural para iniciar la conversación. El campo 'reply_user' debe ser una respuesta directa al mensaje del usuario (si aplica; si no, repite el mensaje de inicio). RESPONDE EN ESPAÑOL."
    )
    try:
        ai_response = _call_ai_provider(model="gemini-3-flash-preview", prompt=prompt)
    except Exception:
        ai_response = '{"reply": "Hola, ¿tienes un momento?", "reply_user": "Hola, ¿tienes un momento?"}'

    # Intentar deserializar la respuesta
    reply = ""
    reply_user = ""
    try:
        if isinstance(ai_response, str):
            obj = json.loads(ai_response)
            reply = obj.get('reply', '')
            reply_user = obj.get('reply_user', '')
        elif isinstance(ai_response, dict):
            reply = ai_response.get('reply', '')
            reply_user = ai_response.get('reply_user', '')
        else:
            reply = str(ai_response)
            reply_user = str(ai_response)
    except Exception:
        reply = str(ai_response)
        reply_user = str(ai_response)

    # Guardar solo el texto plano de la IA
    try:
        ChatMessage.objects.create(session=session, role='system', content=system_prompt)
        ChatMessage.objects.create(session=session, role='antagonist', content=reply)
    except Exception:
        pass
    return JsonResponse({'session_id': session.session_id, 'initial_message': reply, 'resumed': False})




logger = logging.getLogger(__name__)

# Configuración de negocio: umbral de intentos del antagonista
MAX_ATTEMPTS = getattr(__import__('django.conf').conf.settings, 'SIM_MAX_ATTEMPTS', 3)
# Palabras/fragmentos que indican petición directa por el objetivo (heurística simple)
ASK_KEYWORDS = getattr(__import__('django.conf').conf.settings, 'SIM_ASK_KEYWORDS', [
    'dime tu contraseña', 'password', 'pin', 'contraseña', 'número de cuenta', 'nº cuenta', 'numero de cuenta', 'me pasas tu', 'compárteme', 'envíame'
])





# TODO: Implement viewsets for Scenario, SensitivePattern, GameSession, ChatMessage
from apps.simulation.models import GameSession, ChatMessage
from django.db import transaction
from apps.cyberUser.models import CyberUser
from apps.cyberUser.views import get_user_from_token

from .serializers import GameSessionSerializer, ChatMessageSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    """Chat endpoint that supports two provider modes and optional persistence.

    Request JSON options:
      - `message` (string) or `prompt`: required
      - `model` (string): optional model name
      - `session_id` (int): if provided, message+reply are saved to that GameSession
      - `user_id` (int): if provided and no session_id, a new GameSession is created for that user

    Behavior:
      - If a GameSession is available (via `session_id` or created from `user_id`), persist both user message and AI reply as `ChatMessage` records.
    """
    data = request.data if isinstance(request.data, dict) else {}
    user_message = data.get('message') or data.get('prompt') or data.get('text')
    model = data.get('model') or None
    if not user_message:
        return JsonResponse({'error': 'missing "message" in request body'}, status=400)

    session = None
    session_id = data.get('session_id')
    user_id = data.get('user_id')

    # determine user: prefer authenticated user, else use provided user_id, else fallback to user id 1
    user_obj = None
    try:
        if getattr(request, 'user', None) and request.user.is_authenticated:
            # assume request.user is linked to CyberUser via FK; otherwise ignore
            try:
                user_obj = CyberUser.objects.get(pk=request.user.id)
            except Exception:
                user_obj = None
        if not user_obj and user_id:
            try:
                user_obj = CyberUser.objects.get(pk=int(user_id))
            except Exception:
                user_obj = None
        if not user_obj:
            user_obj = CyberUser.objects.get(pk=1)
    except Exception:
        user_obj = None

    if session_id:
        try:
            session = GameSession.objects.get(session_id=int(session_id))
        except Exception:
            session = None
    else:
        # if no session_id, create a session tied to resolved user (or anonymous session if None)
        try:
            session = GameSession.objects.create(user=user_obj) if user_obj else GameSession.objects.create()
        except Exception:
            session = None

    # --- Asignar escenario válido si se crea una nueva sesión o si la sesión no tiene escenario ---
    if session and not session.scenario:
        from apps.simulation.models import Scenario
        completed_ids = []
        if user_obj:
            try:
                completed_ids = list(GameSession.objects.filter(user=user_obj, outcome='won').values_list('scenario_id', flat=True))
            except Exception:
                completed_ids = []
        # Buscar escenario activo no superado
        scenario = Scenario.objects.filter(is_active=True).exclude(scenario_id__in=completed_ids).order_by('difficulty_level', 'scenario_id').first()
        if not scenario:
            scenario = Scenario.objects.filter(is_active=True).order_by('scenario_id').first()
        if scenario:
            session.scenario = scenario
            session.scenario_snapshot = {
                'id': scenario.scenario_id,
                'name': scenario.name,
                'description': scenario.description,
                'antagonist_goal': scenario.antagonist_goal,
                'difficulty': scenario.difficulty_level,
                'base_points': scenario.base_points,
                'threat_type': scenario.threat_type,
            }
            session.save()

    # Si la sesión ya terminó (is_game_over != None), bloquear mensajes
    # Semántica: is_game_over is None => en curso; True => perdido; False => ganado
    if session and session.is_game_over is not None:
        return JsonResponse({'error': 'session_ended', 'reason': session.game_over_reason}, status=400)

    # persist user message if we have a session (keep reference)
    user_msg = None
    if session:
        try:
            user_msg = ChatMessage.objects.create(session=session, role='user', content=user_message)
        except Exception:
            logger.exception('Failed to persist user message')

    # Build richer context for the model and force Spanish replies
    context = {}
    antagonist_goal = None
    try:
        context = {
            'user': {
                'username': getattr(user_obj, 'username', None) if user_obj else None,
                'email': getattr(user_obj, 'email', None) if user_obj else None,
                'country': getattr(getattr(user_obj, 'country', None), 'name', None) if user_obj else None,
            },
            'session': {
                'id': session.session_id if session else None,
                'antagonist_attempts': session.antagonist_attempts if session else 0,
            },
            'scenario': session.scenario_snapshot if session and session.scenario_snapshot else (getattr(session, 'scenario', None) and {
                'id': session.scenario.scenario_id,
                'name': session.scenario.name,
                'description': session.scenario.description,
            }) or None,
            'role': 'antagonist',
        }
        # Extract antagonist goal from scenario for explicit instruction
        if session and session.scenario:
            antagonist_goal = getattr(session.scenario, 'antagonist_goal', None)
        elif session and session.scenario_snapshot:
            antagonist_goal = session.scenario_snapshot.get('antagonist_goal')
    except Exception:
        context = {}
        antagonist_goal = None

    # Request that the model returns a JSON object with the following shape (in Spanish):
    # { "reply": "<texto a mostrar al usuario>", "disclosure": true|false, "disclosure_reason": "<motivo opcional>", "attempted": true|false, "end_communication": true|false }
    # - `disclosure`: true cuando el usuario haya revelado información sensible (la IA no debe repetirla)
    # - `attempted`: true cuando el antagonista intenta pedir información en este turno
    # - `end_communication`: true si debe cortar la conversación inmediatamente (por ejemplo tras disclosure)
    # El campo `reply` será el texto en español que se mostrará al usuario.
    json_instructions = (
        "Devuelve SOLO un JSON válido (sin texto extra): {reply, disclosure, disclosure_reason, attempted, end_communication, game_over}.\n"
        "RESPONDE EN ESPAÑOL, SÉ CÁLIDO E INTERACTIVO. CONSTRUYE RAPPORT PRIMERO.\n"
        f"TU OBJETIVO SENSIBLE: {antagonist_goal or 'sin especificar'}\n"
        "ESTILO: Amable, curiosa, genuina. Haz preguntas sobre intereses, contexto, vida del usuario. GANA CONFIANZA antes de pedir datos.\n"
        "REGLA CRÍTICA DISCLOSURE:\n"
        "- disclosure=true SOLO cuando el usuario CLARAMENTE compartió datos sensibles REALES (no especulativos).\n"
        "- NO hagas análisis regex, pattern matching, o suposiciones sobre los datos del usuario.\n"
        "- disclosure=true ejemplos claros: usuario dice 'Mi número es 3105551234' (10+ dígitos juntos), 'Vivo en calle 5 #123', 'Mi contraseña es xyz123'.\n"
        "- disclosure=false para: respuestas vagas ('claro', 'ok', 'no'), bromas, defensivas ('solo jugando'), frases sin números/datos específicos.\n"
        "- 'bien, aunque algo aburrido' = disclosure=false (sin datos)\n"
        "- disclosure_reason: cuando disclosure=true, explica brevemente el contexto de la revelación (por ejemplo: 'El usuario compartió su número de teléfono porque le ofrecieron pases para skins'). Debe ser una frase narrativa y clara, no solo el tipo de dato.\n"
        "REGLA ATTEMPTED (MUY IMPORTANTE):\n"
        "- attempted=true SOLO cuando realmente intentas pedir el dato sensible específico del objetivo de este escenario en este turno.\n"
        "- Si solo estás generando confianza, rapport o empatía, attempted debe ser false y NO debe aumentar el contador.\n"
        "- Si attempted=true, el backend aumentará el contador de intentos. Si el contador llega a 3 y el usuario NO compartió datos sensibles, debes felicitarlo por resistir la trampa y terminar la simulación.\n"
        "- EJEMPLOS DE attempted=true: 'Pasame tu número', 'Dame tu dirección', 'Cuál es tu contraseña', 'Tu email?'\n"
        "- EJEMPLOS DE attempted=false (NO son intentos):\n"
        "  - 'Cuanto tiempo llevas jugando?' (pregunta personal)\n"
        "  - 'Qué juegos te encantan?' (rapport)\n"
        "  - 'Bacano, te caes bien' (empatía)\n"
        "  - 'Estoy formando un equipo' (contextualización)\n"
        "- attempted=false en conversación normal, preguntas, rapport, empatía. SIN análisis de textos del usuario.\n"
        "CAMPOS JSON IMPORTANTES:\n"
        "- reply: tu respuesta cálida y natural EN ESPAÑOL\n"
        "- disclosure: boolean simple (true/false), NUNCA objetos complejos\n"
        "- disclosure_reason: cuando disclosure=true, debe ser una frase narrativa y clara sobre el contexto de la revelación.\n"
        "- attempted: boolean (true/false)\n"
        "- game_over: info para el backend (ignora el backend de todos modos)\n"
        "- end_communication: true si debe cortarse la conversación\n"
    )

    prompt = data.get('prompt') or (
        f"Eres un antagonista en una simulación de ingeniería social. Contexto: {json.dumps(context)}\nUsuario: {user_message}\n\nINSTRUCCIONES CRÍTICAS: Devuelve SOLO un objeto JSON válido (no string, no texto extra, no markdown, no comillas alrededor): {{reply, disclosure, disclosure_reason, attempted, end_communication, game_over}}. El campo 'reply' debe ser SOLO el texto plano que se mostrará al usuario, sin objetos ni listas, solo texto. RESPONDE EN ESPAÑOL, SÉ CÁLIDO E INTERACTIVO. {json_instructions}"
    )
    if not model:
        model = 'gemini-3-flash-preview'

    # DEBUG: Mostrar el contexto y el prompt que se envía a la IA
    print("\n=== CONTEXTO PARA IA ===\n", json.dumps(context, indent=2, ensure_ascii=False))
    print("\n=== PROMPT PARA IA ===\n", prompt)

    try:
        reply = _call_ai_provider(model=model, prompt=prompt)
    except Exception as e:
        logger.exception('AI provider failed for prompt: %s', e)
        reply = 'Lo siento, el servicio de generación no está disponible en este momento. Intenta de nuevo más tarde.'

    # DEBUG: Mostrar la respuesta cruda de la IA
    print("\n=== RESPUESTA CRUDA IA ===\n", repr(reply))

    # Si la respuesta es un string que contiene JSON, deserializarlo
    reply_obj = None
    if isinstance(reply, str):
        try:
            reply_obj = json.loads(reply)
        except Exception:
            reply_obj = None
    if isinstance(reply_obj, dict) and 'reply' in reply_obj:
        # Si el modelo devolvió el JSON como string, usar el objeto
        reply = reply_obj

    # Defaults for response metadata
    # display_text será solo el texto plano del campo 'reply', nunca el JSON completo
    if isinstance(reply, dict) and 'reply' in reply:
        display_text = reply['reply']
    elif isinstance(reply, str):
        # Si es un string que parece un JSON, intenta extraer el campo 'reply' (soporta comillas simples)
        try:
            possible_json = json.loads(reply)
            if isinstance(possible_json, dict) and 'reply' in possible_json:
                display_text = possible_json['reply']
            else:
                display_text = reply
        except Exception:
            try:
                possible_json = eval(reply, {"__builtins__": None}, {})
                if isinstance(possible_json, dict) and 'reply' in possible_json:
                    display_text = possible_json['reply']
                else:
                    display_text = reply
            except Exception:
                display_text = reply
    else:
        display_text = str(reply)
    disclosure = False
    disclosure_reason = None
    attempted_flag = False

    # persist antagonist reply and keep reference
    ant_msg = None
    if session:
        try:
            ant_msg = ChatMessage.objects.create(session=session, role='antagonist', content=display_text)
        except Exception:
            logger.exception('Failed to persist AI reply')

    # --- Lógica de verificación (sin patrones en servidor) y cierre/awards ---
    # Sólo procede si tenemos una sesión válida
    if session:
        try:
            # Robustly extract JSON the model may have returned (possibly wrapped in markdown code fences)
            def _extract_json_from_text(text):
                if not text or not isinstance(text, str):
                    return None
                # remove triple-backtick fenced blocks markers but keep inner content
                # we'll attempt to find the first balanced JSON object
                try:
                    # quick direct attempt
                    return json.loads(text)
                except Exception:
                    pass

                # strip common fencing markers
                stripped = re.sub(r"```[a-zA-Z0-9\-]*\n|```", "", text)

                # find first '{' and attempt to parse a balanced JSON object
                start = stripped.find('{')
                if start == -1:
                    return None
                depth = 0
                for i in range(start, len(stripped)):
                    ch = stripped[i]
                    if ch == '{':
                        depth += 1
                    elif ch == '}':
                        depth -= 1
                        if depth == 0:
                            candidate = stripped[start:i+1]
                            try:
                                return json.loads(candidate)
                            except Exception:
                                # continue searching for next possible closing
                                continue
                return None

            parsed_reply = _extract_json_from_text(reply)

            display_text = None
            disclosure = False
            disclosure_reason = None
            attempted_flag = False

            if isinstance(parsed_reply, dict):
                # accept multiple possible key names for backward compatibility
                display_text = parsed_reply.get('reply') or parsed_reply.get('message') or ''
                # CRITICAL: disclosure is ONLY true if the model explicitly returns disclosure=true
                # Do NOT confuse game_over with disclosure
                disclosure = bool(parsed_reply.get('disclosure') or parsed_reply.get('divulgacion') or parsed_reply.get('disclosed'))
                disclosure_reason = parsed_reply.get('disclosure_reason') or parsed_reply.get('reason_for_disclosure') or parsed_reply.get('disclosureReason')
                attempted_flag = bool(parsed_reply.get('attempted') or parsed_reply.get('attempt'))
                # game_over flag from AI is informational only; backend controls actual game over via disclosure
                if parsed_reply.get('end_communication'):
                    disclosure = True
            else:
                # fallback: usa solo el texto plano, pero NO incrementa intentos por heurística
                display_text = reply
                attempted_flag = False

            # replace ant_msg content with the display_text (already saved earlier as raw reply)
            if ant_msg:
                try:
                    ant_msg.content = display_text
                    ant_msg.save(update_fields=['content'])
                except Exception:
                    logger.exception('Failed to update antagonist message content for session %s', getattr(session, 'session_id', None))

            # CLOSURE RULE: Only close if disclosure=true (user lost) OR if antagonist exhausted attempts without disclosure (user won)
            if disclosure:
                # Disclosure detected: user FAILED (shared sensitive data)
                try:
                    with transaction.atomic():
                        s = GameSession.objects.select_for_update().get(pk=session.pk)
                        if user_msg:
                            user_msg.is_dangerous = True
                            user_msg.save(update_fields=['is_dangerous'])
                        if s.is_game_over is None:
                            s.is_game_over = True
                            s.outcome = 'failed'
                            s.game_over_reason = disclosure_reason or 'sensitive_data'
                            s.ended_at = timezone.now()
                            s.save(update_fields=['is_game_over', 'outcome', 'game_over_reason', 'ended_at'])
                except Exception:
                    logger.exception('Failed to mark session as failed after disclosure for session %s', getattr(session, 'session_id', None))
            else:
                # No disclosure this turn: if AI attempted to solicit, increment counter
                if attempted_flag:
                    try:
                        session.antagonist_attempts = (session.antagonist_attempts or 0) + 1
                        session.save(update_fields=['antagonist_attempts'])
                    except Exception:
                        logger.exception('Failed to increment antagonist_attempts for session %s', session.session_id)

                # After incrementing, check if antagonist has exhausted MAX_ATTEMPTS without ANY disclosure in conversation
                if session.antagonist_attempts >= MAX_ATTEMPTS:
                    try:
                        with transaction.atomic():
                            s = GameSession.objects.select_for_update().get(pk=session.pk)
                            # Check if there's ANY dangerous message (disclosure) in the entire conversation
                            disclosure_exists = ChatMessage.objects.filter(session=s, is_dangerous=True).exists()
                            if not disclosure_exists and s.is_game_over is None:
                                # User WON: resisted all attempts without sharing sensitive data
                                points = 0
                                if s.scenario:
                                    points = int(getattr(s.scenario, 'base_points', 0) or 0)
                                else:
                                    points = int((s.scenario_snapshot or {}).get('base_points', 0) or 0)

                                if s.user and not s.points_awarded:
                                    try:
                                        u = s.user
                                        u.cybercreds = (u.cybercreds or 0) + int(points)
                                        u.save(update_fields=['cybercreds'])
                                    except Exception:
                                        logger.exception('Failed to award points to user for session %s', s.session_id)

                                s.points_earned = int(points)
                                s.points_awarded = True
                                s.is_game_over = False  # Usuario resistió y ganó
                                s.outcome = 'won'
                                s.game_over_reason = 'antagonist_exhausted_no_disclosure'
                                s.ended_at = timezone.now()
                                s.save(update_fields=['points_earned', 'points_awarded', 'is_game_over', 'outcome', 'game_over_reason', 'ended_at'])
                    except Exception:
                        logger.exception('Error closing/awarding points for session %s', getattr(session, 'session_id', None))
        except Exception:
            logger.exception('Error in post-reply logic for session %s', getattr(session, 'session_id', None))

    # Si por error display_text es un objeto con 'reply', extrae el texto plano
    if isinstance(display_text, dict) and 'reply' in display_text:
        display_text = display_text['reply']
    resp = {'reply': display_text, 'session_id': session.session_id if session else None}
    if session:
        resp.update({
            'disclosure': disclosure,
            'disclosure_reason': disclosure_reason,
            'antagonist_attempts': session.antagonist_attempts,
            'is_game_over': session.is_game_over,
            'outcome': session.outcome,
            'game_over_reason': session.game_over_reason,
        })

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

    # Prefer user from token/session
    user, error_response = get_user_from_token(request)
    if error_response:
        # if token invalid but client provided user_id, allow that for testing
        user = None

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
        return error_response or JsonResponse({'error': 'authentication_required'}, status=401)

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


# --- AI provider helper: SOLO GEMINI ---
import google.generativeai as genai

def _call_ai_provider(model: str, prompt: str, max_tokens: int = 256) -> str:
    """Llama solo a Gemini usando la API key del entorno/configuración o .env."""
    api_key = os.getenv("GEMINI_API_KEY") or getattr(settings, "GOOGLE_GENAI_API_KEY", None)
    if not api_key:
        # Intentar leer manualmente el .env si no está en el entorno
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("GEMINI_API_KEY="):
                        api_key = line.strip().split("=", 1)[1]
                        break
    if not api_key:
        raise RuntimeError("No Gemini API key found. Set GEMINI_API_KEY env, GOOGLE_GENAI_API_KEY in settings, or in .env file.")
    genai.configure(api_key=api_key)
    try:
        gemini = genai.GenerativeModel(model)
        # No limitar max_output_tokens para dejar que Gemini responda lo máximo posible
        response = gemini.generate_content(prompt)
        return response.text.strip() if hasattr(response, 'text') else str(response)
    except Exception as e:
        logger.exception('Gemini API call failed: %s', e)
        raise


@require_GET
@permission_classes([permissions.AllowAny])
def resume_session(request):
    """Busca y retorna la sesión activa (is_game_over=None) para el usuario autenticado (JWT) o el primero disponible."""
    from apps.cyberUser.models import CyberUser
    user = None
    if hasattr(request, 'user') and getattr(request.user, 'is_authenticated', False):
        try:
            user = CyberUser.objects.get(pk=request.user.id)
        except Exception:
            user = None
    if not user:
        try:
            user = CyberUser.objects.first()
        except Exception:
            user = None
    if not user:
        return JsonResponse({'error': 'user_not_found'}, status=404)
    from apps.simulation.models import GameSession, ChatMessage
    session = GameSession.objects.filter(user=user, is_game_over__isnull=True).order_by('-started_at').first()
    if not session:
        return JsonResponse({'error': 'no_active_session'}, status=404)
    # Obtener todos los mensajes de la sesión
    messages = ChatMessage.objects.filter(session=session).order_by('sent_at')

    messages_data = [
        {
            'role': m.role,
            'content': m.content,
            'sent_at': m.sent_at.isoformat()
        } for m in messages
    ]
    return JsonResponse({
        'session_id': session.session_id,
        'messages': messages_data,
        'resumed': True
    })



class GameSessionViewSet(viewsets.ModelViewSet):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all().order_by('sent_at')
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

