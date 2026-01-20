from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from types import SimpleNamespace
from unittest.mock import patch
import json

from apps.cyberUser.models import CyberUser
from apps.simulation.models import Scenario, SensitivePattern, GameSession, ChatMessage
import apps.simulation.views as views


class ChatAttemptTests(TestCase):
    def setUp(self):
        # Create a simple user. avatar accepts a string path in tests.
        self.user = CyberUser.objects.create(username='tester', email='t@example.com', password='x', avatar='t.jpg')
        self.factory = APIRequestFactory()
        # Ensure MAX_ATTEMPTS is 3 for deterministic behavior
        views.MAX_ATTEMPTS = 3
        # Create a scenario with base_points
        self.scenario = Scenario.objects.create(name='s1', antagonist_goal='goal', difficulty_level=1, base_points=50, threat_type='test', is_active=True)

    def _call_chat(self, message, session_id=None, ai_return=None):
        data = {'message': message}
        if session_id:
            data['session_id'] = session_id
        request = self.factory.post('/chat', data, format='json')
        # Use force_authenticate with a lightweight object that exposes
        # `is_authenticated`, `is_active` and `id` so DRF permissions pass
        fake_user = SimpleNamespace(is_authenticated=True, is_active=True, id=self.user.pk)
        force_authenticate(request, user=fake_user)
        mock_response = ai_return or {"reply": "ok", "analysis": {"is_attack_attempt": False, "has_disclosure": False}}
        with patch('apps.simulation.views._call_llm_backend', return_value=mock_response):
            resp = views.chat(request)
        return json.loads(resp.content.decode())

    def test_three_attempts_user_wins(self):
        # First call: AI attempts
        r1 = self._call_chat('hello', ai_return={"reply": "Intento1", "analysis": {"is_attack_attempt": True, "has_disclosure": False}})
        self.assertIn('session_id', r1)
        session_id = r1['session_id']
        session = GameSession.objects.get(session_id=session_id)
        self.assertEqual(session.antagonist_attempts, 1)

        # Second call: AI attempts again
        r2 = self._call_chat('still here', session_id=session_id, ai_return={"reply": "Intento2", "analysis": {"is_attack_attempt": True, "has_disclosure": False}})
        session.refresh_from_db()
        self.assertEqual(session.antagonist_attempts, 2)

        # Third call: AI attempts third time -> should trigger win for user
        r3 = self._call_chat('no reveal', session_id=session_id, ai_return={"reply": "Intento3", "analysis": {"is_attack_attempt": True, "has_disclosure": False}})
        session.refresh_from_db()
        # session should be closed and marked as won
        self.assertIsNotNone(session.is_game_over)
        self.assertFalse(session.is_game_over)
        self.assertEqual(session.outcome, 'won')
        # points awarded
        self.assertTrue(session.points_awarded)
        self.assertEqual(session.points_earned, int(self.scenario.base_points))

    def test_attempt_then_user_discloses_user_loses(self):
        # First call: AI attempts
        r1 = self._call_chat('hello', ai_return={"reply": "Intento1", "analysis": {"is_attack_attempt": True, "has_disclosure": False}})
        session_id = r1['session_id']
        session = GameSession.objects.get(session_id=session_id)
        self.assertEqual(session.antagonist_attempts, 1)

        # Create a sensitive pattern that matches SECRET123
        SensitivePattern.objects.create(name='secret', regex_pattern=r'SECRET123', data_type='secret')

        # Second call: user reveals secret -> backend should detect and mark session failed
        r2 = self._call_chat('here is my secret SECRET123', session_id=session_id, ai_return={"reply": "oh", "analysis": {"is_attack_attempt": False, "has_disclosure": True}})
        session.refresh_from_db()
        self.assertIsNotNone(session.is_game_over)
        self.assertTrue(session.is_game_over)
        self.assertEqual(session.outcome, 'failed')

        # The user's message should be marked dangerous
        dangerous = ChatMessage.objects.filter(session=session, role='user', is_dangerous=True).exists()
        self.assertTrue(dangerous)
