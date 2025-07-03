from django.db import models
from django.db.models.functions import Lower


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

    def __str__(self):
        return self.display_name
