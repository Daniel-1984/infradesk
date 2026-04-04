from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

admin.site.site_header = 'InfraDesk — Administração'
admin.site.site_title = 'InfraDesk Admin'
admin.site.index_title = 'Painel de Controle'

urlpatterns = [
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('tickets/', include('tickets.urls')),
    path('assets/', include('assets.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
