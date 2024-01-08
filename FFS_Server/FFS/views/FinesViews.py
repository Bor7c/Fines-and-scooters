from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response

from .BreachesViews import find_draft_breach
from ..serializers import *
from ..models import *

from FFS_Server.permissions import *
from FFS_Server.settings import REDIS_HOST, REDIS_PORT
import redis

from ..utils import get_session

session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


@api_view(["GET"])
def fines(request):
    query = request.GET.get("title", "")
    fines = Fines.objects.filter(title__icontains=query)
    draft_breach = find_draft_breach(request)

    data = {
        "breach_id": draft_breach.id if draft_breach else None,
        "fines": FinesSerializer(fines, many=True).data
    }

    return Response(data)


@api_view(["GET"])
def search_fines(request):
    query = request.GET.get("title", "")
    fines = Fines.objects.filter(title__icontains=query, status=1)
    draft_breach = find_draft_breach(request)

    data = {
        "breach_id": draft_breach.id if draft_breach else None,
        "fines": FinesSerializer(fines, many=True).data
    }

    return Response(data)


@api_view(["GET"])
def get_fine(request, fine_id):
    fine = Fines.objects.get(pk=fine_id)
    serializer = FinesSerializer(fine, many=False)

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def edit_fine(request, fine_id):
    print(request.data)
    session_id = get_session(request)
    if session_id is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    user = CustomUser.objects.get(username=session_storage.get(session_id).decode('utf-8'))
    if not user.is_moderator:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    fine = Fines.objects.get(pk=fine_id)

    fields = request.data.keys()
    if 'pk' in fields:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer = FinesSerializer(fine, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def add_fine(request):
    print(request.data)
    session_id = get_session(request)
    if session_id is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    user = CustomUser.objects.get(username=session_storage.get(session_id).decode('utf-8'))    
    if not user.is_moderator:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    fields = request.data.keys()
    if 'pk' in fields:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    serializer = FinesSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_fine_to_breach(request, fine_id):
    session_id = get_session(request)
    user = CustomUser.objects.get(username=session_storage.get(session_id).decode('utf-8'))

    draft_breach = find_draft_breach(request)

    if draft_breach is None:
        draft_breach = Breaches.objects.create()
        draft_breach.user = user
        draft_breach.save()

    if ConfOfFines.objects.filter(breach_id=draft_breach.pk, fine_id=fine_id):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    cons = ConfOfFines.objects.create()
    cons.breach = draft_breach
    cons.fine = Fines.objects.get(pk=fine_id)
    cons.save()


    serializer = BreachesSerializer(draft_breach, many=False)

    return Response(serializer.data, status=status.HTTP_200_OK)
