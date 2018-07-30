from django import forms
from .widgets import DatePicker, DateTimePicker

forms.DateField.widget = DatePicker
forms.DateTimeField.widget = DateTimePicker

default_app_config ='scheduler.apps.SchedulerConfig'
