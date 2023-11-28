from django.shortcuts import render
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from ..serializers import *
from ..models import *
from rest_framework.decorators import api_view
from ..filters import *
from datetime import datetime
from .GetUser import *
from ..minio.minioClass import *



from FFS_Server.permissions import *
from rest_framework.decorators import permission_classes, authentication_classes, api_view
from rest_framework.views import APIView
from rest_framework.permissions import *
from FFS_Server.settings import REDIS_HOST, REDIS_PORT
from drf_yasg.utils import swagger_auto_schema # type: ignore
import redis # type: ignore
session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)

# Create your views here.

def checkStatus(old, new, admin):
    return ((not admin) and (new in ['сформирован', 'удалён']) and (old == 'черновик')) or (admin and (new in ['завершён', 'отклонён']) and (old == 'сформирован')) 

def getFineWithImage(serializer: FinesSerializer, title: str):
    minio = MinioClass()
    FineData = serializer.data
    FineData.update({'image': minio.getImage('fines', title)})
    return FineData

def getFineForOneBreach(serializer: PositionSerializer):
    FinesList = []
    for fine in serializer.data:
        Fine = get_object_or_404(Fines, fine_id=fine['fine'])
        if Fine.fine_status == 'действует':
            FineData = fine
            FineData['Fine_data'] = getFineWithImage(FinesInBreachSerializer(Fine), Fine.title)
            FinesList.append(FineData)
    return FinesList


class Breaches_View(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    # получение списка заказов
    # можно только если авторизован
    def get(self, request, format=None):
        """
        Возвращает список нарушений
        """
        try:
            ssid = request.COOKIES["session_id"]
        except:
            return Response(status=status.HTTP_403_FORBIDDEN)

        User = Users.objects.get(Userlogin=session_storage.get(ssid).decode('utf-8'))
        

        if User.admin_pass:
            BreachesList = BreachesFilter(Breaches.objects.all(),request) 
        else:
            BreachesList = BreachesFilter(Breaches.objects.filter(user=User.user_id),request)

        BreachSerializer = BreachesSerializer(BreachesList, many=True)  
        WideBreach = BreachSerializer.data
        for i, wb in enumerate(BreachSerializer.data):
            User = get_object_or_404(Users, user_id=wb.get('user'))     
            WideBreach[i]['User_login'] = User.Userlogin                         
        return Response(WideBreach, status=status.HTTP_202_ACCEPTED)
        

        
        
        

    
    # отправка заказа пользователем
    # можно только если авторизован
    @swagger_auto_schema(request_body=BreachesSerializer)
    def put(self, request, format=None):
        """
        Формирует нарушение
        """
        try:
            ssid = request.COOKIES["session_id"]
        except:
            return Response(status=status.HTTP_403_FORBIDDEN)

        userId = Users.objects.get(Userlogin=session_storage.get(ssid).decode('utf-8')).user_id
        User = get_object_or_404(Users, user_id=userId)
        Breach = get_object_or_404(Breaches, user=userId, breach_status='черновик')
        new_status = "сформирован"
        if checkStatus(Breach.breach_status, new_status, False):
            Breach.breach_status = new_status
            Breach.formated_date = datetime.now()
            Breach.save()
            serializer = BreachesSerializer(Breach)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # удаление заказа пользователем
    # можно только если авторизован
    def delete(self, request, format=None):
        """
        Удаляет нарушение
        """
        try:
            ssid = request.COOKIES["session_id"]
        except:
            return Response(status=status.HTTP_403_FORBIDDEN)

        userId = Users.objects.get(Userlogin=session_storage.get(ssid).decode('utf-8')).user_id
        Breach = Breaches.objects.filter(user = userId).filter(breach_status = 'черновик') 
        if len(Breach) > 0:
            BreachId = Breach[0].breach_id
        CoF = ConfOfFines.objects.filter(breach=BreachId)
        if checkStatus(Breach[0].breach_status, "удалён", False):
            for true_CoF in CoF:
                true_CoF.delete()
            Breach.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)



class Breach_View(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    # получение нарушения
    # можно получить нарушение  если авторизован
    # если авторизован и модератор, то можно получить любой заказ
    def get(self, request, pk, format=None):
        """
        Возвращает одно нарушение
        """
        try:
            ssid = request.COOKIES["session_id"]
        except:
            return Response(status=status.HTTP_403_FORBIDDEN)

        User = Users.objects.get(Userlogin=session_storage.get(ssid).decode('utf-8'))
        
        BreachKeys = Breaches.objects.filter(user=User.user_id).values_list('breach_id', flat=True)
        if(pk in BreachKeys) or User.admin_pass:
            Breach = get_object_or_404(Breaches, breach_id=pk) 
            BreachSerializer = BreachesSerializer(Breach)

            positions = ConfOfFines.objects.filter(breach=pk)
            FineListSerializer = PositionSerializer(positions, many=True)

            WideBreach = BreachSerializer.data

            WideBreach['User_login'] = Users.objects.get(user_id=WideBreach['user']).Userlogin
            WideBreach['Fines_list'] = getFineForOneBreach(FineListSerializer)
            return Response(WideBreach, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    # перевод заказа модератором на статус
    # можно только если авторизован и модератор
    @method_permission_classes((IsModerator,))
    @swagger_auto_schema(request_body=BreachesSerializer)
    def put(self, request, pk, format=None):
        """
        Принимает или отклоняет нарушение
        """
        Breach = get_object_or_404(Breaches, breach_id=pk)
        try: 
            new_status = request.data['breach_status']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if checkStatus(Breach.breach_status, new_status, True):
            Breach.breach_status = new_status
            Breach.closed_date = datetime.now()
            Breach.save()
            serializer = BreachesSerializer(Breach)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response('Нарушение удалено',status=status.HTTP_400_BAD_REQUEST)

