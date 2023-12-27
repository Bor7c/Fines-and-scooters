from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from datetime import datetime
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password="1234", **extra_fields):
        extra_fields.setdefault('username', username)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password="1234", **extra_fields):
        extra_fields.setdefault('is_moderator', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(unique=True)
    is_moderator = models.BooleanField(default=False)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Breaches(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершён'),
        (4, 'Отменён'),
        (5, 'Удалён'),
    )

    user = models.ForeignKey(CustomUser, models.CASCADE, blank=True, null=True)
    created_date = models.DateTimeField(default=datetime.now(tz=timezone.utc), blank=True, null=True)
    formated_date = models.DateTimeField(blank=True, null=True)
    closed_date = models.DateTimeField(blank=True, null=True)
    name = models.CharField(blank=True, null=True, max_length=70)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")

    def __str__(self):
        return "Нарушение №" + str(self.pk)

    class Meta:
        verbose_name = "Нарушение"
        verbose_name_plural = "Нарушения"


class Fines(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    image = models.ImageField(default="null", blank=True, null=True)
    title = models.CharField(blank=True, null=True, max_length=70)
    price = models.CharField(blank=True, null=True)
    text = models.CharField(blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Штраф"
        verbose_name_plural = "Штрафы"


class ConfOfFines(models.Model):
    fine = models.ForeignKey(Fines, models.CASCADE, null=True)
    breach = models.ForeignKey(Breaches, models.CASCADE, null=True)
    fine_desc = models.CharField(blank=True, null=True, max_length=400)

    class Meta:
        unique_together = (('fine', 'breach'),)
        verbose_name = "Штраф-нарушение"
        verbose_name_plural = "Штрафы-нарушение"


    

