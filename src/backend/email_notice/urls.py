from django.urls import path
from . import views

app_name = 'email_notice'

urlpatterns = [
    path('api/notification-settings/', views.notification_settings, name='notification_settings'),
    path('api/toggle-email-status/', views.toggle_email_status, name='toggle_email_status'),
]
