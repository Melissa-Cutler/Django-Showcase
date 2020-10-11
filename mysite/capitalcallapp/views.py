from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect, render
from django.template  import loader
from django.forms     import forms
from django.http      import HttpResponse
from datetime import datetime, timedelta
from .models  import Fund, Commitment, Investment
from typing   import List, Dict
import pytz


# Create your views here.


def cleanDatabase(request: WSGIRequest) -> HttpResponse:
    Query_Set_All_Funds = Fund.objects.order_by('fund_number')[:]
    [ fund.delete() for fund in Query_Set_All_Funds ]
    Query_Set_All_Investments = Investment.objects.order_by('investment_number')[:]
    [ investment.delete() for investment in Query_Set_All_Investments ]
    return redirect('/capitalcallapp/')
# f newCommitment(request) -> HttpResponse



def index(request: WSGIRequest) -> HttpResponse:
    Query_Set_All_Funds    = Fund.objects.order_by('fund_number')[:]
    l_funds: List[Dict]    = [ fund.getDictionaryRepresentation() for fund in Query_Set_All_Funds ]
    f_total_available_usd  = sum([ D_Fund["f_current_balance_usd"] for D_Fund in l_funds ])
    L_Fund_Summary_Strings = [
        "".join([
                D_Fund["s_name"], ": $", str(D_Fund["f_total_committed"]), " committed, $",
                str(D_Fund["f_current_balance_usd"]) + " still available"
        ]) for D_Fund in l_funds
    ]
    template = loader.get_template('capitalcallapp/home.html')
    L_Most_Recent_Commitments: List[Commitment] = [
        fund.L_Commitments_To_This_Fund[-1] for fund in Query_Set_All_Funds
    ]
    L_Most_Recent_Commitments.sort(key=lambda commitment: commitment.date)
    if len(L_Most_Recent_Commitments) == 0:
        Dt_Earliest_Permitted_Investment = datetime(1, 1, 1)
    else:
        Dt_Earliest_Permitted_Investment = L_Most_Recent_Commitments[-1].date + timedelta(days=1)
    context = {
        'l_funds'               : l_funds,
        'L_Fund_Summary_Strings': L_Fund_Summary_Strings,
        "f_total_available_usd" : f_total_available_usd,
        "s_min_allowed_date"    : Dt_Earliest_Permitted_Investment.strftime("%Y-%m-%d")
    }
    return HttpResponse(template.render(context, request))
# f index(request) -> HttpResponse


def newCommitment(request: WSGIRequest) -> HttpResponse:
    d_new_commitment        = request.POST
    f_new_commitment_amount = float(d_new_commitment["new-commitment-amount"])
    dt_new_commitment_date  = datetime.strptime(
        d_new_commitment["new-commitment-date"] + " 12:00:00 GMT", "%Y-%m-%d %H:%M:%S %Z"
    )
    timezone = pytz.timezone("UTC")
    dt_new_commitment_date = timezone.localize(dt_new_commitment_date)
    i_target_fund_num      = int(d_new_commitment["fund-selection"])
    query_set_all_funds    = Fund.objects.order_by('fund_number')[:]
    l_funds: List[Fund]    = [ fund for fund in query_set_all_funds ]
    #
    if i_target_fund_num == 0:
        fund = Fund(fund_number=(len(l_funds)+1))
        fund.save()
    else:
        fund = l_funds[i_target_fund_num - 1]
    #  i_target_fund_num...
    query_set_all_commitments = Commitment.objects.order_by("commitment_number")
    l_all_commitments: List[Commitment] = [ commitment for commitment in query_set_all_commitments ]
    new_commitment = Commitment(
        commitment_number=(len(l_all_commitments)+1),
        fund=fund,
        initial_amount_usd=f_new_commitment_amount,
        date=dt_new_commitment_date
    )
    new_commitment.save()
    return redirect('/capitalcallapp/')
# f newCommitment(request) -> HttpResponse


def newInvestment(request: WSGIRequest) -> HttpResponse:
    Post_Data = request.POST
    f_new_investment_amount_usd = float(Post_Data["new-investment-amount"])
    l_funds: List[Fund]         = [ fund for fund in Fund.objects.order_by('fund_number')[:] ]
    L_Fund_Dicts: List[Dict]    = [ fund.getDictionaryRepresentation() for fund in l_funds   ]
    f_total_available_usd = sum([ D_Fund["f_current_balance_usd"] for D_Fund in L_Fund_Dicts ])
    if f_total_available_usd < f_new_investment_amount_usd:
        raise forms.ValidationError("You cannot invest more than the total available money!")
    Dt_New_Investment_Date = datetime.strptime(
        Post_Data["new-investment-date"] + " 12:00:00 GMT", "%Y-%m-%d %H:%M:%S %Z"
    )
    timezone = pytz.timezone("UTC")
    Dt_New_Investment_Date = timezone.localize(Dt_New_Investment_Date)
    L_Most_Recent_Commitments: List[Commitment] = [ fund.L_Commitments_To_This_Fund[-1] for fund in l_funds ]
    L_Most_Recent_Commitments.sort(key=lambda commitment: commitment.date)
    if Dt_New_Investment_Date < L_Most_Recent_Commitments[-1].date:
        raise forms.ValidationError(
            "Time travel is strictly forbidden! You cannot add an to investment prior to the most recent commitment!"
        )
    #  Dt_New_Investment_Date < L_Most_Recent_Commitments[-1].date
    investment_new = Investment.createWithCalls(f_new_investment_amount_usd, Dt_New_Investment_Date)
    l_call_dicts   = [ call.getDictionaryRepresentation() for call in investment_new.L_Calls_From_Commitments ]
    template       = loader.get_template('capitalcallapp/investment-created.html')
    context        = {
        's_new_investment_name'   : "Investment" + str(investment_new.investment_number),
        "f_total_available_usd"   : f_total_available_usd,
        "i_num_commitments_called": len(l_call_dicts)    ,
        "l_call_dicts"            : l_call_dicts
    }
    return HttpResponse(template.render(context, request))
# f newInvestment(request) -> HttpResponse


