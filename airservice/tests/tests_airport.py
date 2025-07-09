from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from django.db import IntegrityError

from airservice.models import Airport, Route
from airservice.serializers import (
    AirportListSerializer,
    AirportRetrieveSerializer
)


AIRPORT_URL = reverse("airservice:airport-list")


def detail_url(airport_id):
    return reverse("airservice:airport-detail", args=(airport_id,))


class AirportBaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.airport_1 = Airport.objects.create(
            name="Arlanda",
            closest_big_city="Stockholm",
            country="Sweden",
        )
        cls.airport_2 = Airport.objects.create(
            name="MUC",
            closest_big_city="Munich",
            country="German",
        )
        cls.route_1 = Route.objects.create(
            source=cls.airport_1,
            destination=cls.airport_2,
            distance=100,
        )
        cls.route_2 = Route.objects.create(
            source=cls.airport_2,
            destination=cls.airport_1,
            distance=100,
        )

    def test_airport_name_must_be_unique_case_insensitive(self):
        with self.assertRaises(IntegrityError):
            Airport.objects.create(
                name="muc", closest_big_city="Munich", country="German"
            )


class UnauthenticatedAirportApiTests(AirportBaseTest):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(AIRPORT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirportApiTests(AirportBaseTest):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
        )
        self.client.force_authenticate(user=self.user)

    def test_airports_list(self):
        response = self.client.get(AIRPORT_URL)
        airports = Airport.objects.all()
        serializer = AirportListSerializer(airports, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_airports_sorted_by_name(self):
        response = self.client.get(AIRPORT_URL)
        names = [airport["name"] for airport in response.data["results"]]
        self.assertEqual(names, sorted(names))

    def test_retrieve_airport(self):
        url = detail_url(self.airport_1.id)
        response = self.client.get(url)
        serializer = AirportRetrieveSerializer(self.airport_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertIn("departure", response.data)
        self.assertIn("arrival", response.data)
        self.assertEqual(len(response.data["departure"]), 1)
        self.assertEqual(len(response.data["arrival"]), 1)

    def test_create_airport_forbidden(self):
        payload = {
            "name": "BER",
            "closest_big_city": "Berlin",
            "country": "German",
        }
        response = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_airport_forbidden(self):
        payload = {"closest_big_city": "Berlin"}
        url = detail_url(self.airport_1.id)
        response = self.client.patch(url, payload)
        self.airport_1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportTests(AirportBaseTest):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_airport(self):
        payload = {
            "name": "BER",
            "closest_big_city": "Berlin",
            "country": "German",
        }
        response = self.client.post(AIRPORT_URL, payload)
        airport = Airport.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(airport, key))

    def test_update_airport(self):
        payload = {"closest_big_city": "Berlin"}
        url = detail_url(self.airport_1.id)
        response = self.client.patch(url, payload)
        self.airport_1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.airport_1.closest_big_city, "Berlin")

    def test_delete_airport(self):
        url = detail_url(self.airport_1.id)

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
