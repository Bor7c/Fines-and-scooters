from .models import *
from rest_framework import serializers


class FinesSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Fines
        # Поля, которые мы сериализуем
        fields = ["fine_id", "picture", "title", "price", "text", "fine_status"]

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

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Users
        # Поля, которые мы сериализуем
        fields = ["user_id", "name", "login", "password", "contacts", "admin_pass"] 

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfOfFines
        fields = ["fine_desc","fine"]
