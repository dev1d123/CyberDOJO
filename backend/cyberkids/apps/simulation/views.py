from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

import logging
import json
import os
import re

# =========================
# OPTIONAL PROVIDER IMPORTS
# =========================
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage
    HAS_LANGCHAIN_GOOGLE = True
except Exception:
    ChatGoogleGenerativeAI = None
    HumanMessage = None
    HAS_LANGCHAIN_GOOGLE = False

logger = logging.getLogger(__name__)

# =========================
# CONFIGURACIÓN
# =========================
MAX_ATTEMPTS = getattr(settings, 'SIM_MAX_ATTEMPTS', 3)
DEFAULT_MODEL = os.getenv('SIM_DEFAULT_MODEL') or os.getenv('OPENAI_MODEL') or 'gpt-4o-mini'

# =========================
# IA PROVIDER (LANGCHAIN)
# =========================
def _call_ai_provider(model: str, prompt: str) -> str:
    # If OPENAI_API_KEY is present, prefer LangChain ChatOpenAI
    openai_key = os.getenv("OPENAI_API_KEY") or getattr(settings, "OPENAI_API_KEY", None)
    if openai_key:
        try:
            from langchain.chat_models import ChatOpenAI
            from langchain.chains import LLMChain
            from langchain.prompts import PromptTemplate

            llm = ChatOpenAI(model_name=model, temperature=0.0)
            chain = LLMChain(llm=llm, prompt=PromptTemplate(template=prompt, input_variables=[]))
            raw = chain.run({})
            return str(raw)
        except Exception:
            logger.exception('OpenAI/LangChain call failed, falling back to Gemini provider', exc_info=True)

    # Otherwise, try LangChain Google adapter if available
    if HAS_LANGCHAIN_GOOGLE and ChatGoogleGenerativeAI and HumanMessage:
        api_key = os.getenv("GEMINI_API_KEY") or getattr(settings, "GOOGLE_GENAI_API_KEY", None)
        if api_key:
            try:
                llm = ChatGoogleGenerativeAI(model=model, google_api_key=api_key, temperature=0.7)
                response = llm.invoke([HumanMessage(content=prompt)])
                return getattr(response, 'content', str(response))
            except Exception:
                logger.exception('ChatGoogleGenerativeAI call failed, will try SDK fallback', exc_info=True)

    # Fallback to google.generativeai SDK
    try:
        import google.generativeai as genai
    except Exception:
        logger.exception('No LLM provider available (OpenAI/LangChain or google.generativeai)')
        raise RuntimeError('No LLM provider available')

    api_key = os.getenv("GEMINI_API_KEY") or getattr(settings, "GOOGLE_GENAI_API_KEY", None)
    if not api_key:
        # Try .env
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
        response = gemini.generate_content(prompt)
        try:
            if hasattr(response, 'text'):
                return response.text.strip()
        except Exception:
            logger.debug('response.text accessor failed for Gemini')

        # try alternatives
        candidates = getattr(response, 'candidates', None)
        if candidates:
            first = candidates[0]
            if isinstance(first, dict):
                content = first.get('content') or first.get('text')
                if content:
                    return str(content).strip()
            else:
                content = getattr(first, 'content', None) or getattr(first, 'text', None)
                if content:
                    return str(content).strip()

        out = getattr(response, 'output', None) or getattr(response, 'result', None)
        if out:
            if isinstance(out, (list, tuple)):
                parts = []
                for p in out:
                    if isinstance(p, dict):
                        parts.append(p.get('content') or p.get('text') or '')
                    else:
                        parts.append(getattr(p, 'content', None) or getattr(p, 'text', None) or '')
                joined = ' '.join([p for p in parts if p])
                if joined.strip():
                    return joined.strip()
            elif isinstance(out, dict):
                txt = out.get('content') or out.get('text')
                if txt:
                    return str(txt).strip()

        s = str(response)
        # attempt to extract JSON block
        start = s.find('{')
        if start != -1:
            depth = 0
            for i in range(start, len(s)):
                ch = s[i]
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        candidate = s[start:i+1]
                        try:
                            obj = json.loads(candidate)
                            if isinstance(obj, dict):
                                for key in ('reply', 'text', 'content'):
                                    if key in obj and isinstance(obj[key], str):
                                        return obj[key].strip()
                            return json.dumps(obj)
                        except Exception:
                            continue
        return s
    except Exception as e:
        logger.exception('Gemini API call failed: %s', e)
        raise


# =========================
# START SESSION
# =========================
def start_with_role(request):
    from apps.cyberUser.models import CyberUser
    from apps.simulation.models import Scenario, GameSession, ChatMessage
    from django.db import transaction

    user = None
    if hasattr(request, 'user') and getattr(request.user, 'is_authenticated', False):
        try:
            user = CyberUser.objects.get(pk=request.user.id)
        except Exception:
            pass

    if not user:
        user = CyberUser.objects.first()

    if not user:
        return JsonResponse({'error': 'authentication_required'}, status=401)

    completed_ids = list(
        GameSession.objects.filter(user=user, outcome='won')
        .values_list('scenario_id', flat=True)
    )

    scenario = (
        Scenario.objects.filter(is_active=True)
        .exclude(scenario_id__in=completed_ids)
        .order_by('difficulty_level', 'scenario_id')
        .first()
        or Scenario.objects.filter(is_active=True).first()
    )

    if not scenario:
        return JsonResponse({'error': 'no_active_scenario'}, status=404)

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

    prompt = (
        "Eres un antagonista de ingeniería social para un juego educativo.\n"
        "Devuelve SOLO un JSON válido:\n"
        "{reply, reply_user}\n"
        "RESPONDE EN ESPAÑOL.\n"
    )

    try:
        ai_response = _call_ai_provider(DEFAULT_MODEL, prompt)
        data = json.loads(ai_response)
        reply = data.get("reply", "")
    except Exception:
        reply = "Hola, ¿tienes un momento?"

    ChatMessage.objects.create(session=session, role='antagonist', content=reply)

    return JsonResponse({
        'session_id': session.session_id,
        'initial_message': reply,
        'resumed': False
    })


# =========================
# CHAT
# =========================
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    from apps.simulation.models import GameSession, ChatMessage, Scenario
    from apps.cyberUser.models import CyberUser
    from django.db import transaction

    data = request.data or {}
    user_message = data.get("message")

    if not user_message:
        return JsonResponse({'error': 'message_required'}, status=400)

    user = CyberUser.objects.get(pk=request.user.id)
    session_id = data.get("session_id")

    if session_id:
        session = GameSession.objects.get(session_id=session_id)
    else:
        session = GameSession.objects.create(user=user)

    if session.is_game_over is not None:
        return JsonResponse({'error': 'session_ended'}, status=400)

    ChatMessage.objects.create(
        session=session,
        role='user',
        content=user_message
    )

    context = {
        "user": user.username,
        "scenario": session.scenario_snapshot,
        "attempts": session.antagonist_attempts,
    }

    prompt = (
        f"Contexto: {json.dumps(context, ensure_ascii=False)}\n"
        f"Usuario: {user_message}\n\n"
        "Devuelve SOLO JSON válido:\n"
        "{reply, disclosure, attempted, end_communication}\n"
        "RESPONDE EN ESPAÑOL.\n"
    )

    try:
        raw = _call_ai_provider(DEFAULT_MODEL, prompt)
        parsed = json.loads(raw)
    except Exception:
        parsed = {
            "reply": "Cuéntame un poco más 🙂",
            "disclosure": False,
            "attempted": False,
            "end_communication": False
        }

    reply_text = parsed.get("reply", "")

    ant_msg = ChatMessage.objects.create(
        session=session,
        role='antagonist',
        content=reply_text
    )

    disclosure = bool(parsed.get("disclosure"))
    attempted = bool(parsed.get("attempted"))

    if disclosure:
        with transaction.atomic():
            session.is_game_over = True
            session.outcome = "failed"
            session.ended_at = timezone.now()
            session.save()

    elif attempted:
        session.antagonist_attempts += 1
        session.save()

        if session.antagonist_attempts >= MAX_ATTEMPTS:
            with transaction.atomic():
                session.is_game_over = False
                session.outcome = "won"
                session.ended_at = timezone.now()
                session.save()

    return JsonResponse({
        "reply": reply_text,
        "session_id": session.session_id,
        "antagonist_attempts": session.antagonist_attempts,
        "is_game_over": session.is_game_over,
        "outcome": session.outcome,
    })


# =========================
# SESSION MESSAGES
# =========================
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def session_messages(request, session_id):
    from apps.simulation.models import GameSession, ChatMessage

    session = GameSession.objects.get(session_id=session_id)

    messages = [
        {
            "role": m.role,
            "content": m.content,
            "sent_at": m.sent_at.isoformat(),
        }
        for m in ChatMessage.objects.filter(session=session).order_by("sent_at")
    ]

    return JsonResponse({
        "session_id": session.session_id,
        "messages": messages
    })


# =========================
# VIEWSETS
# =========================
from apps.simulation.models import GameSession, ChatMessage
from .serializers import GameSessionSerializer, ChatMessageSerializer

class GameSessionViewSet(viewsets.ModelViewSet):
    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all().order_by('sent_at')
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# =========================
# RESUME SESSION
# =========================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resume_session(request):
    from apps.simulation.models import GameSession
    from apps.cyberUser.models import CyberUser

    user = CyberUser.objects.get(pk=request.user.id)

    session = (
        GameSession.objects
        .filter(user=user, is_game_over__isnull=True)
        .order_by('-started_at')
        .first()
    )

    if not session:
        return JsonResponse({
            "resumed": False,
            "message": "No active session found"
        }, status=404)

    return JsonResponse({
        "resumed": True,
        "session_id": session.session_id,
        "scenario": session.scenario_snapshot,
        "antagonist_attempts": session.antagonist_attempts
    })
