from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
]

urlpatterns += [
    path('calendars', views.BookingCalendarListView.as_view(), name='calendars'),
    path('calendar/<uuid:pk>', views.BookingCalendarDetailView.as_view(), name='calendar-detail'),
    path('calendar/create/', views.BookingCalendarCreateView.as_view(), name='calendar-create'),
    path('calendar/<uuid:pk>/update', views.BookingCalendarUpdateView.as_view(), name='calendar-update'),
    path('calendar/<uuid:pk>/delete', views.BookingCalendarDeleteView.as_view(), name='calendar-delete'),
]

urlpatterns += [
    path('templates', views.BookingTemplateListView.as_view(), name='templates'),
    path('template/<int:pk>', views.BookingTemplateDetailView.as_view(), name='template-detail'),
    path('template/create/', views.BookingTemplateCreateView.as_view(), name='template-create'),
    path('template/<int:pk>/update', views.BookingTemplateUpdateView.as_view(), name='template-update'),
    path('template/<int:pk>/delete', views.BookingTemplateDeleteView.as_view(), name='template-delete'),
]

urlpatterns += [
    path('rules', views.SchedulingRuleListView.as_view(), name='rules'),
    path('rule/<int:pk>', views.SchedulingRuleDetailView.as_view(), name='rule-detail'),
    path('rule/create/', views.SchedulingRuleCreateView.as_view(), name='rule-create'),
    path('rule/<int:pk>/update', views.SchedulingRuleUpdateView.as_view(), name='rule-update'),
    path('rule/<int:pk>/delete', views.SchedulingRuleDeleteView.as_view(), name='rule-delete'),
]