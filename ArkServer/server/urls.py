from django.contrib import admin
from django.urls import path, include
from .views import StartArkServer, createserverstartup_bat, custom_login, register
from .views import get_csrf_token


urlpatterns = [
    path('admin/', admin.site.urls),
    path('start_ark_server', StartArkServer.as_view(), name="start_ark_server"),
    path('createbat', createserverstartup_bat, name="createbat"),
    path('get_csrf_token/', get_csrf_token, name='get_csrf_token'),
    path('login', custom_login, name='login'),
    path('register', register, name='register'),
       
]