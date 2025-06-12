from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

from django.shortcuts import render, redirect

def first(request):
    
    
   
    status = request.GET.get('status')
    context = {"status": status} 
    return render(request, "first.html", context)
    
def dashboard(request):
   
    return render(request, 'dashboard.html')
from django.http import JsonResponse
from django.conf import settings

def share_menu_view(request, menu_id):
    
    return render(request, 'client.html')


