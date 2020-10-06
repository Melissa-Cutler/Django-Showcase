from django.forms import forms
from django.shortcuts import render
from django.template  import loader
from django.http      import HttpResponse
from datetime import datetime
from .models  import Fund, Commitment
from typing   import List, Dict
import pytz


# Create your views here.


# def index(request):
#     return HttpResponse("Hello, world. You're at the capitalcallapp index.")

def index(request):
    Query_Set_All_Funds = Fund.objects.order_by('fund_number')[:]
    L_Funds: List[Dict] = [ fund.getDictionaryRepresentation() for fund in Query_Set_All_Funds ]
    f_total_available_usd = sum([ D_Fund["f_current_balance_usd"] for D_Fund in L_Funds ])
    template = loader.get_template('capitalcallapp/home.html')
    context = {
        'L_Funds'              : L_Funds,
        "f_total_available_usd": f_total_available_usd
    }
    return HttpResponse(template.render(context, request))


def newInvestment(request):
    Post_Data = request.POST
    f_new_investment_amount_usd = float(Post_Data["new-investment-amount"])
    L_Funds: List[Fund]         = [ fund for fund in Fund.objects.order_by('fund_number')[:] ]
    L_Fund_Dicts: List[Dict]    = [ fund.getDictionaryRepresentation() for fund in L_Funds   ]
    f_total_available_usd = sum([ D_Fund["f_current_balance_usd"] for D_Fund in L_Fund_Dicts ])
    if f_total_available_usd < f_new_investment_amount_usd:
        raise forms.ValidationError("You cannot invest more than the total available money!")
    Dt_New_Investment_Date = datetime.strptime(
        Post_Data["new-investment-date"] + " 12:00:00 GMT", "%Y-%m-%d %H:%M:%S %Z"
    )
    timezone = pytz.timezone("UTC")
    Dt_New_Investment_Date = timezone.localize(Dt_New_Investment_Date)
    L_Most_Recent_Commitments: List[Commitment] = [ fund.L_Commitments_To_This_Fund[-1] for fund in L_Funds ]
    L_Most_Recent_Commitments.sort(key=lambda commitment: commitment.date)
    dv = 0
    if Dt_New_Investment_Date < L_Most_Recent_Commitments[-1].date:
        raise forms.ValidationError(
            "Time travel is strictly forbidden! You cannot add an to investment prior to the most recent commitment!"
        )
    dv = 0


    return HttpResponse("Hello, world. You hit the New Investment end point!")


