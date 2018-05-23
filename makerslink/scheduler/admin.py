from django.contrib import admin
from .models import BookingTemplate, BookingCalendar, Booking, BookingInstance, SchedulingRule

# Register your models here.
admin.site.register(BookingTemplate)
admin.site.register(BookingCalendar)
admin.site.register(Booking)
admin.site.register(SchedulingRule)

@admin.register(BookingInstance)
class BookingInstanceAdmin(admin.ModelAdmin):
    list_display = ('start', 'end', 'status', 'display_host')