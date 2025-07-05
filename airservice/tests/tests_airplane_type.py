from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from django.db import IntegrityError

from airservice.models import AirplaneType, Airplane


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

