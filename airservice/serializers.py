from django.db import transaction
from rest_framework import serializers

from airservice.models import (
    Airport,
    Route,
    Airplane,
    AirplaneType,
    Crew,
    Flight,
    Ticket,
    Order,
)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ["id", "name", "closest_big_city", "country"]


class AirportListSerializer(AirportSerializer):
    class Meta:
        model = Airport
        fields = ["id", "name", "country"]


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]

    def validate(self, attrs):
        source = (
            attrs.get("source")
            if "source" in attrs
            else (self.instance.source if self.instance else None)
        )
        destination = (
            attrs.get("destination")
            if "destination" in attrs
            else (self.instance.destination if self.instance else None)
        )

        if source is not None and destination is not None:
            Route.validate_source_and_destination(
                source, destination, serializers.ValidationError
            )
        return attrs


class RouteListSerializer(RouteSerializer):
    source_airport = serializers.CharField(
        source="source.name",
        read_only=True
    )
    destination_airport = serializers.CharField(
        source="destination.name", read_only=True
    )

    class Meta:
        model = Route
        fields = ["id", "source_airport", "destination_airport", "distance"]


class AirportRetrieveSerializer(AirportSerializer):
    departure = RouteListSerializer(
        many=True,
        read_only=True,
        source="routes_from"
    )
    arrival = RouteListSerializer(
        many=True,
        read_only=True,
        source="routes_to"
    )

    class Meta:
        model = Airport
        fields = [
            "id",
            "name",
            "closest_big_city",
            "country",
            "departure",
            "arrival"
        ]


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ["id", "name", "rows", "seats_in_row", "airplane_type"]


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.CharField(
        source="airplane_type.name",
        read_only=True
    )

    class Meta:
        model = Airplane
        fields = ["id", "name", "airplane_type"]


class AirplaneForTypeSerializer(AirplaneSerializer):
    class Meta:
        model = Airplane
        fields = ["id", "name", "rows", "seats_in_row"]


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ["id", "name"]


class AirplaneTypeRetrieveSerializer(AirplaneTypeSerializer):
    airplanes = AirplaneForTypeSerializer(many=True, read_only=True)

    class Meta:
        model = AirplaneType
        fields = ["id", "name", "airplanes"]


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name", "full_name"]


class CrewListSerializer(CrewSerializer):
    class Meta:
        model = Crew
        fields = ["id", "full_name"]


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "departure_date",
            "arrival_date",
            "crew"
        ]

    def validate(self, attrs):
        current_flight_id = self.instance.id if self.instance else None

        crew_list = attrs.get("crew", None)
        if crew_list is None and self.instance:
            crew_list = self.instance.crew.all()

        airplane = attrs.get("airplane") or (
            self.instance.airplane if self.instance else None
        )
        departure_date = attrs.get("departure_date") or (
            self.instance.departure_date if self.instance else None
        )
        arrival_date = attrs.get("arrival_date") or (
            self.instance.arrival_date if self.instance else None
        )

        Flight.validate_airplane_and_crew(
            departure_date,
            arrival_date,
            current_flight_id,
            airplane,
            serializers.ValidationError,
            crew_list=crew_list,
        )

        if departure_date >= arrival_date:
            raise serializers.ValidationError(
                "Departure date must be before arrival date."
            )

        return attrs


class FlightListSerializer(FlightSerializer):
    route = serializers.StringRelatedField(read_only=True)
    airplane_name = serializers.CharField(
        source="airplane.name",
        read_only=True
    )

    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane_name",
            "departure_date",
            "arrival_date"
        ]


class FlightRetrieveSerializer(FlightSerializer):
    route = serializers.StringRelatedField(read_only=True)
    airplane = AirplaneSerializer(read_only=True)
    crew = CrewSerializer(many=True, read_only=True)

    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "departure_date",
            "arrival_date",
            "crew"
        ]


class AirplaneRetrieveSerializer(AirplaneSerializer):
    flights = FlightListSerializer(many=True, read_only=True)

    class Meta:
        model = Airplane
        fields = [
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "flights"
        ]


class CrewRetrieveSerializer(CrewSerializer):
    flights = FlightListSerializer(many=True, read_only=True)

    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name", "full_name", "flights"]


class RouteRetrieveSerializer(RouteSerializer):
    source = AirportSerializer(read_only=True)
    destination = AirportSerializer(read_only=True)
    flights = FlightListSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance", "flights"]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight"]

    def validate(self, attrs):
        row = (attrs.get("row") or
               (self.instance.row if self.instance else None))
        seat = (attrs.get("seat") or
                (self.instance.seat if self.instance else None))
        flight = attrs.get("flight") or (
            self.instance.flight if self.instance else None
        )
        Ticket.validate_place(
            row,
            seat,
            flight.airplane.rows,
            flight.airplane.seats_in_row,
            serializers.ValidationError,
        )
        return attrs


class TicketOrderListSerializer(TicketSerializer):
    route = serializers.StringRelatedField(read_only=True)
    flight_departure = serializers.DateTimeField(
        source="flight.departure_date", read_only=True
    )
    flight_arrival = serializers.DateTimeField(
        source="flight.arrival_date", read_only=True
    )

    class Meta:
        model = Ticket
        fields = ["id", "route", "flight_departure", "flight_arrival"]


class TicketOrderRetrieveSerializer(TicketOrderListSerializer):
    flight = FlightRetrieveSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight"]


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ["id", "created_at", "tickets"]

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketOrderListSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "created_at", "tickets"]


class OrderRetrieveSerializer(OrderSerializer):
    tickets = TicketOrderRetrieveSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "created_at", "tickets"]
