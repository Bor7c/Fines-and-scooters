from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from django.utils.dateparse import parse_date
from django.utils.timezone import make_aware
from rest_framework.response import Response
from rest_framework import status
from ..serializers import *
from ..models import *
from django.db.models import Q


from FFS_Server.permissions import *
from rest_framework.decorators import permission_classes, api_view
from FFS_Server.settings import REDIS_HOST, REDIS_PORT, MY_PASSWORD
import redis
import requests

from ..utils import get_session

session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_breaches(request):
    session_id = get_session(request)
    user = get_object_or_404(CustomUser, username=session_storage.get(session_id).decode('utf-8'))

    statuses = [2, 3, 4]
    if user.is_moderator == True:
        breaches = Breaches.objects.filter(status__in=statuses)
    else: 
        breaches = Breaches.objects.filter(Q(user_id=user.pk) & Q(status__in=statuses))

    # Get parameters for date range and status from the request
    start_date = request.query_params.get('start_date', None)
    end_date = request.query_params.get('end_date', None)
    status = request.query_params.get('status', None)
    

    # if user.is_moderator == True:
    #         FilterUser = request.query_params.get('user', None)

    #         filter_user_ids = CustomUser.objects.filter(username__icontains=FilterUser).values_list('id', flat=True)  # Получаем список идентификаторов пользователей
    #         breaches = breaches.filter(user__id__in=filter_user_ids)

                

     # Parse start_date and end_date and filter the query if they are provided
    if start_date:
        breaches = breaches.filter(formated_date__gte=start_date)

    if end_date:
            breaches = breaches.filter(formated_date__lte=end_date)

    # If status parameter is provided, filter by the status
    if status:
        try:
            status_num = int(status)
            if status_num in dict(Breaches.STATUS_CHOICES).keys():
                breaches = breaches.filter(status=status_num)
        except ValueError:
            pass  # or you could return an error message that status must be an integer


    print(start_date)

    # Serialize and return response
    serializer = BreachesSerializer(breaches, many=True)
    # print(serializer.data)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_breach(request, breach_id):
    breach = Breaches.objects.get(pk=breach_id)

    if breach is None:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = BreachesSerializer(breach, many=False)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_fine_from_breach(request, breach_id, fine_id):
    if not ConfOfFines.objects.filter(breach_id=breach_id, fine_id=fine_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    conf = ConfOfFines.objects.get(breach_id=breach_id, fine_id=fine_id)
    conf.delete()

    breach = Breaches.objects.get(pk=breach_id)
    serializer = BreachesSerializer(breach, many=False)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_breach(request, breach_id):
    if not Breaches.objects.filter(pk=breach_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    for conf in ConfOfFines.objects.filter(breach_id=breach_id):
        conf.delete()

    breach = Breaches.objects.get(pk=breach_id)
    breach.delete()

    return Response(status=status.HTTP_200_OK)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_breach_status_user(request):
    breach = find_draft_breach(request)
    breach.status = 2

    # Сервис
    url = "http://localhost:5000/name/"
    params = {"breach_id": breach.pk}
    response = requests.post(url, json=params)
    print(response.status_code)

    breach.formated_date = datetime.now(tz=timezone.utc)
    breach.save()
    serializer = BreachesSerializer(breach, many=False)

    return Response(status=status.HTTP_200_OK)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_breach_status_admin(request, breach_id):
    session_id = get_session(request)
    user = get_object_or_404(CustomUser, username=session_storage.get(session_id).decode('utf-8'))
    print(user)
    print(request.data)

    if not user.is_moderator == True:
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    Breach = Breaches.objects.get(pk=breach_id)
    Breach.status = request.data['status']
    Breach.closed_date = datetime.now()
    Breach.save()
    serializer = BreachesSerializer(Breach)
    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)



@api_view(["PUT"])
def update_breach_name(request, breach_id):
    name = request.data["name"]
    password = request.data["password"]
    if password != MY_PASSWORD:
        return Response(status=status.HTTP_403_FORBIDDEN)
    try:
        Breach = Breaches.objects.get(pk=breach_id)
        Breach.name = name
        Breach.save()
        return Response(status=status.HTTP_200_OK)
    except Breaches.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)





def find_draft_breach(request):
    session_id = get_session(request)
    if session_id is None:
        return None
    
    if session_id not in session_storage:
        return None

    user = CustomUser.objects.get(username=session_storage.get(session_id).decode('utf-8'))

    breach = Breaches.objects.filter(user_id=user.pk).filter(status=1).first()

    if breach is None:
        return None

    return breach