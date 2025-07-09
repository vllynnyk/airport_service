from django.urls import path, include
from rest_framework import routers

from airservice.views import (
    AirplaneTypeViewSet,
    RouteViewSet,
    FlightViewSet,
    AirportViewSet,
    AirplaneViewSet,
    CrewViewSet,
    OrderViewSet,
)

app_name = "airservice"

router = routers.DefaultRouter()
router.register("airports", AirportViewSet, basename="airport")
router.register("route", RouteViewSet, basename="route")
router.register("airplane_type", AirplaneTypeViewSet, basename="airplane_type")
router.register("airplane", AirplaneViewSet, basename="airplane")
router.register("crew", CrewViewSet, basename="crew")
router.register("flights", FlightViewSet, basename="flight")
router.register("order", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
]
