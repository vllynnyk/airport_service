from datetime import timedelta
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airservice.models import (
    Crew,
    Airport,
    Flight,
    AirplaneType,
    Airplane,
    Route
)
from airservice.serializers import CrewListSerializer, CrewRetrieveSerializer

CREW_URL = reverse("airservice:crew-list")


def detail_url(crew_id):
    return reverse("airservice:crew-detail", args=(crew_id,))


class CrewBaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.crew_1 = Crew.objects.create(
            first_name="John",
            last_name="Smith",
        )
        cls.crew_2 = Crew.objects.create(
            first_name="Jane",
            last_name="Smith",
        )


class UnauthenticatedCrewApiTests(CrewBaseTest):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(CREW_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewApiTests(CrewBaseTest):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
        )
        self.client.force_authenticate(user=self.user)

    def test_crews_list(self):
        response = self.client.get(CREW_URL)
        crews = Crew.objects.all()
        serializer = CrewListSerializer(crews, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_crews_sorted(self):
        response = self.client.get(CREW_URL)
        crews = [(crew["full_name"]) for crew in response.data["results"]]
        self.assertEqual(crews, sorted(crews))

    def test_retrieve_crew(self):
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
        airplane_type = AirplaneType.objects.create(name="Type A")
        airplane = Airplane.objects.create(
            name="Plane A",
            rows=10,
            seats_in_row=6,
            airplane_type=airplane_type
        )

        flight = Flight.objects.create(
            route=route_1,
            airplane=airplane,
            departure_date=timezone.now(),
            arrival_date=timezone.now() + timedelta(hours=2),
        )
        flight.crew.add(self.crew_1)
        flight.save()
        url = detail_url(self.crew_1.id)
        response = self.client.get(url)
        serializer = CrewRetrieveSerializer(self.crew_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertIn("flights", response.data)
        self.assertEqual(len(response.data["flights"]), 1)

    def test_create_crew_forbidden(self):
        payload = {
            "first_name": "Jack",
            "last_name": "Smut",
        }
        response = self.client.post(CREW_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_crew_forbidden(self):
        payload = {"last_name": "Smut"}
        url = detail_url(self.crew_1.id)
        response = self.client.patch(url, payload)
        self.crew_1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewTests(CrewBaseTest):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_create_crew(self):
        payload = {"first_name": "Jack", "last_name": "Smut"}
        response = self.client.post(CREW_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        crew = Crew.objects.get(id=response.data["id"])

        for key in payload:
            self.assertEqual(payload[key], getattr(crew, key))

    def test_update_crew(self):
        payload = {"last_name": "Smut"}
        url = detail_url(self.crew_1.id)
        response = self.client.patch(url, payload)
        self.crew_1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.crew_1.last_name, "Smut")

    def test_delete_crew(self):
        url = detail_url(self.crew_1.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
