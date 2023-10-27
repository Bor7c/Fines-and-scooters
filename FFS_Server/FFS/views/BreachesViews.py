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

# Create your views here.

def checkStatus(old, new, admin):
    return ((not admin) and (new in ['сформирован', 'удалён']) and (old == 'черновик')) or (admin and (new in ['завершён', 'отклонён']) and (old == 'сформирован')) 

def getFineWithImage(serializer: FinesSerializer, title: int):
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


@api_view(['Get','Put','Delete'])
def breaches_action(request, format=None):
    if request.method == 'GET':
        """
        Возвращает список нарушений
        """
        BreachesList = BreachesFilter(Breaches.objects.all(),request)
        BreachSerializer = BreachesSerializer(BreachesList, many=True)  

        WideBreach = BreachSerializer.data
        for i, wb in enumerate(BreachSerializer.data):
            User = get_object_or_404(Users, user_id=wb.get('user'))     
            WideBreach[i]['User_login'] = User.login                         
        return Response(WideBreach, status=status.HTTP_202_ACCEPTED)
    
    elif request.method == 'PUT':
        """
        Формирует нарушение
        """
        userId = GetUser()
        User = get_object_or_404(Users, user_id=userId)
        Breach = get_object_or_404(Breaches, user=userId, breach_status='черновик')
        new_status = "сформирован"
        if checkStatus(Breach.breach_status, new_status, User.admin_pass):
            Breach.breach_status = new_status
            Breach.formated_date = datetime.now()
            Breach.save()
            serializer = BreachesSerializer(Breach)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        """
        Удаляет нарушение
        """
        userId = GetUser()
        User = Users.objects.get(user_id=userId)
        Breach = Breaches.objects.filter(user = userId).filter(breach_status = 'черновик') 
        if len(Breach) > 0:
            BreachId = Breach[0].breach_id
        CoF = ConfOfFines.objects.filter(breach=BreachId)
        if checkStatus(Breach[0].breach_status, "удалён", User.admin_pass):
            for true_CoF in CoF:
                true_CoF.delete()
            Breach.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['Get','Put'])
def breach_action(request, pk, format=None):
    if request.method == 'GET':
        """
        Возвращает одно нарушение
        """
        Breach = get_object_or_404(Breaches, breach_id=pk)
        BreachSerializer = BreachesSerializer(Breach)

        positions = ConfOfFines.objects.filter(breach=pk)
        FineListSerializer = PositionSerializer(positions, many=True)

        WideBreach = BreachSerializer.data

        WideBreach['User_login'] = Users.objects.get(user_id=WideBreach['user']).login
        WideBreach['Fines_list'] = getFineForOneBreach(FineListSerializer)
        return Response(WideBreach, status=status.HTTP_202_ACCEPTED)
    
         
        
    

@api_view(['Put'])
def breach_final(request, pk, format=None):
        """
        Принимает или отклоняет нарушение
        """
        userId = 2
        User = get_object_or_404(Users, user_id=userId)
        Breach = get_object_or_404(Breaches, breach_id=pk)
        try: 
            new_status = request.data['breach_status']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if checkStatus(Breach.breach_status, new_status, User.admin_pass):
            Breach.breach_status = new_status
            Breach.closed_date = datetime.now()
            Breach.save()
            serializer = BreachesSerializer(Breach)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(status=status.HTTP_400_BAD_REQUEST)