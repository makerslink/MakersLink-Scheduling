from django.shortcuts import render
from .models import EventTemplate, SchedulingCalendar, Event, EventInstance, SchedulingRule
from datetime import datetime, timezone
from dateutil.relativedelta import *
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

# Create your views here.
def index(request):
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + relativedelta(months=+1)

    event_objects= Event.objects.all()
    event_list = []
    for event in event_objects:
        event_list+=event.get_events(start, end)

    event_list = sorted(event_list, key=lambda eventinstance: eventinstance.start)

    return render(
        request,
        'index.html',
        context={
            'event_list' :event_list
        },
    )

class SchedulingCalendarListView(generic.ListView):
    model = SchedulingCalendar

class SchedulingCalendarDetailView(generic.DetailView):
    model = SchedulingCalendar

class SchedulingCalendarCreateView(CreateView):
    model = SchedulingCalendar
    fields = '__all__'

class SchedulingCalendarUpdateView(UpdateView):
    model = SchedulingCalendar
    fields = '__all__'

class SchedulingCalendarDeleteView(DeleteView):
    model = SchedulingCalendar
    success_url = reverse_lazy('calendars')

class EventTemplateListView(generic.ListView):
    model = EventTemplate

class EventTemplateDetailView(generic.DetailView):
    model = EventTemplate

class EventTemplateCreateView(CreateView):
    model = EventTemplate
    fields = '__all__'

class EventTemplateUpdateView(UpdateView):
    model = EventTemplate
    fields = '__all__'

class EventTemplateDeleteView(DeleteView):
    model = EventTemplate
    success_url = reverse_lazy('templates')

class SchedulingRuleListView(generic.ListView):
    model = SchedulingRule

class SchedulingRuleDetailView(generic.DetailView):
    model = SchedulingRule

    def get_context_data(self, **kwargs):
        context = super(SchedulingRuleDetailView, self).get_context_data(**kwargs)
        events = self.object.get_events(extra_params="count:5;")
        context['eventlist'] = events
        return context

class SchedulingRuleCreateView(CreateView):
    model = SchedulingRule
    fields = '__all__'

class SchedulingRuleUpdateView(UpdateView):
    model = SchedulingRule
    fields = '__all__'

class SchedulingRuleDeleteView(DeleteView):
    model = SchedulingRule
    success_url = reverse_lazy('rules')

class EventListView(generic.ListView):
    model = Event

class EventDetailView(generic.DetailView):
    model = Event

    def get_context_data(self, **kwargs):
        start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start+relativedelta(months=+1)
        context = super(EventDetailView, self).get_context_data(**kwargs)
        events = self.object.get_events(start, end)
        context['eventlist'] = events
        return context

class EventCreateView(CreateView):
    model = Event
    fields = '__all__'

class EventUpdateView(UpdateView):
    model = Event
    fields = '__all__'

class EventDeleteView(DeleteView):
    model = Event
    success_url = reverse_lazy('events')
