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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

# Create your views here.
@login_required
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

class SchedulingCalendarListView(LoginRequiredMixin, generic.ListView):
    model = SchedulingCalendar

class SchedulingCalendarDetailView(LoginRequiredMixin, generic.DetailView):
    model = SchedulingCalendar

class SchedulingCalendarCreateView(LoginRequiredMixin, CreateView):
    model = SchedulingCalendar
    fields = '__all__'

class SchedulingCalendarUpdateView(LoginRequiredMixin, UpdateView):
    model = SchedulingCalendar
    fields = '__all__'

class SchedulingCalendarDeleteView(LoginRequiredMixin, DeleteView):
    model = SchedulingCalendar
    success_url = reverse_lazy('calendars')

class EventTemplateListView(LoginRequiredMixin, generic.ListView):
    model = EventTemplate

class EventTemplateDetailView(LoginRequiredMixin, generic.DetailView):
    model = EventTemplate

class EventTemplateCreateView(LoginRequiredMixin, CreateView):
    model = EventTemplate
    fields = '__all__'

class EventTemplateUpdateView(LoginRequiredMixin, UpdateView):
    model = EventTemplate
    fields = '__all__'

class EventTemplateDeleteView(LoginRequiredMixin, DeleteView):
    model = EventTemplate
    success_url = reverse_lazy('templates')

class SchedulingRuleListView(LoginRequiredMixin, generic.ListView):
    model = SchedulingRule

class SchedulingRuleDetailView(LoginRequiredMixin, generic.DetailView):
    model = SchedulingRule

    def get_context_data(self, **kwargs):
        context = super(SchedulingRuleDetailView, self).get_context_data(**kwargs)
        events = self.object.get_events(extra_params="count:5;")
        context['eventlist'] = events
        return context

class SchedulingRuleCreateView(LoginRequiredMixin, CreateView):
    model = SchedulingRule
    fields = '__all__'

class SchedulingRuleUpdateView(LoginRequiredMixin, UpdateView):
    model = SchedulingRule
    fields = '__all__'

class SchedulingRuleDeleteView(LoginRequiredMixin, DeleteView):
    model = SchedulingRule
    success_url = reverse_lazy('rules')

class EventListView(LoginRequiredMixin, generic.ListView):
    model = Event

class EventDetailView(LoginRequiredMixin, generic.DetailView):
    model = Event

    def get_context_data(self, **kwargs):
        start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start+relativedelta(months=+1)
        context = super(EventDetailView, self).get_context_data(**kwargs)
        events = self.object.get_events(start, end)
        context['eventlist'] = events
        return context

class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    fields = '__all__'
    #form_class = EventForm

class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    fields = '__all__'
    #form_class = EventForm

class EventDeleteView(LoginRequiredMixin, DeleteView):
    model = Event
    success_url = reverse_lazy('events')

@login_required
def EventSignupView(request):
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + relativedelta(months=+3)

    event_objects = Event.objects.all()
    event_list = []
    for event in event_objects:
        event_list += event.get_events(start, end, False)

    event_list = sorted(event_list, key=lambda eventinstance: eventinstance.start)
    initial_values = [(event_instance.as_dict()) for event_instance in event_list]

    eventinstanceFormSet = modelformset_factory(EventInstance, form=EventInstanceForm, formset=EventInstanceFormSet, extra=len(initial_values))

    if request.method == 'POST':
        taken_events = ""
        logger.warning('form is submitted as POST')
        formset = eventinstanceFormSet(request.POST, initial=initial_values, queryset=EventInstance.objects.filter(Q(host=request.user.email)|Q(status__lte=0)))
        logger.warning('starting looping of forms')
        for form in formset:
            if form.is_valid() and form.has_changed():
                logger.warning('form is valid and changed')
                temp_obj = form.save(commit=False)

                if temp_obj.can_take(request.user.email):
                    logger.warning('user can take')
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
                    temp_obj.host = request.user.email

                    # Save
                    logger.warning('saving:'+str(temp_obj.start))
                    temp_obj.save()
                else:
                    logger.warning('user can not take')
                    # Add instance as already taken
                    taken_events += "<tr><td>" + form.cleaned_data.get('title') + "</td>"
                    taken_events += "<td>" + form.cleaned_data.get('start').strftime('%Y-%m-%d %H:%M') + "</td>"
                    taken_events += "<td>" + form.cleaned_data.get('end').strftime('%Y-%m-%d %H:%M') + "</td></tr>"
                    """
                    taken_event = {
                        'title': form.cleaned_data.get('title'),
                        'start': form.cleaned_data.get('start'),
                        'end': form.cleaned_data.get('end'),
                    }
                    taken_events.append(taken_event)
                    """
            else:
                logger.warning('form is invalid or has not changed')
                if any(form.errors):
                    logger.warning('form has errors')
                    logger.warning(form.errors)
                    taken_events += "<tr><td>" + form.cleaned_data.get('title') + "</td>"
                    taken_events += "<td>" + form.cleaned_data.get('start').strftime('%Y-%m-%d %H:%M') + "</td>"
                    taken_events += "<td>" + form.cleaned_data.get('end').strftime('%Y-%m-%d %H:%M') + "</td></tr>"
                    """
                    taken_event = {
                        'title': form.cleaned_data.get('title'),
                        'start': form.cleaned_data.get('start'),
                        'end': form.cleaned_data.get('end'),
                    }
                    taken_events.append(taken_event)
                    """
        logger.warning('done with looping')
        if taken_events != "":
            taken_events = "<b>The following events were not taken due to already being owned by someone else:</b></<br><table><thead><tr><th>Title</th><th>Start</th><th>End</th></tr></thead>" + taken_events + "</table><br><br>"
            logger.warning('adding message')
            messages.info(request, taken_events, extra_tags='safe')
        logger.warning('redirecting')
        return HttpResponseRedirect('')
    else:
        logger.warning('view is GET')
        formset = eventinstanceFormSet(initial=initial_values, queryset=EventInstance.objects.filter(Q(host=request.user.email)|Q(status__lte=0)))
    logger.warning('rendering')
    return render(request, 'eventinstance_host_form.html', {'formset': formset})

