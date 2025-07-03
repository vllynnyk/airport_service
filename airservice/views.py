from django.db.models import Prefetch
from django.shortcuts import render
from rest_framework import viewsets

from airservice.models import Airport, Route, Flight, AirplaneType
from airservice.serializers import AirportSerializer, AirportListSerializer, AirportRetrieveSerializer, \
    RouteListSerializer, RouteSerializer, RouteRetrieveSerializer, AirplaneTypeSerializer, \
    AirplaneTypeRetrieveSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                Prefetch(
                    "routes_from",
                    queryset=Route.objects.select_related("destination")
                ),
                Prefetch(
                    "routes_to",
                    queryset=Route.objects.select_related("source")
                ),
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        elif self.action == "retrieve":
            return AirportRetrieveSerializer
        return AirportSerializer

class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination").all()
    serializer_class = RouteSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                Prefetch(
                    "flights",
                    queryset=Flight.objects.select_related(
                        "route",
                        "airplane"
                    ),
                )
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        elif self.action == "retrieve":
            return RouteRetrieveSerializer
        return RouteSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AirplaneTypeRetrieveSerializer
        return AirplaneTypeSerializer
