from django.contrib import admin
from .models import EventTemplate, SchedulingCalendar, Event, EventInstance, SchedulingRule

# Register your models here.
admin.site.register(EventTemplate)
admin.site.register(SchedulingCalendar)
admin.site.register(Event)
admin.site.register(SchedulingRule)

@admin.register(EventInstance)
class EventInstanceAdmin(admin.ModelAdmin):
    list_display = ('start', 'end', 'status', 'display_host')
