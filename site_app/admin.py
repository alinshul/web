from django.contrib import admin

# Register your models here.
from site_app.models import Reservation

# admin.site.register(Reservation)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('get_title', 'date', 'time', 'status')

    def get_title(self, obj):
        return obj.comment or f"Бронирование #{obj.id}"

    get_title.short_description = 'Название'