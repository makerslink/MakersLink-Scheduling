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
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from accounts.models import User
import accounts.models

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
    
class UserIsStaffMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

class SchedulingCalendarListView(UserIsStaffMixin, generic.ListView):
    model = SchedulingCalendar

class SchedulingCalendarDetailView(UserIsStaffMixin, generic.DetailView):
    model = SchedulingCalendar

class SchedulingCalendarCreateView(UserIsStaffMixin, CreateView):
    model = SchedulingCalendar
    fields = '__all__'

class SchedulingCalendarUpdateView(UserIsStaffMixin, UpdateView):
    model = SchedulingCalendar
    fields = '__all__'

class SchedulingCalendarDeleteView(UserIsStaffMixin, DeleteView):
    model = SchedulingCalendar
    success_url = reverse_lazy('calendars')

class EventTemplateListView(UserIsStaffMixin, generic.ListView):
    model = EventTemplate

class EventTemplateDetailView(UserIsStaffMixin, generic.DetailView):
    model = EventTemplate

class EventTemplateCreateView(UserIsStaffMixin, CreateView):
    model = EventTemplate
    fields = '__all__'

class EventTemplateUpdateView(UserIsStaffMixin, UpdateView):
    model = EventTemplate
    fields = '__all__'

class EventTemplateDeleteView(UserIsStaffMixin, DeleteView):
    model = EventTemplate
    success_url = reverse_lazy('templates')

class SchedulingRuleListView(UserIsStaffMixin, generic.ListView):
    model = SchedulingRule

class SchedulingRuleDetailView(UserIsStaffMixin, generic.DetailView):
    model = SchedulingRule

    def get_context_data(self, **kwargs):
        context = super(SchedulingRuleDetailView, self).get_context_data(**kwargs)
        events = self.object.get_events(extra_params="count:5;")
        context['eventlist'] = events
        return context

class SchedulingRuleCreateView(UserIsStaffMixin, CreateView):
    model = SchedulingRule
    fields = '__all__'

class SchedulingRuleUpdateView(UserIsStaffMixin, UpdateView):
    model = SchedulingRule
    fields = '__all__'

class SchedulingRuleDeleteView(UserIsStaffMixin, DeleteView):
    model = SchedulingRule
    success_url = reverse_lazy('rules')

class EventListView(UserIsStaffMixin, generic.ListView):
    model = Event

class EventDetailView(UserIsStaffMixin, generic.DetailView):
    model = Event

    def get_context_data(self, **kwargs):
        start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start+relativedelta(months=+1)
        context = super(EventDetailView, self).get_context_data(**kwargs)
        events = self.object.get_events(start, end)
        context['eventlist'] = events
        return context

class EventCreateView(UserIsStaffMixin, CreateView):
    model = Event
    fields = '__all__'
    #form_class = EventForm

class EventUpdateView(UserIsStaffMixin, UpdateView):
    model = Event
    fields = '__all__'
    #form_class = EventForm

class EventDeleteView(UserIsStaffMixin, DeleteView):
    model = Event
    success_url = reverse_lazy('events')

class EventInstanceListView(LoginRequiredMixin, generic.ListView):
    model = EventInstance
    
class EventInstanceUpdateView(LoginRequiredMixin, UpdateView):
    model = EventInstance
    # Empty field list as we save to the current user when submitted.
    fields = ( )
    
    def form_valid(self, form):
        event = form.save(commit=False)
        event.participants.add(self.request.user)  # use your own profile here
        event.save()
        return HttpResponseRedirect(self.get_success_url())

class HostListView(UserIsStaffMixin, generic.ListView):
    model = accounts.models.User
    
    def get_queryset(self):
        queryset = accounts.models.User.objects.all().annotate(
            events_count=Count('eventinstance', filter=Q(eventinstance__status=1)))
        
        return queryset


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
        formset = eventinstanceFormSet(request.POST, initial=initial_values, queryset=EventInstance.objects.filter(Q(host=request.user)|Q(status__lte=0)))

        logger.warning('starting looping of forms')
        for form in formset:
            if form.has_changed() and 'perform_action' in form.changed_data:
                logger.warning('form has changed')
                if form.is_valid():
                    #logger.warning(str(form.cleaned_data.get('perform_action')))
                    logger.warning(form.changed_data)
                    #logger.warning('Handling form starting at: ' + form.cleaned_data.get('start').strftime('%Y-%m-%d %H:%M'))
                    logger.warning('form is valid')
                    temp_obj = form.save(commit=False)

                    if temp_obj.can_take(request.user):
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
                        temp_obj.host = request.user

                        # Save
                        logger.warning('saving')
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
                    #logger.warning('Handling form starting at: ' + form.cleaned_data.get('start').strftime('%Y-%m-%d %H:%M'))
                    logger.warning('form is invalid')
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
            else:
                logger.warning('form has not changed')
        logger.warning('done with looping')
        if taken_events != "":
            taken_events = "<b>The following events were not taken due to already being owned by someone else:</b></<br><table><thead><tr><th>Title</th><th>Start</th><th>End</th></tr></thead>" + taken_events + "</table><br><br>"
            logger.warning('adding message')
            messages.info(request, taken_events, extra_tags='safe')
        logger.warning('redirecting')
        return HttpResponseRedirect('')
    else:
        logger.warning('view is GET')
        formset = eventinstanceFormSet(initial=initial_values, queryset=EventInstance.objects.filter(Q(host=request.user)|Q(status__lte=0)))
    logger.warning('rendering')
    #request.session['signup_initialdata'] =initial_values
    return render(request, 'eventinstance_host_form.html', {'formset': formset})

