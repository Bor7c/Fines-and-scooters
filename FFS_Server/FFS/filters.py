def FinesFilter(objects, request):
    if request.query_params.get('title'):
        return objects.filter(title__icontains=request.query_params.get('title'))
    return objects
    

def DateFilter(objects, request):
    lowerdate = "2020-01-01"
    hierdate = "2500-01-01"
    if request.query_params.get('downdate'):
        lowerdate = request.query_params.get('downdate')
    if request.query_params.get('update'):
        hierdate = request.query_params.get('update')
    return objects.filter(created_date__range=[lowerdate, hierdate])

def StatusFilter(objects, request):
    if request.query_params.get('status'):
        return objects.filter(breach_status=request.query_params.get('status'))
    return objects


def BreachesFilter(objects, request):
    return DateFilter(StatusFilter(objects,request),request)