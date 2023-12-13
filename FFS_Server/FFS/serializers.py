from .models import *
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'is_moderator')


class FinesSerializer(serializers.ModelSerializer):
    class Meta:
        # Модель, которую мы сериализуем
        model = Fines
        # Поля, которые мы сериализуем
        fields = '__all__'


class BreachesSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, many=False)
    fines = serializers.SerializerMethodField()

    def get_fines(self, breach):
        confs = ConfOfFines.objects.filter(breach=breach)
        return FinesSerializer([conf.fine for conf in confs], many=True).data

    class Meta:
        # Модель, которую мы сериализуем
        model = Breaches
        # Поля, которые мы сериализуем
        fields = '__all__'


class ConfOfFinesSerializer(serializers.ModelSerializer):
    fine = FinesSerializer(read_only=True, many=False)
    breach = BreachesSerializer(read_only=True, many=False)

    class Meta:
        # Модель, которую мы сериализуем
        model = ConfOfFines
        # Поля, которые мы сериализуем
        fields = '__all__'


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)