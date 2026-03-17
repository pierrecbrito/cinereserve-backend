from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AccountsApiTests(APITestCase):
    def test_signup_returns_201(self):
        response = self.client.post(
            reverse("signup"),
            {"email": "user@example.com", "username": "user1", "password": "StrongPass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="user1").exists())

    def test_me_requires_authentication(self):
        response = self.client.get(reverse("me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
