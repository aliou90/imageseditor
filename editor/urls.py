# urls.py
from django.urls import path
from . import views
from .views import process_images
from django.conf import settings
from django.conf.urls.static import static
from .views import feedback_view
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.index, name='index'),
    path('upload-image/', views.upload_image, name='upload_image'),
    path('process-images/', process_images, name='process_images'),
    path('feedback/', feedback_view, name='feedback'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
