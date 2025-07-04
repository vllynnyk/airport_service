from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model


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
