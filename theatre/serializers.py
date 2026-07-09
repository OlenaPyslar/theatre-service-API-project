from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from theatre.models import Actor, Genre, TheatreHall, Play, Performance, Ticket, Reservation


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ("id", "first_name", "last_name")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name")


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = ("id", "name", "rows", "seats_in_row")


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ("id", "title", "description", "actor", "genre")


class PlayListSerializer(serializers.ModelSerializer):
    actor = ActorSerializer(many=True, read_only=True)
    genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Play
        fields = ("id", "title", "description", "actor", "genre")


class PerformanceSerializer(serializers.ModelSerializer):
    play_info = serializers.CharField(source="play.description", read_only=True)
    theatre_hall_info = serializers.CharField(source="theatre_hall.name", read_only=True)
    theatre_num_seats = serializers.IntegerField(source="theatre_hall.num_seats", read_only=True)

    class Meta:
        model = Performance
        fields = ("id", "show_time", "play",
                  "play_info", "theatre_hall",
                  "theatre_hall_info", "theatre_num_seats")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance")
        validators = [
            UniqueTogetherValidator(
                queryset=Ticket.objects.all(),
                fields=["row", "seat", "performance"],
                message="This ticket already exists."
            )
        ]

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        row = attrs.get("row")
        seat = attrs.get("seat")
        performance = attrs.get("performance")
        theatre_hall = performance.theatre_hall
        Ticket.validate_ticket(
            row=row,
            seat=seat,
            theatre_hall=theatre_hall,
            error_to_raise=serializers.ValidationError,
        )
        return data


class TicketListSerializer(serializers.ModelSerializer):
    performance = PerformanceSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance")


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, allow_empty=False)

    class Meta:
        model = Reservation
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            current_user = self.context["request"].user
            reservation = Reservation.objects.create(user=current_user, **validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["tickets"] = TicketListSerializer(instance.tickets.all(), many=True).data
        return representation