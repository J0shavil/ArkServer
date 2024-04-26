from django.db import models

# Create your models here.

class Server(models.Model):
    server_name = models.CharField(max_length=64)
    map_name = models.CharField(max_legth=64)
    server_password_hash = models.CharField(max_length=128)
    

