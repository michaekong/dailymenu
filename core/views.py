from django.shortcuts import render

# Create your views here.
from django.shortcuts import render


def first(request):
    
    status = request.GET.get('status')
    context = {"status": status}
    return render(request, "first.html", context)
    
def dashboard(request):
    return render(request, 'dashboard.html')

