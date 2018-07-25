import logging
logger = logging.getLogger(__name__)

from django.shortcuts import render
from .models import EventTemplate, SchedulingCalendar, Event, EventInstance, SchedulingRule
from .forms import EventInstanceFormSet
from django.forms import modelformset_factory
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
    #form_class = EventForm

class EventUpdateView(UpdateView):
    model = Event
    fields = '__all__'
    #form_class = EventForm

class EventDeleteView(DeleteView):
    model = Event
    success_url = reverse_lazy('events')

def TestView(request):
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + relativedelta(months=+1)

    event_objects = Event.objects.all()
    event_list = []
    for event in event_objects:
        event_list += event.get_events(start, end, False)

    event_list = sorted(event_list, key=lambda eventinstance: eventinstance.start)
    initial_values = [(event_instance.as_dict()) for event_instance in event_list]
    initial_values2 = [{'host': "Test"},{'host': "Test"}]
    initial_values3 = [
        {
            'google_calendar_booking_id': None,
            'host': 'None',
            'event': 1,
            'start': '2018-07-30 11:00:00',
            'end': '2018-07-30 14:00:00',
            'status': 0
        }, 
        {
            'google_calendar_booking_id': None,
            'host': 'None',
            'event': 2,
            'start': '2018-07-31 07:00:00',
            'end': '2018-07-31 10:00:00',
            'status': 0
        }, 
        {
            'google_calendar_booking_id': None,
             'host': 'None',
             'event': 1,
             'start': '2018-08-06 11:00:00',
             'end': '2018-08-06 14:00:00',
             'status': 0
         }, 
        {
            'google_calendar_booking_id': None,
             'host': 'None',
             'event': 2,
             'start': '2018-08-07 07:00:00',
             'end': '2018-08-07 10:00:00',
             'status': 0
        },
        {
            'google_calendar_booking_id': None,
             'host': 'None',
             'event': 1,
             'start': '2018-08-13 11:00:00',
             'end': '2018-08-13 14:00:00',
             'status': 0
        },
        {
            'google_calendar_booking_id': None,
             'host': 'None',
             'event': 2,
             'start': '2018-08-14 07:00:00',
             'end': '2018-08-14 10:00:00',
             'status': 0
        },
        {
            'google_calendar_booking_id': None,
             'host': 'None',
             'event': 1,
             'start': '2018-08-20 11:00:00',
             'end': '2018-08-20 14:00:00',
             'status': 0
        },
        {
            'google_calendar_booking_id': None,
             'host': 'None',
             'event': 2,
             'start': '2018-08-21 07:00:00',
             'end': '2018-08-21 10:00:00',
             'status': 0
        }
    ]


    TestFormSet = modelformset_factory(EventInstance, formset=EventInstanceFormSet, exclude=(), extra=len(initial_values2))

    if request.method == 'POST':
        formset = TestFormSet(request.POST, initial=initial_values2)
        if formset.is_valid():
            logger.warning("Form is valid")

            for form in formset:
                logger.warning(form.has_changed())
                if form.cleaned_data.get('perform_action'):
                    logger.warning(form.cleaned_data.get('id'))
        else:
            logger.warning("Form is invalid")
            for form in formset:
                if any(form.errors):
                    logger.warning(form.errors)
                    logger.warning(form.cleaned_data)
    else:
        formset = TestFormSet(initial=initial_values2)

    logger.warning(initial_values)
    return render(request, 'test_form.html', {'formset': formset})