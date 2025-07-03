from rest_framework import serializers

from airservice.models import Airport, Route, Airplane, AirplaneType, Crew, Flight


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
        source="destination.name",
        read_only=True
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

