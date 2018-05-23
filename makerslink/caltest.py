from google.oauth2 import service_account
import googleapiclient.discovery
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *


scope = ['https://www.googleapis.com/auth/calendar']
client_secret_path = "/home/bobo/django-apps/makerslink/makerslink/client_secret.json"
calendar_id = 't05c41p3v4hjlcjvmcg8lvohlo@group.calendar.google.com'

def get_credentials():
    credentials = service_account.Credentials.from_service_account_file(client_secret_path, scopes=scope)
    return credentials

def list_events():
    credentials = get_credentials()
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('current time:', now)
    print('Getting the upcoming 10 events')
    eventsResult = service.events().list(calendarId=calendar_id, timeMin=now, maxResults=10, singleEvents=True, orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

def create_event():
    credentials = get_credentials()
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

    event = {
        'summary': 'Google I/O 2015',
        'location': 'Makerspace Linköping',
        'description': 'Värd: Bobo',
        'start': {
            'dateTime': '2018-03-09T18:00:00',
            'timeZone': 'Europe/Stockholm',
        },
        'end': {
            'dateTime': '2018-03-09T21:00:00',
            'timeZone': 'Europe/Stockholm',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [],
        },
    }

    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print('Event created: ',event.get('id'))

def test():
    print("start")
    start = datetime.now()
    #list(rrule(WEEKLY, byweekday=MO, dtstart=start, until=end, wkst=MO))
    for entry in rrule(WEEKLY, byweekday=MO, dtstart=start, interval=1, count=5, wkst=MO):
        print(entry)

def main():
    """
    list_events()
    create_event()
    list_events()
    """
    test()

if __name__ == '__main__':
    main()
##{% if bookingtemplate.body %}<p class="text-success">Uploaded{% else %}<p class="text-warning">None{% endif %}</p></p>