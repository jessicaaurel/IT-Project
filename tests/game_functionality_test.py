from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import GameResult
import json

class GameFunctionalityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

    def test_game_view_access(self):
        response = self.client.get(reverse("game"))
        self.assertEqual(response.status_code, 200)

    def test_human_vs_ai_async_game(self):
        response = self.client.post(reverse("human_vs_ai_view", args=["gemini"]), json.dumps({"outcome": "win"}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(GameResult.objects.count(), 1)

    def test_ai_vs_ai_async_game(self):
        response = self.client.post(reverse("ai_vs_ai_view", args=["gemini", "claude"]), json.dumps({"outcome": "draw"}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(GameResult.objects.count(), 1)

    def test_outcome_storage(self):
        GameResult.objects.create(player_one=self.user, ai_model2="gemini", outcome="win")
        result = GameResult.objects.first()
        self.assertEqual(result.outcome, "win")