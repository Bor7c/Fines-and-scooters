from django.shortcuts import render
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from ..serializers import *
from ..models import *
from rest_framework.decorators import api_view
from ..filters import *
from datetime import datetime
# Create your views here.

from FFS_Server.permissions import *
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.views import APIView
from rest_framework.permissions import *
from FFS_Server.settings import REDIS_HOST, REDIS_PORT
from drf_yasg.utils import swagger_auto_schema # type: ignore
import redis # type: ignore
session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


class CoF_View(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    # изменение описания штрафа
    # можно только если авторизован
    @swagger_auto_schema(request_body=ConfOfFinesSerializer)
    def put(self, request, fine, format=None):
        try:
            ssid = request.COOKIES["session_id"]
        except:
            return Response(status=status.HTTP_403_FORBIDDEN)

        
        userId = Users.objects.get(Userlogin=session_storage.get(ssid).decode('utf-8')).user_id
        
        TrueBreach = Breaches.objects.filter(user=userId, breach_status='черновик')
        if TrueBreach.exists():
            BreachId = TrueBreach[0].breach_id
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        cof = ConfOfFines.objects.filter(fine=fine).filter(breach=BreachId)
        
        if len(cof) > 0:
            cof[0].fine_desc =request.data['fine_desc']
            cof[0].save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # удаление штрафа из нарушения
    # можно только если авторизован
    @swagger_auto_schema(request_body=ConfOfFinesSerializer)
    def delete(self, request, fine, format=None):
        try:
            ssid = request.COOKIES["session_id"]
        except:
            return Response(status=status.HTTP_403_FORBIDDEN)

        
        userId = Users.objects.get(Userlogin=session_storage.get(ssid).decode('utf-8')).user_id
        
        TrueBreach = Breaches.objects.filter(user=userId, breach_status='черновик')
        if TrueBreach.exists():
            BreachId = TrueBreach[0].breach_id
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        cof = ConfOfFines.objects.filter(fine=fine).filter(breach=BreachId)

        if len(cof) > 0:
            cof[0].delete()
            if len(ConfOfFines.objects.filter(breach=BreachId)) == 0:
                Breaches.objects.get(breach_id=BreachId).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

