import logging
logger = logging.getLogger(__name__)

from django.shortcuts import render
from .models import EventTemplate, SchedulingCalendar, Event, EventInstance, SchedulingRule
from .forms import EventInstanceFormSet, EventInstanceForm
from django.forms import modelformset_factory
from datetime import datetime, timezone
from dateutil.relativedelta import *
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.http import HttpResponseRedirect

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

    TestFormSet = modelformset_factory(EventInstance, form=EventInstanceForm, formset=EventInstanceFormSet, extra=len(initial_values))
    taken_events = []

    if request.method == 'POST':
        formset = TestFormSet(request.POST, initial=initial_values, form_kwargs={'user': request.user})
        if formset.is_valid():
            logger.warning("Form is valid")
            for form in formset:
                if form.has_changed():
                    temp_obj = form.save(commit=False)
                    #Fix status codes
                    #If someone takes an EventInstance in need of rescheduling
                    if temp_obj.status == -1:
                        temp_obj.status = 1
                    #If someone takes an EventInstance that is unscheduled
                    elif temp_obj.status == 0:
                        temp_obj.status = 1
                    #If someone untakes an EventInstance that is scheduled
                    elif temp_obj.status == 1:
                        temp_obj.status = -1

                    #Fix host:
                    if request.user.is_authenticated:
                        temp_obj.host = request.user.email
                    else:
                        temp_obj.host = "N/A"
                    logger.warning(temp_obj.__dict__)
                    temp_obj.save()
                    return HttpResponseRedirect('')
        else:
            logger.warning("Formset is invalid")
            for form in formset:
                if any(form.errors):
                    logger.warning(form.errors)
                    logger.warning(form.cleaned_data)
                    taken_event = {
                        'title': form.cleaned_data.get('title'),
                        'start': form.cleaned_data.get('start'),
                        'end': form.cleaned_data.get('end'),
                    }
                    taken_events.append(taken_event)
                    formset = TestFormSet(initial=initial_values, form_kwargs={'user': request.user})
    else:
        formset = TestFormSet(initial=initial_values, form_kwargs={'user': request.user})
    logger.warning(taken_events)
    return render(request, 'test_form.html', {'formset': formset, 'taken_events': taken_events})

