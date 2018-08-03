from django.urls import path
from django.conf.urls import url
import django.contrib.auth.views
from . import views


urlpatterns = [
    #path('', views.index, name='index'),
    path('', views.EventSignupView, name='index'),
]

urlpatterns += [
    path('calendars', views.SchedulingCalendarListView.as_view(), name='calendars'),
    path('calendar/<uuid:pk>', views.SchedulingCalendarDetailView.as_view(), name='calendar-detail'),
    path('calendar/create/', views.SchedulingCalendarCreateView.as_view(), name='calendar-create'),
    path('calendar/<uuid:pk>/update', views.SchedulingCalendarUpdateView.as_view(), name='calendar-update'),
    path('calendar/<uuid:pk>/delete', views.SchedulingCalendarDeleteView.as_view(), name='calendar-delete'),
]

urlpatterns += [
    path('templates', views.EventTemplateListView.as_view(), name='templates'),
    path('template/<int:pk>', views.EventTemplateDetailView.as_view(), name='template-detail'),
    path('template/create/', views.EventTemplateCreateView.as_view(), name='template-create'),
    path('template/<int:pk>/update', views.EventTemplateUpdateView.as_view(), name='template-update'),
    path('template/<int:pk>/delete', views.EventTemplateDeleteView.as_view(), name='template-delete'),
]

urlpatterns += [
    path('rules', views.SchedulingRuleListView.as_view(), name='rules'),
    path('rule/<int:pk>', views.SchedulingRuleDetailView.as_view(), name='rule-detail'),
    path('rule/create/', views.SchedulingRuleCreateView.as_view(), name='rule-create'),
    path('rule/<int:pk>/update', views.SchedulingRuleUpdateView.as_view(), name='rule-update'),
    path('rule/<int:pk>/delete', views.SchedulingRuleDeleteView.as_view(), name='rule-delete'),
]

urlpatterns += [
    path('events', views.EventListView.as_view(), name='events'),
    path('event/<int:pk>', views.EventDetailView.as_view(), name='event-detail'),
    path('event/create/', views.EventCreateView.as_view(), name='event-create'),
    path('event/<int:pk>/update', views.EventUpdateView.as_view(), name='event-update'),
    path('event/<int:pk>/delete', views.EventDeleteView.as_view(), name='event-delete'),
]

urlpatterns += [
    path('joinEvent', views.EventInstanceListView.as_view(), name='joinEvent'),
    path('joinEvent/<uuid:pk>', views.EventInstanceUpdateView.as_view(), name='eventinstance-join'),
    path('joinEvent/<uuid:pk>', views.EventDetailView.as_view(), name='eventinstance-detail'),
]

urlpatterns += [
    path('signup', views.EventSignupView, name='host-signup'),
    path('hosts', views.HostListView.as_view(template_name='host_list.html'), 
    name='hosts'),
]
