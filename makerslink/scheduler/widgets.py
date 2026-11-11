from bootstrap_datepicker_plus.widgets import DatePickerInput, DateTimePickerInput

# Display formats are moment.js formats. The value sent to the server keeps
# the widget's own ISO format, which Django parses.

# 3.x turned the close/clear/today buttons on by default; 6.x does not.
# allowInputToggle opens the picker when the field itself is tapped, not
# only the calendar button next to it.
COMMON_OPTIONS = {"locale": "sv", "showClose": True, "showClear": True,
                  "showTodayButton": True, "allowInputToggle": True}


class DateTimePicker(DateTimePickerInput):
    options = {**COMMON_OPTIONS, "format": "YYYY-MM-DD HH:mm", "sideBySide": True, "calendarWeeks": True}


class DatePicker(DatePickerInput):
    options = {**COMMON_OPTIONS, "format": "YYYY-MM-DD", "calendarWeeks": True}


class DateMonthPicker(DatePickerInput):
    """A date picker that opens on the month view, for period start and end."""
    options = {**COMMON_OPTIONS, "format": "YYYY-MM-DD", "sideBySide": True, "viewMode": "months"}
