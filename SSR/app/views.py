from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.db import connection
from . import models



def GetOrders(request):
    try:
        input_text = request.GET['text']
        if input_text:
            current_orders = [order for order in models.Fines.objects.filter(fine_status='действует') if input_text.lower() in order.title.lower() or input_text.lower() in order.price.lower()]
            return render(request, 'orders.html', {'data' : {
                'orders': current_orders,
                'search_v': input_text,
            }})
    except:
        return render(request, 'orders.html', {'data' : {
                'orders': models.Fines.objects.filter(fine_status='действует'),   
            }})

def GetOrder(request, id):
    return render(request, 'order.html', {'data' : {
        'id': id,
        'order':models.Fines.objects.filter(fine_id=id).first(),
    }})



def Click_on_HideCard(request, id):
    if not HideCard(id):
        pass
    return redirect(reverse('order_url'))


def HideCard(id):
    try:
        with connection.cursor() as cursor:
    
            quarry = f"UPDATE fines SET fine_status = 'удален' WHERE fine_id = %s"
            cursor.execute(quarry, [id])
            connection.commit()
            
            return True
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return False