from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import GameResult
import json

class PerformanceTests(TestCase):
    def test_load_handling(self):
        for _ in range(100):  # Adjust the number as needed for load testing
            response = self.client.post(reverse("human_vs_ai_view", args=["gemini"]), json.dumps({"outcome": "win"}), content_type="application/json")
            self.assertEqual(response.status_code, 200)

    def test_database_performance(self):
        # You could add specific assertions on query count if using Django's `assertNumQueries` utility.
        with self.assertNumQueriesLessThan(10):  # Arbitrary number for example purposes
            GameResult.objects.create(player_one=self.user, ai_model2="gemini", outcome="win")
