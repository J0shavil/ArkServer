from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('download_steamcmd', views.download_steamcmd, name="download_steamcmd"),
    path('run_steamcmd', views.run_steamcmd, name="run_steamcmd"),    
]