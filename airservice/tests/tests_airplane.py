from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from django.db import IntegrityError

from airservice.models import AirplaneType, Airplane, Airport, Route, Flight
from airservice.serializers import (
    AirplaneListSerializer,
    AirplaneRetrieveSerializer
)

AIRPLANE_URL = reverse("airservice:airplane-list")


def detail_url(airplane_id):
    return reverse("airservice:airplane-detail", args=(airplane_id,))


class AirplaneBaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.airplane_type = AirplaneType.objects.create(name="Airliner")
        cls.airplane_1 = Airplane.objects.create(
            name="Airbus A300",
            rows=30,
            seats_in_row=6,
            airplane_type=cls.airplane_type,
        )
        cls.airplane_2 = Airplane.objects.create(
            name="Boeing 727",
            rows=28,
            seats_in_row=6,
            airplane_type=cls.airplane_type,
        )

    def test_airplane_name_must_be_unique(self):
        with self.assertRaises(IntegrityError):
            Airplane.objects.create(
                name="Airbus A300",
                rows=30,
                seats_in_row=6,
                airplane_type=self.airplane_type,
            )


class UnauthorizedAirplaneTests(AirplaneBaseTest):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(AIRPLANE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedAirplaneTests(AirplaneBaseTest):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
        )
        self.client.force_authenticate(user=self.user)

    def test_airplane_list(self):
        response = self.client.get(AIRPLANE_URL)
        airplane = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplane, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_airplane(self):
        airport_1 = Airport.objects.create(
            name="Arlanda",
            closest_big_city="Stockholm",
            country="Sweden",
        )
        airport_2 = Airport.objects.create(
            name="MUC",
            closest_big_city="Munich",
            country="German",
        )
        route_1 = Route.objects.create(
            source=airport_1,
            destination=airport_2,
            distance=100,
        )
        Flight.objects.create(
            route=route_1,
            airplane=self.airplane_1,
            departure_date=timezone.now(),
            arrival_date=timezone.now() + timedelta(hours=2),
        )
        url = detail_url(self.airplane_1.id)
        response = self.client.get(url)
        serializer = AirplaneRetrieveSerializer(self.airplane_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertIn("flights", response.data)
        self.assertEqual(len(response.data["flights"]), 1)

    def test_create_airport_forbidden(self):
        payload = {
            "name": "Airbus C300",
            "rows": 30,
            "seats_in_row": 6,
            "airplane_type": self.airplane_type.id,
        }
        response = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_airplane_forbidden(self):
        payload = {
            "name": "Airbus C300",
        }
        response = self.client.patch(detail_url(self.airplane_1), payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTests(AirplaneBaseTest):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_airplane(self):
        payload = {
            "name": "Airbus B300",
            "rows": 30,
            "seats_in_row": 6,
            "airplane_type": self.airplane_type.id,
        }
        response = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        airplane = Airplane.objects.get(id=response.data["id"])
        for key in payload:
            value = getattr(airplane, key)
            if key == "airplane_type":
                self.assertEqual(payload[key], value.id)
            else:
                self.assertEqual(payload[key], value)

    def test_update_airplane(self):
        payload = {"name": "Airbus C300"}
        url = detail_url(self.airplane_1.id)
        response = self.client.patch(url, payload)
        self.airplane_1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.airplane_1.name, "Airbus C300")

    def test_delete_airplane(self):
        url = detail_url(self.airplane_1.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
