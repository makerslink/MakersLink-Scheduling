from django.db import models
from django.urls import reverse
import uuid
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import datetime
from google.oauth2 import service_account
from dateutil.rrule import *

# New Filesystem
client_secret_fs = FileSystemStorage(location=settings.CALENDAR_PK_DIR)

# Create your models here.
class EventTemplate(models.Model):
    """
    Defines how something will look in the google calendar
    """

    # Fields
    name = models.CharField(max_length=50, help_text="Enter a human-friendly name for this template")
    title = models.CharField(max_length=100, help_text="Enter title to be used for booking")
    header = models.CharField(max_length=200, help_text="Enter a, optional, header for the event to be inserted after the hosts name into the descriptionfield in the calendar event.", null=True, blank=True)
    body = models.TextField(max_length=1000, help_text="Enter a larger body of text to be inserted after the header in the description field in the calendar event", null=True, blank=True)
    calendar = models.ForeignKey('SchedulingCalendar', on_delete=models.SET_NULL, null=True, help_text="Select the calendar to sync events to.")
    synchronize = models.BooleanField(default=True, help_text="If active, scheduled events will be synced to Google calendar upon creation.")

    # Metadata
    class Meta:
        ordering = ["name"]

    # Methods
    def get_absolute_url(self):
        """
         Returns the url to access a particular instance of EventTemplate.
         """
        return reverse('template-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the EventTemplate object (in Admin site etc.)
        """
        return self.name

class SchedulingCalendar(models.Model):
    """
    Defines a Google calendar to insert bookings into
    https://stackoverflow.com/questions/37754999/google-calendar-integration-with-django
    """

    # Data
    TIMEZONES = (
        ("Europe/Stockholm", "Europe/Stockholm"),
    )

    # Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="Unique ID for this calendar")
    name = models.CharField(max_length=50, help_text="Enter a human-friendly name for this Google Calendar")
    google_calendar_id = models.CharField(max_length=250, help_text="Enter a calendar id")
    service_account_username = models.CharField(max_length=250, help_text="Enter the username for the service account used")
    timezone = models.CharField(max_length=50, choices=TIMEZONES, help_text='Calendar timezone')
    service_account = models.FileField(storage=client_secret_fs, help_text='Upload client_secret json-file')
    scope = models.TextField(default="https://www.googleapis.com/auth/calendar", help_text='Enter scope of api calls, change at your own risk')

    # Metadata
    class Meta:
        ordering = ["name"]

    # Methods
    def get_absolute_url(self):
        """
         Returns the url to access a particular instance of SchedulingCalendar.
         """
        return reverse('calendar-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the SchedulingCalendar object (in Admin site etc.)
        """
        return self.name

    def get_credentials(self):
        credentials = service_account.Credentials.from_service_account_file(self.service_account.path, scopes=[self.scope])
        return credentials


class Event(models.Model):
    """
    Defines a booking that users can create themselves.
    User only gets to chose day and time to create a EventInstance
    """
    # Data
    #objects = BookingManager()

    # Fields
    name = models.CharField(max_length=50, help_text="Enter a human-friendly name for this type of Event")
    description = models.CharField(max_length=300, help_text="Enter a description for this type of Event", null=True, blank=True)
    booking_template = models.ForeignKey('EventTemplate', on_delete=models.SET_NULL, null=True, help_text="Select a template for how scheduled Events will look in the calendar.")
    start = models.DateTimeField(help_text="Start of event repetition and start time of events", db_index=True)
    end = models.DateTimeField(help_text="End time of events, must be after start", db_index=True)
    repeat_end = models.DateTimeField(help_text="Date to end repetition")
    rule = models.ForeignKey('SchedulingRule', null=True, blank=True, help_text="Select '----' for a one time only event.", on_delete=models.SET_NULL)

    # Metadata
    class Meta:
        ordering = ["name"]

    # Methods
    def get_absolute_url(self):
        """
         Returns the url to access a particular instance of EventTemplate.
         """
        return reverse('event-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the EventTemplate object (in Admin site etc.)
        """
        return self.name

    def create_eventinstance(self, start, end):
        return EventInstance(event=self, start=start, end=end)

    def get_events(self):


        """
        skapa funktion för att hämta events denna genererar
        skapa funktion för att skapa en "fejkad" EventInstance-objekt
        ta bort riktiga EventInstance från listan (jämför med länkade instances)
            Om instansen finns ska den tas bort
                om den riktiga dessutom är bokningsbar skall den in istället.
        returnera lista
        kanske något för att sortera?
        kanske ska det finnas någon funktion för att skapa en "ta denna" länk
        :return:
        """

class EventManager(models.Manager):
    def get_instances(self, fromTime, untilTime):
        return self.eventinstance_set.filter(start__gte=fromTime, start__lte=untilTime)

class EventInstance(models.Model):
    """
    Each actually scheduled time in the calendar corresponds with this.
    """

    # Data
    STATUS = (
        (-1, 'Reschedule needed'),
        (0, 'Unscheduled'),
        (1, 'Scheduled'),
        (2, 'Cancelled'),
    )

    # Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="Unique ID for this bookinginstance")
    google_calendar_booking_id = models.CharField(max_length=300, help_text="Unique ID from google after instance is created", null=True, blank=True)
    #host = models.ForeignKey('User', on_delete=models.SET_NULL, null=True)
    host = models.CharField(max_length=50, help_text="Enter a name instead of user-key", null=True, blank=True)
    event = models.ForeignKey('Event', on_delete=models.SET_NULL, null=True)
    start = models.DateTimeField(help_text="Start of event")
    end = models.DateTimeField(help_text="End of event")
    status = models.IntegerField(default=0, choices=STATUS, help_text="Instance status")

    # Metadata
    class Meta:
        ordering = ["start", "end"]

    # Methods
    def get_absolute_url(self):
        """
         Returns the url to access a particular instance of EventInstance.
         """
        return reverse('eventinstance-detail', args=[str(self.id)])

    def display_host(self):
        return ''.join([self.host])
    display_host.short_description = "Host"

class SchedulingRule(models.Model):
    #Data
    freqs = (
        ("YEARLY", "Yearly"),
         ("MONTHLY", "Monthly"),
         ("WEEKLY", "Weekly"),
         ("DAILY", "Daily"),
    )

    _week_days = {
        'MO': MO,
        'TU': TU,
        'WE': WE,
        'TH': TH,
        'FR': FR,
        'SA': SA,
        'SU': SU
    }

    #Fields
    name = models.CharField(max_length=50)
    description = models.TextField()
    frequency = models.CharField("frequency", choices=freqs, max_length=10)
    params = models.TextField("params", blank=True)

    #Functions
    def get_absolute_url(self):
        """
         Returns the url to access a particular instance of EventTemplate.
         """
        return reverse('rule-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the EventTemplate object (in Admin site etc.)
        """
        return self.name

    def rrule_frequency(self):
        compatibility_dict = {
            'DAILY': DAILY,
            'MONTHLY': MONTHLY,
            'WEEKLY': WEEKLY,
            'YEARLY': YEARLY
        }
        return compatibility_dict[self.frequency]

    def _weekday_or_number(self, param):
        '''
        Receives a rrule parameter value, returns a upper case version
        of the value if its a weekday or an integer if its a number
        '''
        try:
            return int(param)
        except (TypeError, ValueError):
            uparam = str(param).upper()
            if uparam in SchedulingRule._week_days:
                return SchedulingRule._week_days[uparam]

    def get_params(self, extra_params=""):
        """
        >>> rule = Rule(params = "count:1;bysecond:1;byminute:1,2,4,5")
        >>> rule.get_params()
        {'count': 1, 'byminute': [1, 2, 4, 5], 'bysecond': 1}
        """

        total_params = self.params + ";" + extra_params

        params = total_params.split(';')
        param_dict = []
        for param in params:
            param = param.split(':')
            if len(param) != 2:
                continue

            param = (
                str(param[0]).lower(),
                [x for x in
                 [self._weekday_or_number(v) for v in param[1].split(',')]
                 if x is not None],
            )

            if len(param[1]) == 1:
                param_value = self._weekday_or_number(param[1][0])
                param = (param[0], param_value)
            param_dict.append(param)
        return dict(param_dict)

    def get_events(self, dtstart=None, until=None, extra_params=""):
        params = self.get_params(extra_params=extra_params)
        if (('until' in params) and until):
            del params['until']
        if((until is None) and not('count' in params) and not('until' in params)):
            params['count'] = 10
        if(dtstart is None):
            dtstart = datetime.datetime.now()
        frequency = self.rrule_frequency()
        events = rrule(frequency, dtstart=dtstart, **params)
        return events