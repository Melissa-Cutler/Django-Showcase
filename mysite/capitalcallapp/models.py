from django.db import models
from typing    import List
from django.utils import timezone


# Create your models here.


class Fund(models.Model):
    # I think that Django takes care of creating the id field under the hood
    # fund_id: models.IntegerField(default=0)
    fund_number    : models.query_utils.DeferredAttribute = models.IntegerField(unique=True)
    initial_balance: models.query_utils.DeferredAttribute = models.FloatField(default=0)

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
        L_Commitment_Amounts_Usd_f: List[float] = [
            commitment.amount_usd for commitment in self.L_Commitments_To_This_Fund
        ]
        self.f_current_balance_usd: float  = self.initial_balance + sum(L_Commitment_Amounts_Usd_f)
        return

    def getDictionaryRepresentation(self):
        D_Output = {
            "s_name"               : "fund" + str(self.fund_number),
            "f_current_balance_usd": self.f_current_balance_usd
            # "L_Commitments"        : []
        }
        return D_Output

    def __str__(self) -> str:
        return "< fund" + str(self.fund_number) + ": $" + str(self.f_current_balance_usd) + ">"

    def __repr__(self) -> str:
        return "< fund" + str(self.fund_number) + ": $" + str(self.f_current_balance_usd) + ">"


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


# a call describes an amount of money being called from a fund/commitment and used towards an investment
class Call(models.Model):
    commitment_number                                   = models.IntegerField()
    investment_number                                   = models.IntegerField()
    amount_usd   : models.Field                         = models.FloatField(default=0)
    fund         : models.ForeignObject                 = models.ForeignKey(Fund,       on_delete=models.CASCADE)
    investment   : models.ForeignObject                 = models.ForeignKey(Investment, on_delete=models.CASCADE)
    date         : models.query_utils.DeferredAttribute = models.DateTimeField('date of call')

    def __str__(self) -> str:
        #return "$" + str(self.amount_usd) + " from fund" + str(self.fund.fund_number) + " to investment" + str(self.investment_number) + " on " + str(self.date)
        return " ".join([
            "$" + str(self.amount_usd), "from", "fund" + str(self.fund.fund_number),
            "to", "investment" + str(self.investment_number), "on", str(self.date)
        ])



