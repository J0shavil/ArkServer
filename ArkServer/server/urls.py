from django.contrib import admin
from django.urls import path, include
from .views import StartArkServer


urlpatterns = [
    path('admin/', admin.site.urls),
    path('start_ark_server', StartArkServer.as_view(), name="start_ark_server"),
       
]