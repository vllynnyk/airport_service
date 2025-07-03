from django.db import models
from django.db.models.functions import Lower
from rest_framework.exceptions import ValidationError

from airport_service import settings


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

class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Crew"
        ordering = ["last_name", "first_name"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.full_name


class Flight(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    departure_date = models.DateTimeField()
    arrival_date = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flights")

    class Meta:
        ordering = ("departure_date", "arrival_date")

    @staticmethod
    def validate_airplane_and_crew(
        departure_date,
        arrival_date,
        current_flight_id,
        airplane,
        error_to_raise,
        crew_list=None,
    ):
        errors = {}

        for flight in airplane.flights.all():
            if flight.id == current_flight_id:
                continue
            if (
                arrival_date > flight.departure_date
                and departure_date < flight.arrival_date
            ):
                errors["airplane"] = (
                    f"Airplane {airplane.name} is already"
                    f" assigned to another flight at this time."
                )
                break

        if crew_list is not None:
            for crew_member in crew_list:
                for flight in crew_member.flights.all():
                    if flight.id == current_flight_id:
                        continue
                    if (
                        arrival_date > flight.departure_date
                        and departure_date < flight.arrival_date
                    ):
                        errors["crew"] = (
                            f"Crew member {crew_member.full_name} is already"
                            f" assigned to another flight at this time."
                        )
                        break

        if errors:
            raise error_to_raise(errors)

    def clean(self):
        if self.departure_date >= self.arrival_date:
            raise ValidationError("Departure must be before arrival.")
        Flight.validate_airplane_and_crew(
            self.departure_date,
            self.arrival_date,
            self.id,
            self.airplane,
            ValidationError,
        )

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None
    ):
        self.full_clean()
        return super(Flight, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"{self.route}, {self.departure_date} - {self.arrival_date}"

class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    class Meta:
        ordering = ("-created_at",)

class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["row", "seat", "flight"], name="unique_ticket"
            )
        ]
        ordering = ("flight",)

    def __str__(self):
        return f"{self.flight}, {self.row}: {self.seat}"

