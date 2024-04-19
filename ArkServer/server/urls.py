from django.contrib import admin
from django.urls import path, include
from .views import start_server, test


urlpatterns = [
    path('admin/', admin.site.urls),
    path('start_server', start_server, name="start_server"),
    path('test', test, name="test"),
       
]