from unittest.mock import patch

from django.urls import reverse
from rest_framework.test import APITestCase, APIClient

from apps.cyberUser.models import CyberUser
from apps.simulation.models import Scenario, GameSession


class LLMFlowTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CyberUser.objects.create(username="tester", email="tester@example.com")
        self.client.force_authenticate(user=self.user)

        # Minimal scenario so start_with_role can snapshot it
        self.scenario = Scenario.objects.create(
            name="Phishing Demo",
            description="",
            difficulty_level=1,
            antagonist_goal="conseguir telefono",
            base_points=10,
            threat_type="generic",
            is_active=True,
        )

    @patch("apps.simulation.views._call_llm_backend")
    def test_attempts_and_win_after_three_attacks(self, mock_llm):
        # First call: start session
        mock_llm.return_value = {"reply": "Hola", "analysis": {}}
        resp = self.client.post(
            reverse("simulation-start-with-role"),
            {"scenario_id": self.scenario.scenario_id},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        session_id = resp.json()["session_id"]

        # Prepare LLM responses: rapport (no attempt), then three attempts
        mock_llm.side_effect = [
            {"reply": "charlando", "analysis": {"is_attack_attempt": False, "has_disclosure": False}},
            {"reply": "dame tu dato", "analysis": {"is_attack_attempt": True, "has_disclosure": False}},
            {"reply": "insisto", "analysis": {"is_attack_attempt": True, "has_disclosure": False}},
            {"reply": "último", "analysis": {"is_attack_attempt": True, "has_disclosure": False}},
        ]

        # Rapport: attempts should remain 0
        r1 = self.client.post(reverse("simulation-chat"), {"session_id": session_id, "message": "hola"}, format="json")
        self.assertEqual(r1.status_code, 200)
        session = GameSession.objects.get(session_id=session_id)
        self.assertEqual(session.antagonist_attempts, 0)

        # Three attack attempts → should win after third (attempts reaches MAX_ATTEMPTS=3)
        self.client.post(reverse("simulation-chat"), {"session_id": session_id, "message": "msg2"}, format="json")
        self.client.post(reverse("simulation-chat"), {"session_id": session_id, "message": "msg3"}, format="json")
        r4 = self.client.post(reverse("simulation-chat"), {"session_id": session_id, "message": "msg4"}, format="json")
        self.assertEqual(r4.status_code, 200)

        session.refresh_from_db()
        self.assertEqual(session.antagonist_attempts, 3)
        self.assertEqual(session.outcome, "won")
        self.assertFalse(session.is_game_over)  # False == user won
        self.assertEqual(session.game_over_reason, "antagonist_exhausted_no_disclosure")

    @patch("apps.simulation.views._call_llm_backend")
    def test_disclosure_losses_immediately(self, mock_llm):
        mock_llm.return_value = {"reply": "Hola", "analysis": {}}
        resp = self.client.post(
            reverse("simulation-start-with-role"),
            {"scenario_id": self.scenario.scenario_id},
            format="json",
        )
        session_id = resp.json()["session_id"]

        mock_llm.return_value = {
            "reply": "ok",
            "analysis": {"has_disclosure": True, "disclosure_reason": "usuario compartio telefono"},
        }
        r = self.client.post(reverse("simulation-chat"), {"session_id": session_id, "message": "mi numero es 123"}, format="json")
        self.assertEqual(r.status_code, 200)

        session = GameSession.objects.get(session_id=session_id)
        self.assertTrue(session.is_game_over)
        self.assertEqual(session.outcome, "failed")
        self.assertEqual(session.game_over_reason, "usuario compartio telefono")