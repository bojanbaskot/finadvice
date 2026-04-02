from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('apps.core.urls', namespace='core')),
    path('vijesti/', include('apps.news.urls', namespace='news')),
    path('edukacija/', include('apps.elearning.urls', namespace='elearning')),
    path('kalkulatori/', include('apps.calculators.urls', namespace='calculators')),
    path('analize/', include('apps.analysis.urls', namespace='analysis')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
