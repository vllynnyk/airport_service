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

