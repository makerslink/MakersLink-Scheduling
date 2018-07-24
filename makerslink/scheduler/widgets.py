from bootstrap_datepicker_plus import DateTimePickerInput

class DateTimePicker(DateTimePickerInput):
    format='%Y-%m-%d %H:%M:%S'
    options={"sideBySide":True, "calendarWeeks":True,}

class DatePicker(DateTimePickerInput):
    format='%Y-%m-%d'
    options={"calendarWeeks":True}
