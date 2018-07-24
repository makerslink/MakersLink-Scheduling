from django import forms
from .widgets import DatePicker, DateTimePicker

forms.DateField.widget = DatePicker
forms.DateTimeField.widget = DateTimePicker
