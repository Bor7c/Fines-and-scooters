from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


class Breaches(models.Model):
    breach_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    closed_date = models.DateTimeField(blank=True, null=True)
    created_date = models.DateTimeField(blank=True, null=True)
    formated_date = models.DateTimeField(blank=True, null=True)
    breach_status = models.CharField(max_length=20, default='черновик')  # This field type is a guess.
    moder_id = models.IntegerField(blank=True, null=True)
    


class Fines(models.Model):
    fine_id = models.AutoField(primary_key=True)
    picture_url = models.CharField(blank=True, null=True)
    title = models.CharField(blank=True, null=True, max_length=70, unique=True)
    price = models.CharField(blank=True, null=True)
    text = models.CharField(blank=True, null=True)
    fine_status = models.CharField(default='действует', max_length=15)  # This field type is a guess.

class ConfOfFines(models.Model):
    cofid = models.BigAutoField(primary_key=True)
    fine = models.ForeignKey('Fines', models.DO_NOTHING)
    breach = models.ForeignKey('Breaches', models.DO_NOTHING)
    fine_desc = models.CharField(blank=True, null=True, max_length=400)

    class Meta:
        unique_together = (('fine', 'breach'),)

class Users(AbstractBaseUser):
    
    user_id = models.AutoField(primary_key=True)
    login = models.CharField(max_length=255, unique=True, verbose_name="Логин")
    password = models.CharField(max_length=255, verbose_name="Пароль")
    contacts = models.CharField(blank=True, null=True)
    admin_pass = models.BooleanField(blank=True, null=True, default=False)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    is_staff = models.BooleanField(default=False, verbose_name="Является ли пользователь менеджером?")
    is_superuser = models.BooleanField(default=False, verbose_name="Является ли пользователь админом?")

    def str(self):
        return self.username
    

