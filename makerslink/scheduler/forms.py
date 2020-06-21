import logging
logger = logging.getLogger(__name__)

from django import forms
from .widgets import DateMonthPicker, DatePicker
from django.forms import BaseModelFormSet, BaseFormSet, ModelForm, Textarea
from .models import EventTemplate, SchedulingCalendar, Event, EventInstance, SchedulingPeriod, SchedulingRuleExclusion
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime #for checking renewal date range.

"""
1. Calendar - koppling mot google calendar - crud
2. Template - hur skall saker formateras - crud
3. Event - Koppla ihop calendars och templates - crud
4. Instance - Skapa en instance i kalendern
5. Visa instances
6. Boka instance genom att klicka
7. Reschedule/Cancel instance - Detta måste kopplas så att den automatiskt blir inställd efter en viss tid eller dylikt
8. Användare överallt istället för string-generic
9. Skapa ett schema som skapar instancer x-dagar framåt
10. Rapporter för vad som är vad
11. Fixarpass 
12. Bekräfta e-post för registrering
13. Slack-id och tagg-id på användare
14. Skapa rättigheter för de olika funktionerna
15. Skapa en vy där vi kan lägga till icke-medlemmar i grupper (välj grupp, visa lista på användare som inte är med, bocka i och spara)


"""


class PeriodForm(forms.ModelForm):
    add_from_last = forms.BooleanField(help_text="Add hosts from last period.")
    class Meta:
        fields = '__all__'
        model = SchedulingPeriod
        widgets = {
            'start': DateMonthPicker,
            'end': DateMonthPicker,
            'hosts': forms.CheckboxSelectMultiple,
        }
    def save(self, commit=True):
        if self.cleaned_data['add_from_last']:
            self.cleaned_data['hosts'] = SchedulingPeriod.objects.latest('end').hosts.all() | self.cleaned_data['hosts']
        
        return super(PeriodForm, self).save(commit=commit)

class RuleExclusionForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = SchedulingRuleExclusion
        widgets = {
            'excluded_date': DatePicker,
        }

class EventInstanceAdminForm(forms.ModelForm):
    class Meta:
        #fields = '__all__'
        fields = ('status', 'unique_title', 'unique_description', 'participants')
        model = EventInstance

class EventInstanceFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_fields(self, form, index):
        super().add_fields(form, index)

class EventInstanceForm(ModelForm):

    class Meta:
        model = EventInstance
        fields = ('start', 'end', 'status', 'event', 'period')

    def __init__(self, *args, **kwargs):
        super(EventInstanceForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget = forms.HiddenInput()

        if 'event' in self.initial:
            title = Event.objects.get(pk=self.initial["event"]).template.title
        else:
            title = "N/A"
        self.fields["title"] = forms.CharField(required=False, initial=title, widget=forms.HiddenInput())
        
        if 'period' in self.initial:
            period = SchedulingPeriod.objects.get(pk=self.initial["period"]).name
        #    self.fields["period"] = forms.CharField(required=False, initial=period, widget=forms.HiddenInput())
        else:
            period = "N/A"
        self.fields["period_name"] = forms.CharField(required=False, initial=period, widget=forms.HiddenInput())
        
        #logger.warning("EventInstanceForm: %s", self.initial["period"])
        #logger.warning("EventInstanceForm: %s",  self.fields["period"])

        if 'status' in self.initial:
            if self.initial["status"] == 1:
                self.fields["perform_action"] = forms.BooleanField(required=False, label="Take", initial=True)
            else:
                self.fields["perform_action"] = forms.BooleanField(required=False, label="Take", initial=False)
