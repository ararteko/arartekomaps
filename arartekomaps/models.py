from django.db import models

class OldUser(models.Model):
    username = models.CharField(max_length=230)
    first_name = models.CharField(max_length=230)
    last_name = models.CharField(max_length=230)
    email = models.CharField(max_length=230)
    password = models.CharField(max_length=230)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()

    class Meta:
        db_table ='auth_user'