from django.shortcuts import render
from django.http      import HttpResponse
from django.template  import loader
from .models          import Fund


# Create your views here.


# def index(request):
#     return HttpResponse("Hello, world. You're at the capitalcallapp index.")

def index(request):
    L_Funds = Fund.objects.order_by('-pub_date')[:5]
    template = loader.get_template('polls/index.html')
    context = {
        'L_Funds': L_Funds,
    }
    return HttpResponse(template.render(context, request))


