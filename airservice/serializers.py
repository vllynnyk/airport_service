from rest_framework import serializers

from airservice.models import Airport


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ["id", "name", "closest_big_city", "country"]
