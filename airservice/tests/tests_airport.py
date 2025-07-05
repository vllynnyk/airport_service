from django.test import TestCase
from rest_framework.reverse import reverse
from django.db import IntegrityError

from airservice.models import Airport, Route


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
