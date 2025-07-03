from django.db import models
from django.db.models.functions import Lower
from rest_framework.exceptions import ValidationError


class Airport(models.Model):
    name = models.CharField(max_length=100, unique=True)
    closest_big_city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    class Meta:
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="unique_lower_name_airport",
            )
        ]

    def __str__(self):
        return f"{self.name}, closest city: {self.closest_big_city}"


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="routes_from"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="routes_to"
    )
    distance = models.IntegerField()
    display_name = models.CharField(max_length=255, editable=False, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source", "destination"],
                name="unique_route_source_destination"
            )
        ]
        ordering = ("source", "destination")

    @staticmethod
    def validate_source_and_destination(source, destination, error_to_raise):
        if source == destination:
            raise error_to_raise(
                f"Source({source.name}) and"
                f" Destination({destination.name}) can't be the same"
            )

    def clean(self):
        Route.validate_source_and_destination(
            self.source, self.destination, ValidationError
        )

    def save(self, *args, **kwargs):
        self.display_name = f"{self.source.name} - {self.destination.name}"
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name

class AirplaneType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.name}"


class Airplane(models.Model):
    name = models.CharField(max_length=100, unique=True)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.CASCADE, related_name="airplanes"
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return f"{self.name}"
