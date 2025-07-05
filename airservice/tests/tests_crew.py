from datetime import timedelta
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from airservice.models import (
    Crew,
    Airport,
    Flight,
    AirplaneType,
    Airplane,
    Route
)
from airservice.serializers import CrewListSerializer, CrewRetrieveSerializer

CREW_URL = reverse("airservice:crew-list")


def detail_url(crew_id):
    return reverse("airservice:crew-detail", args=(crew_id,))


class CrewBaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.crew_1 = Crew.objects.create(
            first_name="John",
            last_name="Smith",
        )
        cls.crew_2 = Crew.objects.create(
            first_name="Jane",
            last_name="Smith",
        )

