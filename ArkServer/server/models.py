from django.db import models

# Create your models here.

class Server(models.Model):
    server_session_name = models.CharField(max_length=64)
    map_name = models.CharField(max_length=64)
    server_password_hash = models.CharField(max_length=128, null=True)
    server_password_salt = models.CharField(max_length=128,null=True)
    admin_password_hash = models.CharField(max_length=128, null=True)
    admin_password_salt = models.CharField(max_length=128, null=True)
    max_server_players = models.IntegerField(default=70, null=True)



