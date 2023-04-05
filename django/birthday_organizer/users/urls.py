from django.urls import path
from users import views


urlpatterns = [
    path('signup', views.signup),
    path('log_in', views.log_in),
    path('log_out', views.log_out),
    path('update_personal_info', views.update_personal_info),
    path('update_password', views.update_password),
]
