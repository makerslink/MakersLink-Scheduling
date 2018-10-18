from django.contrib import admin
from .models import EventTemplate, SchedulingCalendar, Event, EventInstance, SchedulingRule, SchedulingPeriod

# Register your models here.
admin.site.register(EventTemplate)
admin.site.register(SchedulingCalendar)
admin.site.register(Event)
admin.site.register(SchedulingRule)

@admin.register(EventInstance)
class EventInstanceAdmin(admin.ModelAdmin):
    list_display = ('title', 'start', 'status', 'display_host', 'period')

@admin.register(SchedulingPeriod)
class UserAdmin(admin.ModelAdmin):
    actions = ['assign_unassigned']
    
    def assign_unassigned(self, request, queryset):
    
        if queryset.count() != 1:
            modeladmin.message_user(request, "Can not assign all unassigned to more then one period!")
            return
        rows_updated = EventInstance.objects.filter(period=None).update(period = queryset[0])
        
        if rows_updated == 1:
            message_bit = "1 eventInstance was"
        else:
            message_bit = "%s eventInstances were" % rows_updated
        
        self.message_user(request, "%s successfully assigned to %s." % (message_bit, queryset[0]))
    assign_unassigned.short_description = "Assign all unassigned eventInstances to selected period"

