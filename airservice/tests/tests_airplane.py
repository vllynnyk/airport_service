from django.test import TestCase
from rest_framework.reverse import reverse
from django.db import IntegrityError

from airservice.models import AirplaneType, Airplane


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
