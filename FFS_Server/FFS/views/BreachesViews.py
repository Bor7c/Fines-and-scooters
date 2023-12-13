from rest_framework.response import Response
from rest_framework import status
from ..serializers import *
from ..models import *


from FFS_Server.permissions import *
from rest_framework.decorators import permission_classes, api_view
from FFS_Server.settings import REDIS_HOST, REDIS_PORT
import redis

from ..utils import get_session

session_storage = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_breaches(request):
    session_id = get_session(request)

    user = CustomUser.objects.get(username=session_storage.get(session_id).decode('utf-8'))

    breaches = Breaches.objects.filter(user_id=user.pk)

    serializer = BreachesSerializer(breaches, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_draft_breach(request):
    draft_breach = find_draft_breach(request)

    if draft_breach is None:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = BreachesSerializer(draft_breach, many=False)

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
def update_breach_status_user(request, breach_id):
    if not Breaches.objects.filter(pk=breach_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    breach = Breaches.objects.get(pk=breach_id)
    breach.status = 2
    breach.formated_date = datetime.now(tz=timezone.utc)
    breach.save()

    return Response(status=status.HTTP_200_OK)


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