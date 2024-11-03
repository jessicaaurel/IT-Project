from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import GameResult
import json

class ErrorHandlingTests(TestCase):
    def test_invalid_game_model(self):
        response = self.client.post(reverse("human_vs_ai_view", args=["invalid_model"]), json.dumps({"outcome": "win"}), content_type="application/json")
        self.assertEqual(response.status_code, 400)  # Assuming the app returns 400 for invalid model names.

    def test_missing_fields_in_request(self):
        response = self.client.post(reverse("human_vs_ai_view", args=["gemini"]), json.dumps({}), content_type="application/json")
        self.assertEqual(response.status_code, 400)  # Assuming missing fields return a 400 status.