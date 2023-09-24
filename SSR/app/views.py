from django.shortcuts import render
from . import models

def GetOrders(request):
    try:
        input_text = request.GET['text']
        if input_text:
            current_orders = [order for order in models.Fines.objects.all() if input_text.lower() in order.title.lower() or input_text.lower() in order.price.lower()]
            return render(request, 'orders.html', {'data' : {
                'orders': current_orders,
                'search_v': input_text,
            }})
    except:
        return render(request, 'orders.html', {'data' : {
                'orders': models.Fines.objects.all(),   
            }})

def GetOrder(request, id):
    return render(request, 'order.html', {'data' : {
        
        'id': id,
        'order':models.Fines.objects.filter(fine_id=id).first(),
    }})