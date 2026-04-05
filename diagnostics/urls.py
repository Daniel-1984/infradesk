from django.urls import path
from . import views

app_name = 'diagnostics'

urlpatterns = [
    path('ticket/<int:ticket_pk>/', views.diagnostic_panel, name='panel'),
    path('ticket/<int:ticket_pk>/regenerate/', views.regenerate_diagnostic, name='regenerate'),
    path('alerts/', views.recurrence_alerts, name='alerts'),
]
