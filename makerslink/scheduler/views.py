from django.shortcuts import render
from .models import EventTemplate, SchedulingCalendar, Event, EventInstance, SchedulingRule
from datetime import datetime, timezone
from dateutil.relativedelta import *
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

# Create your views here.
def index(request):
    now = datetime.now().isoformat()
    num_host_needed = EventInstance.objects.filter(status__lte=0, start__gte=now).count()

    return render(
        request,
        'index.html',
        context={
            'num_host_needed' :num_host_needed
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