# from django.shortcuts import render
from django.template  import loader
from django.forms     import forms
from django.http      import HttpResponse
from datetime import datetime, timedelta
from .models  import Fund, Commitment, Investment
from typing   import List, Dict
import pytz


# Create your views here.


# def index(request):
#     return HttpResponse("Hello, world. You're at the capitalcallapp index.")

def index(request) -> HttpResponse:
    Query_Set_All_Funds    = Fund.objects.order_by('fund_number')[:]
    L_Funds: List[Dict]    = [ fund.getDictionaryRepresentation() for fund in Query_Set_All_Funds ]
    f_total_available_usd  = sum([ D_Fund["f_current_balance_usd"] for D_Fund in L_Funds ])
    L_Fund_Summary_Strings = [
        "".join([
                D_Fund["s_name"], ": $", str(D_Fund["f_total_committed"]), " committed, $",
                str(D_Fund["f_current_balance_usd"]) + " still available"
        ]) for D_Fund in L_Funds
    ]
    template = loader.get_template('capitalcallapp/home.html')
    L_Most_Recent_Commitments: List[Commitment] = [
        fund.L_Commitments_To_This_Fund[-1] for fund in Query_Set_All_Funds
    ]
    L_Most_Recent_Commitments.sort(key=lambda commitment: commitment.date)
    if len(L_Most_Recent_Commitments) == 0:
        dv = 0
        Dt_Earliest_Permitted_Investment = datetime(1, 1, 1)
    else:
        Dt_Earliest_Permitted_Investment = L_Most_Recent_Commitments[-1].date + timedelta(days=1)
    context = {
        'L_Funds'               : L_Funds,
        'L_Fund_Summary_Strings': L_Fund_Summary_Strings,
        "f_total_available_usd" : f_total_available_usd,
        "s_min_allowed_date"    : Dt_Earliest_Permitted_Investment.strftime("%Y-%m-%d")
    }
    return HttpResponse(template.render(context, request))
# f index(request) -> HttpResponse


def newCommitment(request) -> HttpResponse:
    D_New_Commitment = request.POST
    f_new_commitment_amount = float(D_New_Commitment["new-commitment-amount"])
    dt_new_commitment_date = datetime.strptime(
        D_New_Commitment["new-commitment-date"] + " 12:00:00 GMT", "%Y-%m-%d %H:%M:%S %Z"
    )
    timezone = pytz.timezone("UTC")
    dt_new_commitment_date = timezone.localize(dt_new_commitment_date)
    i_target_fund_num = int(D_New_Commitment["fund-selection"])
    Query_Set_All_Funds = Fund.objects.order_by('fund_number')[:]
    L_Funds: List[Fund] = [ fund for fund in Query_Set_All_Funds ]
    #
    if i_target_fund_num == -1:
        fund = Fund(fund_number=(len(L_Funds)+1))
        fund.save()
    else:
        fund = L_Funds[i_target_fund_num]
    #  i_target_fund_num...
    Query_Set_All_Commitments = Commitment.objects.order_by("commitment_number")
    L_All_Commitments: List[Commitment] = [ commitment for commitment in Query_Set_All_Commitments ]
    new_commitment = Commitment(
        commitment_number=(len(L_All_Commitments)+1),
        fund=fund,
        initial_amount_usd=f_new_commitment_amount,
        date=dt_new_commitment_date
    )
    new_commitment.save()
    return HttpResponse("Commitment created!")
# f newCommitment(request) -> HttpResponse


def newInvestment(request) -> HttpResponse:
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
    if Dt_New_Investment_Date < L_Most_Recent_Commitments[-1].date:
        raise forms.ValidationError(
            "Time travel is strictly forbidden! You cannot add an to investment prior to the most recent commitment!"
        )
    #  Dt_New_Investment_Date < L_Most_Recent_Commitments[-1].date
    investment_new = Investment.createWithCalls(f_new_investment_amount_usd, Dt_New_Investment_Date)
    L_Call_Dicts   = [ call.getDictionaryRepresentation() for call in investment_new.L_Calls_From_Commitments ]
    template       = loader.get_template('capitalcallapp/investment-created.html')
    context        = {
        's_new_investment_name'   : "Investment" + str(investment_new.investment_number),
        "f_total_available_usd"   : f_total_available_usd,
        "i_num_commitments_called": len(L_Call_Dicts)    ,
        "L_Call_Dicts"            : L_Call_Dicts
    }
    return HttpResponse(template.render(context, request))
# f newInvestment(request) -> HttpResponse


