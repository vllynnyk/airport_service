from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from django.db import IntegrityError

from airservice.models import AirplaneType, Airplane
from airservice.serializers import (
    AirplaneTypeSerializer,
    AirplaneTypeRetrieveSerializer,
)


AIRPLANE_TYPE_URL = reverse("airservice:airplane_type-list")


def detail_url(airplane_type_id):
    return reverse("airservice:airplane_type-detail", args=(airplane_type_id,))


class AirplaneTypeBaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.airplane_type_1 = AirplaneType.objects.create(name="Airliner")
        cls.airplane_type_2 = AirplaneType.objects.create(name="Seaplane")
        cls.airplane_1 = Airplane.objects.create(
            name="Airbus A300",
            rows=30,
            seats_in_row=6,
            airplane_type=cls.airplane_type_1,
        )

    def test_airplane_type_name_must_be_unique(self):
        with self.assertRaises(IntegrityError):
            AirplaneType.objects.create(name="Airliner")


class UnauthenticatedAirplaneTypeApiTests(AirplaneTypeBaseTest):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneTypeApiTests(AirplaneTypeBaseTest):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
        )
        self.client.force_authenticate(user=self.user)

    def test_airplane_types_list(self):
        response = self.client.get(AIRPLANE_TYPE_URL)
        airplane_types = AirplaneType.objects.all()
        serializer = AirplaneTypeSerializer(airplane_types, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_airplane_type(self):
        url = detail_url(self.airplane_type_1.id)
        response = self.client.get(url)
        serializer = AirplaneTypeRetrieveSerializer(self.airplane_type_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertIn("airplanes", response.data)
        self.assertEqual(len(response.data["airplanes"]), 1)

    def test_create_airplane_type_forbidden(self):
        payload = {
            "name": "Glider",
        }
        response = self.client.post(AIRPLANE_TYPE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_airplane_type_forbidden(self):
        payload = {"name": "Glider"}
        url = detail_url(self.airplane_type_1.id)
        response = self.client.patch(url, payload)
        self.airplane_type_1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTypeTests(AirplaneTypeBaseTest):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_airplane_type(self):
        payload = {
            "name": "Glider",
        }
        response = self.client.post(AIRPLANE_TYPE_URL, payload)
        airplane_type = AirplaneType.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payload["name"], getattr(airplane_type, "name"))

    def test_update_airplane_type(self):
        payload = {"name": "Glider"}
        url = detail_url(self.airplane_type_1.id)
        response = self.client.patch(url, payload)
        self.airplane_type_1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.airplane_type_1.name, "Glider")

    def test_delete_airplane_type(self):
        url = detail_url(self.airplane_type_1.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
