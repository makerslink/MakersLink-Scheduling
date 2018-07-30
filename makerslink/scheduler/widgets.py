from bootstrap_datepicker_plus import DateTimePickerInput

class DateTimePicker(DateTimePickerInput):
    format='%Y-%m-%d %H:%M'
    options={"sideBySide":True, "calendarWeeks":True, "locale":"sv"}

class DatePicker(DateTimePickerInput):
    format='%Y-%m-%d'
    options={"calendarWeeks":True, "locale":"sv"}
