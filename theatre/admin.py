from django.contrib import admin

from theatre.models import Actor, Genre, TheatreHall, Play, Performance, Reservation, Ticket

admin.site.register(Actor)
admin.site.register(Genre)
admin.site.register(TheatreHall)
admin.site.register(Play)
admin.site.register(Performance)


class TicketInLine(admin.TabularInline):
   model = Ticket
   extra = 1


@admin.register(Reservation)
class OrderAdmin(admin.ModelAdmin):
   inlines = (TicketInLine,)
