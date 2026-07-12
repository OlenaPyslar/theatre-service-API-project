from django.shortcuts import render
from rest_framework import viewsets

from theatre.models import Actor, Genre, TheatreHall, Play, Performance, Reservation
from theatre.serializers import ActorSerializer, GenreSerializer, TheatreHallSerializer, PlayListSerializer, \
    PlaySerializer, PerformanceSerializer, ReservationSerializer


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.all()
    serializer_class = PlayListSerializer

    def get_queryset(self):
        queryset = self.queryset

        if self.action in ("list", "retrieve"):
            return queryset.prefetch_related("actor", "genre")
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        return PlaySerializer


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer

    def get_queryset(self):
        queryset = self.queryset
        date = self.request.query_params.get("date")

        if date:
            queryset = queryset.filter(show_time__date=date)

        if self.action in ("list", "retrieve"):
            return queryset.select_related("play", "theatre_hall")
        return queryset


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action == "list":
            queryset = queryset.prefetch_related("tickets__performance__play",
                                                 "tickets__performance__theatre_hall")

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
