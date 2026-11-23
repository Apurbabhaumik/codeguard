from django.contrib import admin
from django.urls import path, include

from core_views import dashboard, landing

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('assignments/', include('assignments.urls')),
    path('submissions/', include('submissions.urls')),
    path('', landing, name='landing'),
    path('dashboard/', dashboard, name='dashboard'),
]
