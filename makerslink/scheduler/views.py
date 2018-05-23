from django.shortcuts import render
from .models import BookingTemplate, BookingCalendar, Booking, BookingInstance, SchedulingRule
import datetime
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

# Create your views here.
def index(request):
    now = datetime.datetime.now().isoformat()
    num_host_needed = BookingInstance.objects.filter(status__lte=0, start__gte=now).count()

    return render(
        request,
        'index.html',
        context={
            'num_host_needed' :num_host_needed
        },
    )

class BookingCalendarListView(generic.ListView):
    model = BookingCalendar

class BookingCalendarDetailView(generic.DetailView):
    model = BookingCalendar

class BookingCalendarCreateView(CreateView):
    model = BookingCalendar
    fields = '__all__'

class BookingCalendarUpdateView(UpdateView):
    model = BookingCalendar
    fields = '__all__'

class BookingCalendarDeleteView(DeleteView):
    model = BookingCalendar
    success_url = reverse_lazy('calendars')

class BookingTemplateListView(generic.ListView):
    model = BookingTemplate

class BookingTemplateDetailView(generic.DetailView):
    model = BookingTemplate

class BookingTemplateCreateView(CreateView):
    model = BookingTemplate
    fields = '__all__'

class BookingTemplateUpdateView(UpdateView):
    model = BookingTemplate
    fields = '__all__'

class BookingTemplateDeleteView(DeleteView):
    model = BookingTemplate
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