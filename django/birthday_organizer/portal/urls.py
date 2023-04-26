from django.urls import path
from portal import views


urlpatterns = [
    path('', views.index),
    path('events', views.events),
    path('users', views.users),
    path('settings', views.settings),
    path('add_event', views.add_event),
    path('edit_event', views.edit_event),
    path('event', views.event),
    path('add_payment', views.add_payment),
    path('toggle_payment', views.toggle_payment),
    path('remove_payment', views.remove_payment),
    path('add_comment', views.add_comment),
    path('edit_comment', views.edit_comment),
    path('get_total', views.get_total),
    path('join_event', views.join_event),
    path('become_host', views.become_host),
    path('delete_event', views.delete_event),
    path('toggle_like', views.toggle_like),
]
