import logging
logger = logging.getLogger(__name__)

from django.db import models
from django.urls import reverse
import uuid
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import datetime, pytz
from google.oauth2 import service_account
import googleapiclient.discovery
from dateutil.rrule import *
import accounts.models
from .fields import ParticipantKeyField
from django.db.models import Q, Count, Max

# New Filesystem
client_secret_fs = FileSystemStorage(location=settings.CALENDAR_PK_DIR)

# Create your models here.
class EventTemplate(models.Model):
    """
    Defines how something will look in the google calendar
    """

    # Fields
    name = models.CharField(max_length=50, help_text="Enter a human-friendly name for this template")
    count_key = models.CharField(max_length=1, help_text="Key displayed when counting participantcy", default = 'D')
    title = models.CharField(max_length=100, help_text="Enter title to be used for booking")
    header = models.CharField(max_length=200, help_text="Enter a, optional, header for the event to be inserted after the hosts name into the descriptionfield in the calendar event.", null=True, blank=True)
    body = models.TextField(max_length=1000, help_text="Enter a larger body of text to be inserted after the header in the description field in the calendar event", null=True, blank=True)
    num_participants = models.IntegerField(default = 0, help_text="Number of participants, -1 for infinite")
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

    def createEventEntry(self, host, start, end, status):
        if self.synchronize:
            data = self._createUpdatedEventData(host, start, end, status)
            #logger.warning("Data:")
            #logger.warning(data)
            #return True
            return self.calendar.createEvent(data)
        else:
            return True


    def updateEventEntry(self, booking_id, host, start, end, status):
        if self.synchronize:
            data =self._createUpdatedEventData(host, start, end, status)
            #logger.warning("Data:")
            #logger.warning(data)
            #return True
            return self.calendar.updateEvent(booking_id, data)
        else:
            return True

    def _createUpdatedEventData(self, host, start, end, status, unique_title="", unique_description=""):
        #logger.warning("createEventData:start: %s", start)
        if status == 2:
            if unique_title == "":
                summary = settings.CANCELLED_TITLE + self.title
            else:
                summary = unique_title + self.title

            if unique_description == "":
                description = settings.CANCELLED_DESCRIPTION
            else:
                description = unique_description
        else:
            summary = self.title

            description = 'Värd: ' + str(host.slackId)
            if self.header:
                description += "\n" + self.header
            if self.body:
                description += "\n" + self.body

        calendarTZ = pytz.timezone(self.calendar.timezone)
        event_data = {
            'summary': summary,
            'location': 'Makerspace Linköping',
            'description': description,
            'start': {
                'dateTime': start.astimezone(calendarTZ).strftime('%Y-%m-%dT%H:%M:%S'),
                'timeZone': self.calendar.timezone,
            },
            'end': {
                'dateTime': end.astimezone(calendarTZ).strftime('%Y-%m-%dT%H:%M:%S'),
                'timeZone': self.calendar.timezone,
            },
            'reminders': {
                'useDefault': False,
                'overrides': [],
            },
        }

        return event_data

    def deleteEventEntry(self, booking_id):
        if self.synchronize:
            return self.calendar.deleteEvent(booking_id)
        else:
            return True

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
    service_account = models.FileField(storage=client_secret_fs, help_text='Upload client_secret json-file', null=True, blank=True)
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

    def createEvent(self, data):
        logger.warning("SchedulingCalendar:createEvent called")
        credentials = service_account.Credentials.from_service_account_file(self.service_account.path, scopes=[self.scope])
        service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
        try:
            event = service.events().insert(calendarId=self.google_calendar_id, body=data).execute()
            return event.get('id')
        except:
            raise ValueError("Could not create event in calendar")

    def updateEvent(self, id, data):
        logger.warning("SchedulingCalendar:updateEvent called")
        credentials = service_account.Credentials.from_service_account_file(self.service_account.path, scopes=[self.scope])
        service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
        try:
            service.events().update(calendarId=self.google_calendar_id, eventId=id, body=data).execute()
            return True
        except:
            raise ValueError("Could not update event in calendar")

    def deleteEvent(self, id):
        logger.warning("SchedulingCalendar:deleteEvent called")
        credentials = service_account.Credentials.from_service_account_file(self.service_account.path, scopes=[self.scope])
        service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
        try:
            service.events().delete(calendarId=self.google_calendar_id, eventId=id).execute()
            return True
        except:
            raise ValueError("Could not delete event in calendar")

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
    template = models.ForeignKey('EventTemplate', on_delete=models.SET_NULL, null=True, help_text="Select a template for how scheduled Events will look in the calendar.")
    start = models.DateTimeField(help_text="Start of event repetition and start time of events", db_index=True)
    end = models.DateTimeField(help_text="End time of events, must be after start", db_index=True)
    repeat_end = models.DateTimeField(help_text="Date to end repetition", null=True, blank=True)
    rule = models.ForeignKey('SchedulingRule', null=True, blank=True, help_text="Select '----' for a one time only event.", on_delete=models.SET_NULL)

    # Metadata
    class Meta:
        ordering = ["name"]

    # Methods
    
    @property
    def max_num_participants(self):
        return self.template.num_participants
    
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

    def create_eventinstance(self, start, end=None):
        if end is None:
            end = start + (self.end - self.start)
        #logger.warning("create_eventinstacreate_eventinstancence:start: %s", start)
        #logger.warning("create_eventinstance:end: %s", end)
        
        period = SchedulingPeriod.objects.filter(start__lte=start, end__gte=end)
        
        if period.count() == 1:
       	    period = period[0]
       	else:
            period = None
            
        event = EventInstance(id=None, event=self, start=start, end=end, status=0, period=period)
        
        return event

    def get_event_list(self, from_date, until_date):
        #logger.warning("Event:get_event_list called")
        #logger.warning("name: %s", self.name)
        # logger.warning("Event:get_event_list:from_date: %s", from_date)
        # logger.warning("Event:get_event_list:until_date: %s", until_date)
        #logger.warning("Event:get_event_list:self.start: %s", self.start.tzinfo)
        #logger.warning("Event:get_event_list:self.end: %s", self.end)

        # Create list of Events
        event_list = []
        # Check if this Event is meant to be started yet
        if self.start > until_date:
            # logger.warning("Event:get_event_list:Start parameter not within range")
            return event_list
        # If there is a rule for repetition
        if self.rule is not None:
            # logger.warning("Event:get_event_list:Rule for repetition found")
            # Calculate the duration of events
            event_duration = self.end - self.start

            # Check if Event starts later than given date
            # Set the start to the Events start if later
            if self.start > from_date:
                from_date = self.start
            else:
            	# Set the date to the given startdate but keep the same time if earlier
                # As we are combining a current date with a time that might have
                # been set in with another DST set up, we have to convert the time
                # to local at the past timezone and convert it back to UTC with
                # timezone for current local.
                tz = pytz.timezone(settings.TIME_ZONE)
                from_date = datetime.datetime.combine(from_date.date(), self.start.astimezone(tz).time()).astimezone(pytz.timezone("utc"))
                #from_date = datetime.datetime.combine(from_date.date(), self.start.time(), self.start.tzinfo)
            # Check if there is a date set to stop generating events, use that instead of given date if it is before given date
            if self.repeat_end and self.repeat_end < until_date:
                until_date = self.repeat_end
            #logger.warning("Event:get_event_list:from_date: %s", from_date)
            #logger.warning("Event:get_event_list:until_date: %s", until_date)
            start_list = self.rule.get_events(from_date, until_date)

            for startdate in start_list:
                event_instance = self.create_eventinstance(startdate, startdate+event_duration)
                if event_instance.period:
                    event_list.append(event_instance)
        # If this is a single Event
        else:
            # logger.warning("Event:get_event_list:No rule for repetition found, adding single event")
            #logger.warning("get_event_list:single: %s", self.start)
            event_instance =self.create_eventinstance(self.start)
            if event_instance.period:
                event_list.append(event_instance)

        return event_list

    """
    Retrieves events between two dates
    If replace=True it replaces generated events with actual objects from DB
    If replace=False it removes generated events where there is an actual object in DB but does not replace it.
    """
    def get_events(self, from_date, until_date, replace=True):
        #logger.warning("Event:get_events called")
        #logger.warning("Event:get_events:from_date: %s", from_date)
        #logger.warning("Event:get_events:until_date: %s", until_date)

        # Get all actual EventInstances created from this Event
        event_instances = self.eventinstance_set.all()
        ## logger.warning("event_instances is: %s", event_instances)
        # Create an EventReplacer object containing these EventInstances
        event_replacer = EventReplacer(event_instances)
        # Generate EventInstances that this Event can create between dates
        generated_events = self.get_event_list(from_date, until_date)
        ## logger.warning("generated_events is: %s", generated_events)
        # Create list to hold a combination of generated and actual EventInstance
        final_eventlist = []
        # Go through all generated EventInstances
        for event_instance in generated_events:
            # Check if a generated EventInstance coincides with an actual EventInstance and add it
            if event_replacer.has_eventinstance(event_instance):
                if replace:
                    # logger.warning("Replacing with real event")
                    final_eventlist.append(event_replacer.get_eventinstance(event_instance))
                #else:
                    # logger.warning("Skipping event since replace=False")
            # If it doesn't, add the generated EventInstance
            else:
                # logger.warning("Adding generated event with id:"+str(event_instance.id))
                final_eventlist.append(event_instance)

        # Finally we add the straggling EventInstances that coincides with these dates unless replace is false in which case we only want generated events
        if replace:
            final_eventlist += event_replacer.get_straggling_eventinstances(from_date, until_date)
        # Return list
        return final_eventlist

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

class EventReplacer(object):
    """
    Used to replace generated Events with actual EventInstances
    """
    # Create a dict to keep track of actual EventInstances when creating an instance of this class
    def __init__(self, event_instances):
        lookup = [((event_instance.event.id, event_instance.start, event_instance.end), event_instance) for event_instance in event_instances]
        self.lookup = dict(lookup)

    # Return an actual EventInstance that matches "event_instance" and remove it since it has been matched
    def get_eventinstance(self, event_instance):
        return self.lookup.pop((event_instance.event.id, event_instance.start, event_instance.end), event_instance)

    # Check if an EventInstance exists in the list or raise an error if something goes wrong
    def has_eventinstance(self, event_instance):
        try:
            return (event_instance.event.id, event_instance.start, event_instance.end) in self.lookup
        except TypeError:
            if not self.lookup:
                return False
            else:
                raise TypeError('A problem with checking if an actual EventInstace exists occured!')

    # Return stragglers that start between the given dates. This can happen if you schedule events and then change the rule generating events
    def get_straggling_eventinstances(self, from_date, until_date):
        return [event_instance for _, event_instance in list(self.lookup.items()) if (event_instance.start < until_date and event_instance.start >= from_date and not event_instance.status == 2)]

class EventManager(models.Manager):
    def get_instances(self, fromTime, untilTime):
        return self.eventinstance_set.filter(start__gte=fromTime, start__lte=untilTime)

class EventInstance(models.Model):
    """
    Each actually scheduled time in the calendar corresponds with this.
    """

    # Data
    STATUS = (
        (-1, 'Ombokning krävs'),
        (0, 'Ledigt'),
        (1, 'Bokat'),
        (2, 'Inställt'),
    )
    
    # Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="Unique ID for this bookinginstance")
    google_calendar_booking_id = models.CharField(max_length=300, help_text="Unique ID from google after instance is created", null=True, blank=True)
    host = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    participants = models.ManyToManyField('accounts.User', related_name="participants", blank=True)
    event = models.ForeignKey('Event', on_delete=models.SET_NULL, null=True)
    start = models.DateTimeField(help_text="Start of event")
    end = models.DateTimeField(help_text="End of event")
    status = models.IntegerField(default=0, choices=STATUS, help_text="Instance status")
    period = models.ForeignKey('SchedulingPeriod', on_delete=models.SET_NULL, null=True, blank=True)
    unique_title = models.CharField(max_length=100, default="", blank=True, help_text="Enter title to be inserted before the header when cancelling, leave blank to use default: {}".format(settings.CANCELLED_TITLE))
    unique_description = models.CharField(max_length=400, default="", blank=True, help_text="Enter a description for a cancelled event, leave blank to use default: {}".format(settings.CANCELLED_DESCRIPTION))

    @property
    def statusText(self):
        return EventInstance.STATUS[self.status + 1][1]
    
    @property
    def title(self):
        return self.event.template.title
    
    @property
    def header(self):
        return self.event.template.header
    
    @property
    def body(self):
        return self.event.template.body
    
    @property
    def max_num_participants(self):
        return self.event.template.num_participants
    
    @property
    def template(self):
        return self.event.template

    # Metadata
    class Meta:
        ordering = ["start", "end"]
        unique_together = ('event', 'start', 'end')

    # Methods
    def get_absolute_url(self):
        """
         Returns the url to access a particular instance of EventInstance.
         """
        return reverse('eventinstance-detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        logger.warning('EventInstance save called')
        if self.google_calendar_booking_id is not None:
            logger.warning("Updating calendar entry with ID: " + str(self.google_calendar_booking_id))

            if not self.event.template.updateEventEntry(self.google_calendar_booking_id, self.host, self.start, self.end, self.status):
                raise ValueError('Could not update calendar')
        else:
            logger.warning("Creating new calendar entry")
            calendar_id = self.event.template.createEventEntry(self.host, self.start, self.end, self.status)
            if isinstance(calendar_id, bool):
                logger.warning('No non-boolean ID was returned, not saving value as calendar id')
            else:
                logger.warning('Inserting new calendar ID into object')
                self.google_calendar_booking_id = calendar_id

        logger.warning("Calling super().save()")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.google_calendar_booking_id is not None:
            if not self.event.template.updateEventEntry(self.google_calendar_booking_id, self.host, self.start, self.end, self.status):
                raise ValueError('Could not update calendar')
        super().delete(*args, **kwargs)

    def display_host(self):
        return ''.join([self.host.email])
    display_host.short_description = "Host"

    def as_dict(self):
        if self.id == None:
            return {
            'google_calendar_booking_id': self.google_calendar_booking_id,
            'host': str(self.host),
            'event': self.event.id,
            'start': self.start,
            'end': self.end,
            'status': self.status,
            'period': self.period.id
        }
        else:
            return {
                'id': str(self.id),
                'google_calendar_booking_id': self.google_calendar_booking_id,
                'host': str(self.host),
                'event': self.event.id,
                'start': self.start.strftime('%Y-%m-%d %H:%M:%S'),
                'end': self.end.strftime('%Y-%m-%d %H:%M:%S'),
                'status': self.status,
            	'period': self.period.id
            }

    def can_take(self, user):
        if self.status > 0:
            return self.host == user
        else:
            return True

    def __str__(self):
        """
        String for representing the EventTemplate object (in Admin site etc.)
        """
        if self.host and self.period:
            return self.title+"("+self.host.slackId+", "+self.period.__str__()+")"
        else:
            return self.title

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
    use_exclusions = models.BooleanField(default=True,
                                      help_text="If active, this rule for generating dates will ignore excluded dates generated dates falling on those dates will not be added.")

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
        #logger.warning("Rule:get_events called")
        #logger.warning("dtstart: %s", dtstart)
        #logger.warning("until: %s", until)
        #logger.warning("name: %s", self.name)
        params = self.get_params(extra_params=extra_params)
        if (('until' in params) and until):
            del params['until']
        if((until is None) and not('count' in params) and not('until' in params)):
            params['count'] = 10
        if(dtstart is None):
            dtstart = datetime.datetime.now()
        #if not 'tzid' in params:
        #    params['tzid'] = settings.TIME_ZONE
        frequency = self.rrule_frequency()
        # logger.warning("params: %s", params)
        # Move time to timezone currently used and make time objects unaware to avoid any problems with rrule
        if until:
            until = until.astimezone(pytz.timezone(settings.TIME_ZONE))
            until = until.replace(tzinfo=None)
        dtstart = dtstart.astimezone(pytz.timezone(settings.TIME_ZONE))
        dtstart = dtstart.replace(tzinfo=None)

        # Changing from rrule to rruleset
        #events = rrule(frequency, dtstart=dtstart, until=until, **params)
        rules = rruleset()
        rules.rrule(rrule(frequency, dtstart=dtstart, until=until, **params))

        if self.use_exclusions:
            #Here we should add all excluded dates
            if until:
                rule_exclusions = SchedulingRuleExclusion.objects.filter(
                    excluded_date__range=(dtstart.date(), until.date()))
            else:
                rule_exclusions = SchedulingRuleExclusion.objects.filter(
                    excluded_date__gte=dtstart.date())
            for rule_exclusion in rule_exclusions:
                excluded_date = rule_exclusion.excluded_date
                exclusion = dtstart.replace(year=excluded_date.year, month=excluded_date.month, day=excluded_date.day)
                rules.exdate(exclusion)
        
        #events = rules.between(dtstart, until)
        events = rules

        tz = pytz.timezone(settings.TIME_ZONE)
        #logger.warning("get_events:tz"+tz)
        updatedEvents = []
        for event in events:
            updatedEvents.append(tz.normalize(tz.localize(event)).astimezone(pytz.utc))
        
        #for event in updatedEvents:
        #    logger.warning("get_events: %s", event)
        return updatedEvents

class SchedulingPeriod(models.Model):
    
    #Fields
    start = models.DateField(help_text="Start of period", db_index=True)
    end = models.DateField(help_text="End of period", db_index=True)
    num_required_events = models.IntegerField(default = 6, help_text="Number of events a host should have in this period")
    participant_key_string = ParticipantKeyField(default = "", help_text="A string representing the events a host is required to be a participant to in this period", max_length=10)
    
    @property
    def name(self):
        return self.start.strftime('%Y %b') + "-" + self.end.strftime('%b')
    
    #Functions
    def get_absolute_url(self):
        """
         Returns the url to access a particular instance of SchedulingPeriod.
         """
        return reverse('period-detail', args=[str(self.id)])
    
    def get_participant_key_list(self):
        userParticipantList = accounts.models.User.objects.all().order_by('eventinstance__participants__slackId', 'eventinstance__period', 'eventinstance__event__template__count_key').annotate(
            participantName = Max('eventinstance__participants__slackId'), keyChar=Max('eventinstance__event__template__count_key', filter=Q(eventinstance__period=self.id)))
        
        currentUser = None
        resultList = {}
        for userParticipant in userParticipantList:
            #logger.warning("get_participant_key_list: %s", userParticipant.participantName)
            if (currentUser == None or currentUser != userParticipant.participantName) and userParticipant.participantName != None:
                currentUser = userParticipant.participantName
                resultList[currentUser] = "";
            if currentUser != None and userParticipant.keyChar != None:
                resultList[currentUser] = resultList[currentUser] + userParticipant.keyChar
        
        return resultList
    
    def get_host_count_list(self):
        userHostList = accounts.models.User.objects.all().order_by('slackId', 'eventinstance__period').annotate(
            host_count=Count('slackId', filter=Q(eventinstance__status=1, eventinstance__period=self.id)))
        
        return userHostList
    
    def get_host_count_key_list(self):
        count_list = self.get_host_count_list()
        key_list = self.get_participant_key_list()
        resultList = {}
        
        for host in count_list:
            resultList[host.slackId] = str(host.host_count)
            if host.slackId in key_list:
                resultList[host.slackId] = resultList[host.slackId] + " " + key_list[host.slackId]
        
        return resultList
    
    def get_all_host_count_key_lists():
        periodList = SchedulingPeriod.objects.all().order_by('-start')
        
        resultList = {}
        
        for period in periodList:
            for user, count_key in period.get_host_count_key_list().items():
                if user not in resultList:
                    resultList[user] = {}
                resultList[user][period] = count_key
        
        return resultList
            
    
    def __str__(self):
        """
        String for representing the EventTemplate object (in Admin site etc.)
        """
        return self.name


class SchedulingRuleExclusion(models.Model):
    # Fields
    excluded_date = models.DateField(help_text="Date to exclude", db_index=True)
    description = models.TextField()

    @property
    def name(self):
        return '{} ({})'.format(self.excluded_date.strftime("%Y-%m-%d"), self.description)

    class Meta:
        ordering = ["excluded_date"]

    # Functions
    def get_absolute_url(self):
        """
         Returns the url to access a particular instance of SchedulingRuleExclusion.
         """
        return reverse('ruleexclusion-detail', args=[str(self.id)])

    def __str__(self):
        """
        String for representing the SchedulingRuleExclusion object (in Admin site etc.)
        """
        return self.name
