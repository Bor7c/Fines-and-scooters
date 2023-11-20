from .models import *
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from collections import OrderedDict


class FinesSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Fines
        # Поля, которые мы сериализуем
        fields = ["fine_id", "picture_url", "title", "price", "text", "fine_status"]

class FinesInBreachSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Fines
        # Поля, которые мы сериализуем
        fields = ["title", "price", "text"]        

class BreachesSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Breaches
        # Поля, которые мы сериализуем
        fields = ["breach_id", "user", "closed_date","created_date", "formated_date","breach_status","moder_id"]        

class ConfOfFinesSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = ConfOfFines
        # Поля, которые мы сериализуем
        fields = ["cofid", "fine", "breach", "fine_desc"]   


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfOfFines
        fields = ["fine_desc","fine"]




class UserSerializer(ModelSerializer):
    admin_pass = serializers.BooleanField(default=False, required=False)
    is_staff = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = Users
        fields = ["user_id", "login", "password", "admin_pass", "is_staff", "is_superuser"]