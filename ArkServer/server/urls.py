from django.contrib import admin
from django.urls import path, include
from .views import StartArkServer, run_steamcmd, download_steamcmd


urlpatterns = [
    path('admin/', admin.site.urls),
    path('start_ark_server', StartArkServer.as_view(), name="start_ark_server"),
    path('run_steamcmd', run_steamcmd, name="run_steamcmd"),
    path('download_steamcmd', download_steamcmd, name="download_steamcmd"),
       
]