from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import GameResult
import json

class UserInterfaceTests(TestCase):
    def test_responsive_design(self):
        response = self.client.get(reverse("game"))
        self.assertEqual(response.status_code, 200)
        # You could extend this test using Selenium or a similar tool to check actual responsiveness across devices

    def test_error_message_display(self):
        response = self.client.post(reverse("register"), {"username": ""})
        self.assertContains(response, "This field is required.")
