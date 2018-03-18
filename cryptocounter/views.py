from django.shortcuts import render

# Create your views here.
def market(request):
    return render(request, 'cryptocounter/market.html')

def ico(request):
    return render(request, 'cryptocounter/ico.html')

def socialTrends(request):
    return render(request, 'cryptocounter/trends.html')

def watchlist(request):
    return render(request, 'cryptocounter/watchlist.html')

def login(request):
    return render(request, 'cryptocounter/index.html')

def register(request):
    return render(request, 'cryptocounter/register.html')

def header(request):
    return render(request, 'cryptocounter/header.html')

def footer(request):
    return render(request, 'cryptocounter/footer.html')
