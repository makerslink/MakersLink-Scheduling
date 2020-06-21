from django.urls import path
from django.conf.urls import url
import django.contrib.auth.views
from . import views

# Signup for eventinstance
urlpatterns = [
    #path('', views.index, name='index'),
    path('', views.EventSignupView, name='index'),
]
# Calendars
urlpatterns += [
    path('calendars', views.SchedulingCalendarListView.as_view(), name='calendars'),
    path('calendar/<uuid:pk>', views.SchedulingCalendarDetailView.as_view(), name='calendar-detail'),
    path('calendar/create/', views.SchedulingCalendarCreateView.as_view(), name='calendar-create'),
    path('calendar/<uuid:pk>/update', views.SchedulingCalendarUpdateView.as_view(), name='calendar-update'),
    path('calendar/<uuid:pk>/delete', views.SchedulingCalendarDeleteView.as_view(), name='calendar-delete'),
]
# Templates
urlpatterns += [
    path('templates', views.EventTemplateListView.as_view(), name='templates'),
    path('template/<int:pk>', views.EventTemplateDetailView.as_view(), name='template-detail'),
    path('template/create/', views.EventTemplateCreateView.as_view(), name='template-create'),
    path('template/<int:pk>/update', views.EventTemplateUpdateView.as_view(), name='template-update'),
    path('template/<int:pk>/delete', views.EventTemplateDeleteView.as_view(), name='template-delete'),
]
# Rules
urlpatterns += [
    path('rules', views.SchedulingRuleListView.as_view(), name='rules'),
    path('rule/<int:pk>', views.SchedulingRuleDetailView.as_view(), name='rule-detail'),
    path('rule/create/', views.SchedulingRuleCreateView.as_view(), name='rule-create'),
    path('rule/<int:pk>/update', views.SchedulingRuleUpdateView.as_view(), name='rule-update'),
    path('rule/<int:pk>/delete', views.SchedulingRuleDeleteView.as_view(), name='rule-delete'),
]
# Events
urlpatterns += [
    path('events', views.EventListView.as_view(), name='events'),
    path('event/<int:pk>', views.EventDetailView.as_view(), name='event-detail'),
    path('event/create/', views.EventCreateView.as_view(), name='event-create'),
    path('event/<int:pk>/update', views.EventUpdateView.as_view(), name='event-update'),
    path('event/<int:pk>/delete', views.EventDeleteView.as_view(), name='event-delete'),
]
# SchedulingPeriods
urlpatterns += [
    path('periods', views.PeriodListView.as_view(), name='periods'),
    path('period/<int:pk>', views.PeriodDetailView.as_view(), name='period-detail'),
    path('period/create/', views.PeriodCreateView.as_view(), name='period-create'),
    path('period/<int:pk>/update', views.PeriodUpdateView.as_view(), name='period-update'),
    path('period/<int:pk>/delete', views.PeriodDeleteView.as_view(), name='period-delete'),
]
# Join as participant
urlpatterns += [
    path('joinEvent', views.EventInstanceListView.as_view(), name='joinEvent'),
    path('joinEvent/<uuid:pk>', views.EventInstanceUpdateView.as_view(), name='eventinstance-join'),
    path('joinEvent/<uuid:pk>', views.EventDetailView.as_view(), name='eventinstance-detail'),
]
# Host details
urlpatterns += [
    path('host/<str:slug>', views.HostDetailView.as_view(), name='host-detail'),
    path('profile', views.ProfileView.as_view(), name='profile'),
    path('signup', views.EventSignupView, name='host-signup'),
    path('hosts/<str:filter>', views.HostListView.as_view(template_name='host_list.html'), name='hosts_filter'),
    path('hosts', views.HostListView.as_view(template_name='host_list.html'), name='hosts'),
]
# SchedulingRuleExclusion
urlpatterns += [
    path('ruleexclusions', views.SchedulingRuleExclusionListView.as_view(), name='ruleexclusions'),
    path('ruleexclusion/<int:pk>', views.SchedulingRuleExclusionDetailView.as_view(), name='ruleexclusion-detail'),
    path('ruleexclusion/create/', views.SchedulingRuleExclusionCreateView.as_view(), name='ruleexclusion-create'),
    path('ruleexclusion/<int:pk>/update', views.SchedulingRuleExclusionUpdateView.as_view(), name='ruleexclusion-update'),
    path('ruleexclusion/<int:pk>/delete', views.SchedulingRuleExclusionDeleteView.as_view(), name='ruleexclusion-delete'),
]

# EventInstance admin
urlpatterns += [
    path('eventinstances-admin', views.EventInstanceAdminListView.as_view(), name='eventinstances-admin'),
    path('eventinstance-admin/<uuid:pk>', views.EventInstanceAdminDetailView.as_view(), name='eventinstance-admin-detail'),
    path('eventinstance-admin/<uuid:pk>/update', views.EventInstanceAdminUpdateView.as_view(), name='eventinstance-admin-update'),
    path('eventinstance-admin/<uuid:pk>/delete', views.EventInstanceAdminDeleteView.as_view(), name='eventinstance-admin-delete'),
]
