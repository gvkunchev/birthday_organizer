from django.urls import path
from portal import views


urlpatterns = [
    path('', views.index),
    path('events', views.events),
    path('users', views.users),
    path('circles', views.circles),
    path('join_circle', views.join_circle),
    path('leave_circle', views.leave_circle),
    path('add_circle', views.add_circle),
    path('edit_circle', views.edit_circle),
    path('settings', views.settings),
    path('add_event', views.add_event),
    path('edit_event', views.edit_event),
    path('event', views.event),
    path('participants_wanted', views.participants_wanted),
    path('add_payment', views.add_payment),
    path('toggle_payment', views.toggle_payment),
    path('remove_payment', views.remove_payment),
    path('add_comment', views.add_comment),
    path('edit_comment', views.edit_comment),
    path('get_total', views.get_total),
    path('join_event', views.join_event),
    path('leave_event', views.leave_event),
    path('become_host', views.become_host),
    path('delete_event', views.delete_event),
    path('toggle_like', views.toggle_like),
    path('change_theme', views.change_theme),
]
