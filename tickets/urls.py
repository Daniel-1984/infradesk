from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('', views.ticket_list, name='list'),
    path('novo/', views.ticket_create, name='create'),
    path('exportar/', views.ticket_export_csv, name='export_csv'),
    path('notificacoes/', views.ticket_notifications, name='notifications'),
    path('<int:pk>/', views.ticket_detail, name='detail'),
    path('<int:pk>/encerrar/', views.ticket_close, name='close'),
]
