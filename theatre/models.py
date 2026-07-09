from typing import Type

from django.db import models
from django.core.exceptions import ValidationError

from user.models import User


class Actor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"Actor: {self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"Genre: {self.name}"


class TheatreHall(models.Model):
    name = models.CharField(max_length=100)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    def __str__(self):
        return f"TheatreHall: {self.name} have rows: {self.rows}"


class Play(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    actor = models.ManyToManyField(Actor)
    genre = models.ManyToManyField(Genre)

    def __str__(self):
        return f"Play: {self.title}"


class Performance(models.Model):
    play = models.ForeignKey(Play, on_delete=models.CASCADE)
    theatre_hall = models.ForeignKey(TheatreHall, on_delete=models.CASCADE)
    show_time = models.DateTimeField()

    def __str__(self):
        return f"{self.play} in {self.theatre_hall}"


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Reservation: {self.created_at} by {self.user}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    performance = models.ForeignKey(Performance, on_delete=models.CASCADE)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("performance", "row", "seat")
        ordering = ["row", "seat"]

    @staticmethod
    def validate_ticket(
            row: int,
            seat: int,
            theatre_hall: TheatreHall,
            error_to_raise: Type[Exception]) -> None:
        if not (1 <= row <= theatre_hall.rows):
            raise error_to_raise({
                "row": f"Rows must be in range from 1 to {theatre_hall.rows}"
            })
        if not (1 <= seat <= theatre_hall.seats_in_row):
            raise error_to_raise({
                "seat": f"Seats must be in range from 1 to {theatre_hall.seats_in_row}"
            })

    def clean(self):
        Ticket.validate_ticket(
            row=self.row,
            seat=self.seat,
            theatre_hall=self.performance.theatre_hall,
            error_to_raise=ValidationError
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket: {self.performance} (row: {self.row}, seat: {self.seat})"
