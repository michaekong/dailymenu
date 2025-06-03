from django.shortcuts import render

# Create your views here.
from django.shortcuts import render


def first(request):
    return render(request, 'first.html')
def dashboard(request):
    return render(request, 'dashboard.html')

