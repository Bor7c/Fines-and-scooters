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
# Create your views here.
@api_view(['Put','Delete'])
def Change_Fine(request, fine, format=None):
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

    
    if request.method == 'DELETE':
        if len(cof) > 0:
            cof[0].delete()
            if len(ConfOfFines.objects.filter(breach=BreachId)) == 0:
                Breaches.objects.get(breach_id=BreachId).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'PUT':
        if len(cof) > 0:
            cof[0].fine_desc = request.data['desc']
            cof[0].save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)