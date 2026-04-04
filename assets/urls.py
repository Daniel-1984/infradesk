from django.urls import path
from . import views

app_name = 'assets'

urlpatterns = [
    path('', views.asset_list, name='list'),
    path('novo/', views.asset_create, name='create'),
    path('<int:pk>/', views.asset_detail, name='detail'),
    path('<int:pk>/editar/', views.asset_edit, name='edit'),
]
