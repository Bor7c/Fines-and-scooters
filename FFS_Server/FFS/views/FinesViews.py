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
def search_fines(request):
    query = request.GET.get("title", "")
    fines = Fines.objects.filter(title__icontains=query)
    draft_breach = find_draft_breach(request)

    data = {
        "breach": BreachesSerializer(draft_breach, many=False).data,
        "fines": FinesSerializer(fines, many=True).data
    }

    return Response(data)


@api_view(["GET"])
def get_fine(request, fine_id):
    fine = Fines.objects.get(pk=fine_id)
    serializer = FinesSerializer(fine, many=False)

    return Response(serializer.data)


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
