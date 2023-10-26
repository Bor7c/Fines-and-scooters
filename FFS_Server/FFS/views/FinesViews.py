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


# Create your views here.

def getFineWithImage(serializer: FinesSerializer):
    minio = MinioClass()
    FineData = serializer.data
    FineData.update({'image': minio.getImage('fines', serializer.data['title'])})
    return FineData

def postFineImage(request, serializer: FinesSerializer):
    minio = MinioClass()
    minio.addImage('fines', request.data['title'], serializer.data['picture_url'])

def putFineImage(request, serializer: FinesSerializer):
    minio = MinioClass()
    minio.removeImage('fines', serializer.data['title'])
    minio.addImage('fines', serializer.data['title'], request.data['title'], serializer.data['picture_url'])




@api_view(['Get','Post'])
def fines_action(request, format=None):
    if request.method == 'GET':
        """
        Возвращает список штрафов
        """
        userId = GetUser()
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
    
    elif request.method == 'POST':
        """
        Добавляет новый штраф
        """
        print('post')
        serializer = FinesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            postFineImage(request, serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['Get','Delete','Post'])
def fine_action(request, pk, format=None):
    if request.method == 'GET':
        """
        Возвращает один штраф
        """
        Fine = get_object_or_404(Fines, fine_id=pk)
        serializer = FinesSerializer(Fine)
        return Response(getFineWithImage(serializer), status=status.HTTP_202_ACCEPTED)     

    elif request.method == 'DELETE':
        """
        Удаляет штраф
        """    
        Fine = get_object_or_404(Fines, fine_id=pk)
        Fine.fine_status = 'удалён'
        Fine.save()
        serializer = FinesSerializer(Fine)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    elif request.method == 'POST':
        """
        Добавляет штраф в нарушение
        """ 
        userId = GetUser()
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
