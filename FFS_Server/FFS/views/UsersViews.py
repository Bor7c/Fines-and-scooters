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

from datetime import timedelta 


import uuid
from FFS_Server.settings import REDIS_HOST, REDIS_PORT

import redis # type: ignore
session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)

from ..serializers import *
from ..models import *
from rest_framework.decorators import api_view
from ..filters import *
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



@api_view(['Post'])
@permission_classes([AllowAny])
def check(request):
    session_id = request.headers.get("authorization")
    print(session_id)

    print(session_storage.get(session_id))

    if (session_storage.get(session_id)):
        user = Users.objects.get(Userlogin=session_storage.get(session_id).decode('utf-8'))
        
        serializer = UserSerializer(user, many=False)
        print(serializer.data)

        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_403_FORBIDDEN)


@swagger_auto_schema(method='post', request_body=UserSerializer)
@api_view(['Post'])
@permission_classes([AllowAny])
def login_view(request):
    print(request.data)
    Userlogin = request.data["userlogin"]
    password = request.data["password"]
    user = authenticate(request, Userlogin=Userlogin, password=password)
    if user is not None:
        random_key = str(uuid.uuid4())
        session_storage.set(random_key, Userlogin)

        print(user.last_login)
        print(user.get_username())

        data = {
            "session_id": random_key,
            "user_id": user.pk,
            "UserLogin": user.Userlogin,
            "admin_pass": user.admin_pass
        }

        response = Response(data, status=status.HTTP_201_CREATED)
        response.set_cookie("session_id", random_key, httponly=False, expires=timedelta(days=1))


        return response
    else:
        return HttpResponse("{'status': 'error', 'error': 'login failed'}")



@csrf_exempt
@swagger_auto_schema(method='post')
@api_view(['Post'])
@permission_classes([AllowAny])
def logout_view(request):
    try:
       ssid = request.headers.get("authorization")
       print(ssid)
    except:
        return HttpResponse("{'status': 'error', 'error': 'logout failed'}")
        
    session_storage.delete(ssid)

    logout(request._request)
    response = HttpResponse("{'status': 'success'}")
    response.delete_cookie("session_id")
    return response