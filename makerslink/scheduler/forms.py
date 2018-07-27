import logging
logger = logging.getLogger(__name__)

from django import forms
from django.forms import BaseModelFormSet, BaseFormSet, ModelForm, Textarea
from bootstrap_datepicker_plus import DateTimePickerInput
from .models import User, EventTemplate, SchedulingCalendar, Event, EventInstance
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
class EventInstanceFormSet(BaseModelFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)

class RegistrationForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['email', ]

class EventInstanceForm(ModelForm):

    class Meta:
        model = EventInstance
        fields = ('start', 'end', 'status', 'event')

    def __init__(self, *args, **kwargs):
        super(EventInstanceForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget = forms.HiddenInput()

        title = Event.objects.get(pk=self.initial["event"]).template.title
        self.fields["title"] = forms.CharField(required=False, initial=title, widget=forms.HiddenInput())

        if self.initial["status"] == 1:
            self.fields["perform_action"] = forms.BooleanField(required=False, label="Take", initial=True)
        else:
            self.fields["perform_action"] = forms.BooleanField(required=False, label="Take", initial=False)

        logger.warning('start')
        logger.warning(self.__dict__)
