from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airservice.models import (
    Flight,
    Airport,
    Order,
    AirplaneType,
    Airplane,
    Route,
    Crew,
    Ticket,
)


ORDER_URL = reverse("airservice:order-list")


def detail_url(order_id):
    return reverse("airservice:order-detail", args=(order_id,))


class OrderAndTicketBaseTest(TestCase):
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
        cls.airplane_type = AirplaneType.objects.create(name="Type A")
        cls.airplane_1 = Airplane.objects.create(
            name="Plane A",
            rows=10,
            seats_in_row=6,
            airplane_type=cls.airplane_type
        )
        cls.airplane_2 = Airplane.objects.create(
            name="Plane B",
            rows=10,
            seats_in_row=6,
            airplane_type=cls.airplane_type
        )
        cls.crew_1 = Crew.objects.create(first_name="Jack", last_name="Jones")
        cls.flight = Flight.objects.create(
            route=cls.route_1,
            airplane=cls.airplane_1,
            departure_date=timezone.now(),
            arrival_date=timezone.now() + timedelta(hours=2),
        )
        cls.flight.crew.add(cls.crew_1)
        cls.flight.save()
        cls.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="testpass",
        )
        cls.order_1 = Order.objects.create(
            user=cls.user,
        )
        cls.order_2 = Order.objects.create(
            user=cls.user,
        )
        cls.ticket_1 = Ticket.objects.create(
            row=1,
            seat=1,
            flight=cls.flight,
            order=cls.order_1,
        )
        cls.ticket_2 = Ticket.objects.create(
            row=2,
            seat=1,
            flight=cls.flight,
            order=cls.order_2,
        )

    def test_unique_ticket(self):
        with self.assertRaises(ValidationError):
            Ticket.objects.create(
                row=1,
                seat=1,
                flight=self.flight,
                order=self.order_1,
            )



class UnauthenticatedOrderAndTicketApiTests(OrderAndTicketBaseTest):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ORDER_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
