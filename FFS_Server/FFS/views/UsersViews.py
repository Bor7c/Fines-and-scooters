from django.contrib.auth import authenticate, logout
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from drf_yasg.utils import swagger_auto_schema

from datetime import timedelta

import uuid

from ..serializers import *
from rest_framework.decorators import api_view
from FFS_Server.permissions import *
from ..utils import get_session

session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


@api_view(['Post'])
@permission_classes([IsAuthenticated])
def check(request):
    session_id = request.headers.get("authorization")

    if session_storage.get(session_id):
        user = CustomUser.objects.get(username=session_storage.get(session_id).decode('utf-8'))

        serializer = UserSerializer(user, many=False)
        # print(serializer.data)

        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_403_FORBIDDEN)


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(['Post'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data["username"]
    password = request.data["password"]
    user = authenticate(request, username=username, password=password)

    if user is not None:
        random_key = str(uuid.uuid4())
        session_storage.set(random_key, username)

        data = {
            "session_id": random_key,
            "user_id": user.pk,
            "username": user.username,
            "is_moderator": user.is_moderator
        }

        response = Response(data, status=status.HTTP_201_CREATED)
        response.set_cookie("session_id", random_key, httponly=False, expires=timedelta(days=1))

        return response
    else:
        return HttpResponse(status=status.HTTP_403_FORBIDDEN)


@swagger_auto_schema(method='post')
@api_view(['Post'])
@permission_classes([AllowAny])
def logout_view(request):
    ssid = get_session(request)

    if ssid is None:
        return Response(status=status.HTTP_403_FORBIDDEN)

    session_storage.delete(ssid)

    logout(request._request)
    response = HttpResponse(status=status.HTTP_200_OK)
    response.delete_cookie("session_id")
    return response