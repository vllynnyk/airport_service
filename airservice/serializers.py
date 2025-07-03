from rest_framework import serializers

from airservice.models import Airport, Route


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
