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
from airservice.serializers import (
    OrderListSerializer,
    OrderRetrieveSerializer,
    FlightRetrieveSerializer,
    TicketSerializer,
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


class AuthenticatedOrderAndTicketApiTests(OrderAndTicketBaseTest):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.__class__.user)

    def test_orders_list(self):
        response = self.client.get(ORDER_URL)
        orders = Order.objects.all()
        serializer = OrderListSerializer(orders, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_orders_sorted_by_negative_date(self):
        response = self.client.get(ORDER_URL)
        orders = [order["created_at"] for order in response.data["results"]]
        self.assertEqual(orders, sorted(orders, reverse=True))

    def test_retrieve_order(self):
        url = detail_url(self.order_1.id)
        response = self.client.get(url)
        serializer = OrderRetrieveSerializer(self.order_1)
        expected_flight_data = FlightRetrieveSerializer(self.flight).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertIn("tickets", response.data)
        self.assertEqual(len(response.data["tickets"]), 1)
        for ticket in response.data["tickets"]:
            self.assertIn("flight", ticket)
            self.assertEqual(ticket["flight"], expected_flight_data)

    def test_create_order(self):
        payload = {
            "tickets": [
                {
                    "row": 3,
                    "seat": 1,
                    "flight": self.flight.id,
                }
            ]
        }
        response = self.client.post(ORDER_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        order = Order.objects.get(id=response.data["id"])
        self.assertEqual(order.tickets.count(), 1)
        ticket = order.tickets.first()
        self.assertEqual(ticket.row, payload["tickets"][0]["row"])
        self.assertEqual(ticket.seat, payload["tickets"][0]["seat"])
        self.assertEqual(ticket.flight.id, payload["tickets"][0]["flight"])

    def test_serializer_validates_row(self):
        payload = {
            "row": 33,
            "seat": 1,
            "flight": self.flight.id,
            "order": self.order_1.id,
        }
        serializer = TicketSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("row", serializer.errors)
        self.assertIn("33", str(serializer.errors["row"]))

    def test_serializer_validates_seat(self):
        payload = {
            "row": 3,
            "seat": 8,
            "flight": self.flight.id,
            "order": self.order_1.id,
        }
        serializer = TicketSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("seat", serializer.errors)
        self.assertIn("8", str(serializer.errors["seat"]))

    def test_serializer_validates_and_row_seat(self):
        payload = {
            "row": 13,
            "seat": 9,
            "flight": self.flight.id,
            "order": self.order_1.id,
        }
        serializer = TicketSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("row", serializer.errors)
        self.assertIn("13", str(serializer.errors["row"]))
        self.assertIn("seat", serializer.errors)
        self.assertIn("9", str(serializer.errors["seat"]))

    def test_update_order(self):
        payload = {
            "tickets": [
                {
                    "id": self.ticket_1.id,
                    "row": 6,
                }
            ]
        }
        url = detail_url(self.order_1.id)
        response = self.client.patch(url, payload, format="json")
        self.order_1.refresh_from_db()
        print(response.data)
        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_delete_order(self):
        url = detail_url(self.order_1.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
