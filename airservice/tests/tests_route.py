from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.reverse import reverse

from airservice.models import Route, Airport

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
