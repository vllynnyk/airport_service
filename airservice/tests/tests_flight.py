from datetime import timedelta
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from django.db import models

from airservice.models import (
    Airport,
    Flight,
    AirplaneType,
    Airplane,
    Route,
    Crew,
)
from airservice.serializers import (
    FlightListSerializer,
    FlightRetrieveSerializer,
    FlightSerializer,
)


FLIGHT_URL = reverse("airservice:flight-list")


def detail_url(flight_id):
    return reverse("airservice:flight-detail", args=(flight_id,))


class FlightBaseTest(TestCase):
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
        cls.airplane_type = AirplaneType.objects.create(name="Type A")
        cls.airplane_1 = Airplane.objects.create(
            name="Plane A",
            rows=10, seats_in_row=6,
            airplane_type=cls.airplane_type
        )
        cls.airplane_2 = Airplane.objects.create(
            name="Plane B",
            rows=10, seats_in_row=6,
            airplane_type=cls.airplane_type
        )
        cls.crew_1 = Crew.objects.create(first_name="Jack", last_name="Jones")
        cls.crew_2 = Crew.objects.create(first_name="Jon", last_name="Jones")
        cls.flight = Flight.objects.create(
            route=cls.route_1,
            airplane=cls.airplane_1,
            departure_date=timezone.now(),
            arrival_date=timezone.now() + timedelta(hours=2),
        )
        cls.flight.crew.add(cls.crew_1)
        cls.flight.save()


class UnauthenticatedFlightApiTests(FlightBaseTest):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(FLIGHT_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFightApiTests(FlightBaseTest):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
        )
        self.client.force_authenticate(user=self.user)

    def test_flights_list(self):
        response = self.client.get(FLIGHT_URL)
        flights = Flight.objects.all()
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_flights_sorted_by_date(self):
        response = self.client.get(FLIGHT_URL)
        flights = [
            (flight["departure_date"], flight["arrival_date"])
            for flight in response.data["results"]
        ]
        self.assertEqual(flights, sorted(flights))

    def test_retrieve_flight(self):
        url = detail_url(self.flight.id)
        response = self.client.get(url)
        serializer = FlightRetrieveSerializer(self.flight)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.data["route"], self.route_1.display_name)
        self.assertEqual(response.data["route"], self.route_1.display_name)
        self.assertIn("airplane", response.data)
        self.assertIn("departure_date", response.data)
        self.assertIn("arrival_date", response.data)
        self.assertIn("crew", response.data)

    def test_create_flight_forbidden(self):
        payload = {
            "route": self.route_1.id,
            "airplane": self.airplane_2.id,
            "departure_date": timezone.now(),
            "arrival_date": timezone.now() + timedelta(hours=2),
        }
        response = self.client.post(FLIGHT_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_flight_forbidden(self):
        payload = {
            "route": self.route_2.id,
        }
        url = detail_url(self.flight.id)
        response = self.client.patch(url, payload)
        self.flight.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightTests(FlightBaseTest):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_flight(self):
        payload = {
            "route": self.route_2.id,
            "airplane": self.airplane_2.id,
            "departure_date": timezone.now(),
            "arrival_date": timezone.now() + timedelta(hours=2),
            "crew": [
                self.crew_2.id,
            ],
        }
        response = self.client.post(FLIGHT_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        flight = Flight.objects.get(id=response.data["id"])

        for key in payload:
            with self.subTest(field=key):
                flight_value = getattr(flight, key)
                if isinstance(flight_value, models.Model):
                    self.assertEqual(payload[key], flight_value.id)
                else:
                    if hasattr(flight_value, "all"):
                        self.assertEqual(
                            sorted(payload[key]),
                            sorted(
                                [member.id for member in flight_value.all()]
                            ),
                        )
                    else:
                        self.assertEqual(payload[key], flight_value)

    def test_serializer_validates_assigned_crew(self):
        payload = {
            "route": self.route_2.id,
            "airplane": self.airplane_2.id,
            "departure_date": timezone.now(),
            "arrival_date": timezone.now() + timedelta(hours=2),
            "crew": [
                self.crew_1.id,
            ],
        }
        serializer = FlightSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("crew", serializer.errors)
        self.assertIn("Jack Jones", str(serializer.errors["crew"]))

    def test_serializer_validates_assigned_airplane(self):
        payload = {
            "route": self.route_2.id,
            "airplane": self.airplane_1.id,
            "departure_date": timezone.now(),
            "arrival_date": timezone.now() + timedelta(hours=2),
            "crew": [
                self.crew_2.id,
            ],
        }
        serializer = FlightSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("airplane", serializer.errors)
        self.assertIn("Plane A", str(serializer.errors["airplane"]))

    def test_serializer_invalid_airplane_and_crew_conflict(self):
        payload = {
            "route": self.route_2.id,
            "airplane": self.airplane_1.id,  # уже занят
            "departure_date": timezone.now(),
            "arrival_date": timezone.now() + timedelta(hours=2),
            "crew": [self.crew_1.id],  # уже занят
        }
        serializer = FlightSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("airplane", serializer.errors)
        self.assertIn("crew", serializer.errors)

    def test_serializer_invalid_if_departure_after_arrival(self):
        payload = {
            "route": self.route_2.id,
            "airplane": self.airplane_2.id,
            "departure_date": timezone.now() + timedelta(hours=3),
            "arrival_date": timezone.now() + timedelta(hours=2),
            "crew": [self.crew_2.id],
        }
        serializer = FlightSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)

    def test_update_flight(self):
        payload = {
            "route": self.route_2.id,
        }
        url = detail_url(self.flight.id)
        response = self.client.patch(url, payload)
        self.flight.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.flight.route, self.route_2)

    def test_delete_flight(self):
        url = detail_url(self.flight.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
