from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from django.db import models

from airservice.models import Route, Airport, Flight, AirplaneType, Airplane
from airservice.serializers import (
    RouteListSerializer,
    RouteRetrieveSerializer,
    RouteSerializer,
)


ROUTE_URL = reverse("airservice:route-list")


def detail_url(route_id):
    return reverse("airservice:route-detail", args=(route_id,))


class RouteBaseTest(TestCase):
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
        cls.airport_3 = Airport.objects.create(
            name="BER",
            closest_big_city="Berlin",
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
        cls.route_3 = Route.objects.create(
            source=cls.airport_3,
            destination=cls.airport_2,
            distance=100,
        )
        cls.route_4 = Route.objects.create(
            source=cls.airport_3,
            destination=cls.airport_1,
            distance=100,
        )

    def test_unique_route(self):
        route = Route(
            source=self.airport_1,
            destination=self.airport_2,
            distance=100,
        )
        with self.assertRaises(ValidationError):
            route.full_clean()
            route.save()


class UnauthenticatedRouteApiTests(RouteBaseTest):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ROUTE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTests(RouteBaseTest):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
        )
        self.client.force_authenticate(user=self.user)

    def test_routes_list(self):
        response = self.client.get(ROUTE_URL)
        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_routes_sorted_by_source_and_destination(self):
        response = self.client.get(ROUTE_URL)
        routes = [
            (route["source_airport"], route["destination_airport"])
            for route in response.data["results"]
        ]
        self.assertEqual(routes, sorted(routes))

    def test_retrieve_route(self):
        airplane_type = AirplaneType.objects.create(name="Type A")
        airplane = Airplane.objects.create(
            name="Plane A",
            rows=10,
            seats_in_row=6,
            airplane_type=airplane_type
        )

        Flight.objects.create(
            route=self.route_1,
            airplane=airplane,
            departure_date=timezone.now(),
            arrival_date=timezone.now() + timedelta(hours=2),
        )
        url = detail_url(self.route_1.id)
        response = self.client.get(url)
        serializer = RouteRetrieveSerializer(self.route_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertIn("flights", response.data)
        self.assertEqual(len(response.data["flights"]), 1)

    def test_create_route_forbidden(self):
        payload = {
            "source": self.airport_1.id,
            "destination": self.airport_3.id,
            "distance": 100,
        }
        response = self.client.post(ROUTE_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_route_forbidden(self):
        payload = {"distance": 300}
        url = detail_url(self.route_1.id)
        response = self.client.patch(url, payload)
        self.route_1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
