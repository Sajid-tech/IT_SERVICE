"""
URL configuration for it_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static 
from django.conf import settings
from service import views as service_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', service_views.index, name='index'),
    path('home/',service_views.home, name="home"),
    path('register/', service_views.register, name='register'),
    path('otp_verification/', service_views.otp_verification, name='otp_verification'),
    path('login/', include('django.contrib.auth.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('create_service/', service_views.create_service, name='create_service'),
    path('service/<int:id>/toggle/', service_views.toggle_active, name='toggle_active'),
    path('service/<int:service_id>/edit/', service_views.edit_service, name='edit_service'),
    path('service/<int:service_id>/delete/', service_views.delete_service, name='delete_service'),
    path('subscribe/<int:service_id>/', service_views.subscribe, name='subscribe'),
    path('payment/<str:payment_id>/', service_views.payment_page, name='payment_page'),
    path('payment_callback/', service_views.payment_callback, name='payment_callback'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

