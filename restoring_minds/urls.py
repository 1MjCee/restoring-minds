from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('dashboard/', admin.site.urls),
    path('scripts/', include("crewai_agents.urls")),
]


admin.autodiscover()

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
