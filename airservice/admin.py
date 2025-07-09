from django.contrib import admin

from airservice.models import (
    Ticket,
    Flight,
    Order,
    Airport,
    AirplaneType,
    Airplane,
    Crew,
    Route,
)

admin.site.register(Airport)
admin.site.register(Route)
admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Crew)
admin.site.register(Flight)


class TicketAdmin(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [TicketAdmin]
