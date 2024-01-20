from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.db import connection
from . import models



def Getfines(request):
    try:
        input_text = request.GET['text']
        if input_text:
            current_fines = models.Fines.objects.filter(fine_status='действует',title__icontains=input_text)
            return render(request, 'fines.html', {'data' : {
                'fines': current_fines,
                'search_v': input_text,
            }})
    except:
        return render(request, 'fines.html', {'data' : {
                'fines': models.Fines.objects.filter(fine_status='действует'),   
            }})

def Getfine(request, id):
    return render(request, 'fine.html', {'data' : {
        'id': id,
        'fine':models.Fines.objects.filter(fine_id=id).first(),
    }})



def Click_on_HideCard(request, id):
    HideCard(id)
    return redirect(reverse('fine_url'))


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