from django.shortcuts import render
from django.template  import loader
from django.http      import HttpResponse
from .models import Fund, Commitment
from typing  import List, Dict


# Create your views here.


# def index(request):
#     return HttpResponse("Hello, world. You're at the capitalcallapp index.")

def index(request):
    Query_Set_All_Funds = Fund.objects.order_by('fund_number')[:]
    L_Funds: List[Dict] = [ fund.getDictionaryRepresentation() for fund in Query_Set_All_Funds ]
    dv = 0
    f_total_available_usd = sum([ D_Fund["f_current_balance_usd"] for D_Fund in L_Funds ])
    template = loader.get_template('capitalcallapp/home.html')
    context = {
        'L_Funds'              : L_Funds,
        "f_total_available_usd": f_total_available_usd
    }
    return HttpResponse(template.render(context, request))


