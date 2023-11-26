from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from drf_yasg.utils import swagger_auto_schema # type: ignore


import uuid
from FFS_Server.settings import REDIS_HOST, REDIS_PORT

import redis # type: ignore
session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)

from ..serializers import *
from ..models import *
from rest_framework.decorators import api_view
from ..filters import *
from .GetUser import *
from FFS_Server.permissions import *



class UserViewSet(ModelViewSet):
    """Класс, описывающий методы работы с пользователями
    Осуществляет связь с таблицей пользователей в базе данных
    """
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    model_class = Users

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [AllowAny]
        elif self.action in ['list']:
            permission_classes = [IsAdmin | IsModerator]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

    def create(self, request):
        """
        Функция регистрации новых пользователей
        Если пользователя c указанным в request Userlogin ещё нет, в БД будет добавлен новый пользователь.
        """
        if self.model_class.objects.filter(Userlogin=request.data['Userlogin']).exists():
            return Response({'status': 'Exist'}, status=400)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            self.model_class.objects.create_user(Userlogin=serializer.data['Userlogin'],
                                     password=serializer.data['password'],
                                     is_superuser=serializer.data['is_superuser'],
                                     is_staff=serializer.data['is_staff'],
                                     admin_pass=serializer.data['admin_pass'])
            return Response({'status': 'Success'}, status=200)
        return Response({'status': 'Error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
@authentication_classes([])
@csrf_exempt
@swagger_auto_schema(method='post', request_body=UserSerializer)
@api_view(['Post'])
def login_view(request):
    Userlogin = request.data["Userlogin"]
    password = request.data["password"]
    user = authenticate(request, Userlogin=Userlogin, password=password)
    if user is not None:
        random_key = str(uuid.uuid4())
        session_storage.set(random_key, Userlogin)

        response = HttpResponse("{'status': 'ok'}")
        response.set_cookie("session_id", random_key)

        return response
    else:
        return HttpResponse("{'status': 'error', 'error': 'login failed'}")

@permission_classes([AllowAny])
@authentication_classes([])
@csrf_exempt
@swagger_auto_schema(method='post')
@api_view(['Post'])
def logout_view(request):
    try:
        ssid = request.COOKIES["session_id"]
    except:
        return HttpResponse("{'status': 'error', 'error': 'logout failed'}")
        
    session_storage.delete(ssid)

    logout(request._request)
    response = HttpResponse("{'status': 'success'}")
    response.delete_cookie("session_id")
    return response