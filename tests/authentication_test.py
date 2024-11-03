from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import GameResult
import json


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
    
    def test_login_with_valid_data(self):
        response = self.client.post(reverse("login"), {"username": "testuser", "password": "testpass"})
        self.assertRedirects(response, reverse("home"))

    def test_login_with_invalid_credentials(self):
        response = self.client.post(reverse("login"), {"username": "testuser", "password": "wrongpass"})
        self.assertContains(response, "Invalid username or password.")
    
    def test_login_with_incomplete_data(self):
        response = self.client.post(reverse("login"), {"username": "testuser"})
        self.assertContains(response, "Invalid username or password.")

    def test_successful_registration(self):
        response = self.client.post(reverse("register"), {
            "username": "newuser",
            "password1": "newuserpassword",
            "password2": "newuserpassword",
            "email": "newuser@example.com",
        })
        self.assertRedirects(response, reverse("login"))

    def test_registration_with_duplicate_username(self):
        response = self.client.post(reverse("register"), {
            "username": "testuser",
            "password1": "anotherpass",
            "password2": "anotherpass",
            "email": "anotheruser@example.com",
        })
        self.assertContains(response, "A user with that username already exists.")

    def test_logout_functionality(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("login"))