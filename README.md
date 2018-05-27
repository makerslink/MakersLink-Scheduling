# MakersLink-Scheduling
Project to develop a system to schecdule and book opening times at MakersLink

Rough roadmap:
1. Clean up existing code and rename models [DONE]
-Booking=>Event
-BookingInstance=>EventInstance
-Bookingrule=>SchedulingRule
-BookingTemplate=>EventTemplate
-Calendar=>SchedulingCalendar
2. Make generation of Events go [IN PROGRESS]
3. Make creation of EventInstance from Event possible
4. Require logged in user for all functions
5. EventInstance connected to user
6. Google Calendar Integration
7. ???
?. Rescheduling / Cancellation of EventInstance
?. Notification to email/slack
?. CSV-export?
