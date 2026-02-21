from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/profile/', TemplateView.as_view(template_name='home.html')),
    path('accounts/register/', TemplateView.as_view(template_name='registration/register.html'), name='register'),
    path('news/', include('app_news.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)