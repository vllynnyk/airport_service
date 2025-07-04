from datetime import timedelta, datetime

from django.db import IntegrityError
from django.test import TestCase
from freezegun import freeze_time
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from user.models import User


class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.email = "user@test.com"
        self.password = "1234pass"
        self.payload_user = {"email": self.email, "password": self.password}
        self.payload_test = {"email": "test@test.com", "password": "1234pass"}

        self.user = get_user_model().objects.create_user(
            email=self.email,
            password=self.password,
        )

        self.token_url = reverse("user:token_obtain_pair")
        self.refresh_url = reverse("user:token_refresh")
        self.verify_url = reverse("user:token_verify")
        self.register_url = reverse("user:create")
        self.me_url = reverse("user:manage_user")

    def get_tokens(self, payload=None):
        data = payload or self.payload_user
        return self.client.post(self.token_url, data=data)

    def test_create_user_model(self):
        user = get_user_model().objects.create_user(
            email="model@test.com", password="1234pass"
        )
        self.assertTrue(user)
        self.assertFalse(user.is_staff)

    def test_create_superuser_model(self):
        user = get_user_model().objects.create_superuser(
            email="admin@test.com", password="1234pass"
        )
        self.assertTrue(user)
        self.assertTrue(user.is_staff)

    def test_duplicate_user_creation_raises_error(self):
        with self.assertRaises(IntegrityError):
            get_user_model().objects.create_user(
                email=self.email,
                password="1234pass"
            )

    def test_create_user(self):
        response = self.client.post(self.register_url, data=self.payload_test)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            User.objects.filter(email=self.payload_test["email"]).count(), 1
        )
        self.assertFalse(response.data["is_staff"])

    def test_create_user_without_email(self):
        response = self.client.post(
            self.register_url,
            data={"password": "1234pass"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_obtain_pair_success(self):
        response = self.get_tokens()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)

    def test_token_auth_with_invalid_credentials(self):
        invalid_payload = {"email": "test@test.com", "password": "1234pass"}
        response = self.client.post(self.token_url, data=invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        token_response = self.get_tokens()
        refresh_token = token_response.data["refresh"]
        response = self.client.post(
            self.refresh_url,
            data={"refresh": refresh_token}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    @freeze_time("2025-01-01 12:00:00", tick=True)
    def test_verify_user_token(self):
        now = datetime(2025, 1, 1, 12, 0, 0)
        token_response = self.get_tokens()
        access = token_response.data["access"]
        response = self.client.post(self.verify_url, data={"token": access})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        with freeze_time(now + timedelta(minutes=6)):
            response = self.client.post(
                self.verify_url,
                data={"token": access}
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED
            )
