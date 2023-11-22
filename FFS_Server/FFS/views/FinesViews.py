from django.shortcuts import render
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from ..serializers import FinesSerializer, BreachesSerializer, ConfOfFinesSerializer
from ..models import *
from rest_framework.decorators import api_view
from ..filters import *
from .GetUser import *
from ..minio.minioClass import *
from datetime import datetime

from ..permissions import *
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.views import APIView
from rest_framework.permissions import *
from FFS_Server.settings import REDIS_HOST, REDIS_PORT
from drf_yasg.utils import swagger_auto_schema # type: ignore
import redis # type: ignore
session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


# Create your views here.

def getFineWithImage(serializer: FinesSerializer):
    minio = MinioClass()
    FineData = serializer.data
    FineData.update({'image': minio.getImage('fines', serializer.data['title'])})
    return FineData

def postFineImage(serializer: FinesSerializer):
    minio = MinioClass()
    minio.addImage('fines', serializer.data['title'], serializer.data['picture_url'])

def putFineImage(serializer: FinesSerializer, old_title):
    minio = MinioClass()
    minio.removeImage('fines', old_title)
    minio.addImage('fines', serializer.data['title'], serializer.data['picture_url'])


class Fines_View(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    # получение списка продуктов
    # можно всем
    def get(self, request, format=None):
        """
        Возвращает список штрафов
        """
        try:
            ssid = request.COOKIES["session_id"]
        except:
            return Response(status=status.HTTP_403_FORBIDDEN)

        userId = Users.objects.get(Userlogin=session_storage.get(ssid).decode('utf-8')).user_id
        TrueBreach = Breaches.objects.filter(user_id = userId).filter(breach_status = 'черновик') 
        if TrueBreach.exists():
            BreachId = TrueBreach[0].breach_id
        else:
            BreachId = 'null'
        List = {
            'breach_id': BreachId
        }
        FinesList = FinesFilter(Fines.objects.filter(fine_status='действует'),request)
        FinesListData = [getFineWithImage(FinesSerializer(fine)) for fine in FinesList]
        List['fines'] = FinesListData
        return Response(List)
    
    
    # добавление штрафа
    # можно только если авторизован и модератор
    @method_permission_classes((IsModerator,))
    @swagger_auto_schema(request_body=FinesSerializer)
    def post(self, request, format=None):
        """
        Добавляет новый штраф
        """
        Fine = Fines.objects.filter(title=request.data['title'])
        if Fine.exists():
            return Response('Такой штраф уже существует', status=status.HTTP_400_BAD_REQUEST)

        serializer = FinesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            postFineImage(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class Fine_View(APIView):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    # получение штрафа
    # можно всем
    def get(self, request, pk, format=None):
        """
        Возвращает один штраф
        """
        Fine = get_object_or_404(Fines, fine_id=pk)
        serializer = FinesSerializer(Fine)
        return Response(getFineWithImage(serializer), status=status.HTTP_202_ACCEPTED)     
    
    # изменение штрафа
    # можно только если авторизован и модератор
    @method_permission_classes((IsModerator,))
    @swagger_auto_schema(request_body=FinesSerializer)
    def put(self, request, pk, format=None):
        """
        Обновляет информацию о штрафе
        """
        if request.data.get('fine_status'):
                return Response(status=status.HTTP_400_BAD_REQUEST)
        
        Fine = get_object_or_404(Fines, fine_id=pk)
        old_title = Fine.title
        
        serializer = FinesSerializer(Fine, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            putFineImage(serializer, old_title)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # логическое удаление штрафа
    # можно только если авторизован и модератор
    @method_permission_classes((IsModerator,))
    def delete(self, request, pk, format=None):
        """
        Удаляет штраф
        """    
        Fine = get_object_or_404(Fines, fine_id=pk)
        Fine.fine_status = 'удалён'
        Fine.save()
        serializer = FinesSerializer(Fine)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    # добавление продукта в заказ
    # можно только если авторизован
    def post(self, request, pk, format=None):
        """
        Добавляет штраф в нарушение
        """ 
        try:
            ssid = request.COOKIES["session_id"]
        except:
            return Response(status=status.HTTP_403_FORBIDDEN)

        userId = Users.objects.get(Userlogin=session_storage.get(ssid).decode('utf-8')).user_id
        TrueBreach = Breaches.objects.filter(user_id = userId).filter(breach_status = 'черновик') 
        if not TrueBreach.exists():
            Breach = {
                'user': userId,
                'moder_id': 2,
                'created_date': datetime.now(),
            }
            BreachSerializer = BreachesSerializer(data=Breach)
            if not BreachSerializer.is_valid():
                return Response(BreachSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
            BreachSerializer.save()
    

        TrueBreach2 = Breaches.objects.filter(user_id = userId).filter(breach_status = 'черновик') 
        BreachId = TrueBreach2[0].breach_id
        if Breaches.objects.get(breach_id=BreachId).breach_status != 'черновик' or ConfOfFines.objects.filter(fine=pk).filter(breach=BreachId).exists():
            return Response({'error': 'Этот штраф уже добавлен'}, status=status.HTTP_400_BAD_REQUEST)
        
        New_COF = {
            'fine': pk,
            'breach': BreachId,
            'fine_desc': 'Описание:',
        }
        serializer = ConfOfFinesSerializer(data=New_COF)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

