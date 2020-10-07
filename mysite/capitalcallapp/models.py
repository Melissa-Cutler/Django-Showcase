from django.utils import timezone
from django.db    import models
from datetime     import datetime
from typing import List, Dict


# Create your models here.


class Fund(models.Model):
    # I think that Django takes care of creating the id field under the hood
    # fund_id: models.IntegerField(default=0)
    fund_number    : models.query_utils.DeferredAttribute = models.IntegerField(unique=True)
    initial_balance: models.query_utils.DeferredAttribute = models.FloatField(  default=0  )

    def __init__(self, *args, **kwargs):
        self.fund_number    : int
        self.initial_balance: float
        self.id     : int
        self.objects: str
        self.pk     : int
        super().__init__(*args, **kwargs)
        self.L_Commitments_To_This_Fund: List[Commitment] = [
            commitment for commitment in Commitment.objects.filter(fund=self)
        ]
        self.L_Commitments_To_This_Fund.sort(key=lambda commitment: commitment.date)

        # TODO: This code currently assumes that all of the money provided by all commitments remains available.  IE is
        # does not take into account existing calls that will soon be added to the DB!!!
        L_Commitment_Amounts_Usd_f: List[float] = [
            commitment.amount_usd for commitment in self.L_Commitments_To_This_Fund
        ]
        # TODO: This code currently assumes that all of the money provided by all commitments remains available.  IE is
        # does not take into account existing calls that will soon be added to the DB!!!
        self.f_current_balance_usd: float  = self.initial_balance + sum(L_Commitment_Amounts_Usd_f)

        return

    def getDictionaryRepresentation(self):
        D_Output = {
            "s_name"               : "fund" + str(self.fund_number),
            "f_current_balance_usd": self.f_current_balance_usd
            # "L_Commitment_Dictss" : []
        }
        return D_Output

    def __str__(self) -> str:
        return "< fund" + str(self.fund_number) + ": $" + str(self.f_current_balance_usd) + ">"

    def __repr__(self) -> str:
        return "< fund" + str(self.fund_number) + ": $" + str(self.f_current_balance_usd) + ">"

# ass Fund(models.Model)


# A class to describe commitments to funds
class Commitment(models.Model):
    # commitment_id: models.Field = models.IntegerField(default=0)
    # fund_id      :   models.ForeignKey(Fund, on_delete=models.CASCADE)
    commitment_number: models.Field                  = models.IntegerField(unique=True)
    fund      : models.ForeignObject                 = models.ForeignKey(Fund, on_delete=models.CASCADE)
    date      : models.query_utils.DeferredAttribute = models.DateTimeField('date of commitment')
    amount_usd: models.Field                         = models.FloatField(default=0.0)

    def __str__(self) -> str:
        return "$" + str(self.amount_usd) + " to fund" + str(self.fund.fund_number) + " on " + str(self.date)


# a class to describe investments from funds
class Investment(models.Model):
    investment_number: models.Field                         = models.IntegerField(unique=True)
    date             : models.query_utils.DeferredAttribute = models.DateTimeField('date of investment')
    amount_usd       : models.Field                         = models.FloatField(default=0.0)

    def __str__(self) -> str:
        return "$" + str(self.amount_usd) + " on " + str(self.date)

    @staticmethod
    def createWithCalls(f_new_investment_amount_usd: float, Dt_New_Investment_Date: datetime) -> "Investment":
        L_Funds     : List[Fund]     = [fund for fund in Fund.objects.order_by('fund_number')[:]]
        L_Fund_Dicts: List[Dict]     = [fund.getDictionaryRepresentation() for fund in L_Funds  ]
        f_total_available_usd: float = sum([D_Fund["f_current_balance_usd"] for D_Fund in L_Fund_Dicts])
        assert f_new_investment_amount_usd <= f_total_available_usd
        L_Most_Recent_Commitments: List[Commitment] = [fund.L_Commitments_To_This_Fund[-1] for fund in L_Funds]
        L_Most_Recent_Commitments.sort(key=lambda commitment: commitment.date)
        assert L_Most_Recent_Commitments[-1].date < Dt_New_Investment_Date


        #L_Funds: List[Fund] = [fund for fund in Fund.objects.order_by('fund_number')[:]]

        # number to call to close down JSA application: 0800 169 0310

        # recall all existing investments from the DB, order by number, select highest, add one!
        Query_Set_All_Investments = Investment.objects.order_by('investment_number')[:]
        L_All_Existing_Investments: List[Investment] = [ investment for investment in Query_Set_All_Investments ]
        i_new_investment_number = len(L_All_Existing_Investments) + 1
        New_Investment = Investment(
            investment_number=i_new_investment_number,
            amount_usd=f_new_investment_amount_usd,
            date=Dt_New_Investment_Date
        )
        f_remaining_amount_needed = f_new_investment_amount_usd
        Query_Set_All_Commitments = Commitment.objects.order_by('date')[:]
        L_Calls: List[Call] = []
        New_Investment.save()
        for commitment in Query_Set_All_Commitments:
            # TODO: Check that this commitment has a non-zero remaining balance
            if f_remaining_amount_needed < commitment.amount_usd:
                # TODO: create a call of size f_remaining_amount_needed
                New_Call = Call()
                dv = 0
                # then exit the for loop
                L_Calls.append( Call(
                        amount_usd=f_remaining_amount_needed,
                        fund=commitment.fund,
                        commitment=commitment,
                        investment=New_Investment,
                        date=Dt_New_Investment_Date
                ) )
                f_remaining_amount_needed = 0
                break
            else:
                # TODO: create a new call of the size of the commitment
                dv = 0
                L_Calls.append( Call(
                        amount_usd=commitment.amount_usd,
                        fund=commitment.fund,
                        commitment=commitment,
                        investment=New_Investment,
                        date=Dt_New_Investment_Date
                ) )
                f_remaining_amount_needed -= commitment.amount_usd
            #
        # r commitment in Query_Set_All_Commitments

        # We've now created a list of Calls that meet this investment.
        # We should save them to the DB, save our new investment to the DV, and return our new investment to the
        # caller views.py which must prepare the responds, reporting the answer.
        [ call.save() for call in L_Calls ]
        return New_Investment



# ass Investment(models.Model)


# a call describes an amount of money being called from a fund/commitment and used towards an investment
#remane this class to calls from commitments, and create a new class (calls from funds) to group calls from the same fund
class Call(models.Model):
    amount_usd   : models.Field                         = models.FloatField(default=0)
    fund         : models.ForeignObject                 = models.ForeignKey(Fund,       on_delete=models.CASCADE)
    commitment                                          = models.ForeignKey(Commitment, on_delete=models.CASCADE)
    investment   : models.ForeignObject                 = models.ForeignKey(Investment, on_delete=models.CASCADE)
    date         : models.query_utils.DeferredAttribute = models.DateTimeField('date of call')

    def __str__(self) -> str:
        #return "$" + str(self.amount_usd) + " from fund" + str(self.fund.fund_number) + " to investment" + str(self.investment_number) + " on " + str(self.date)
        return " ".join([
            "$" + str(self.amount_usd), "from", "fund" + str(self.fund.fund_number),
            "to", "investment" + str(self.investment.investment_number), "on", str(self.date)
        ])



