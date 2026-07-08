from django.db import models


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

