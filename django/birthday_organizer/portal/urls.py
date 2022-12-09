from django.urls import path
from portal import views


urlpatterns = [
    path('', views.index),
    path('signup', views.signup),
    path('log_in', views.log_in),
    path('log_out', views.log_out),
    path('events', views.events),
    path('users', views.users),
    path('settings', views.settings),
    path('update_personal_info', views.update_personal_info),
    path('update_password', views.update_password),
    path('add_event', views.add_event),
    path('edit_event', views.edit_event),
    path('event', views.event),
    path('add_payment', views.add_payment),
    path('toggle_payment', views.toggle_payment),
    path('remove_payment', views.remove_payment),
    path('add_comment', views.add_comment),
    path('get_total', views.get_total),
    path('join_event', views.join_event)
]
