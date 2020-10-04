from django.db    import models
from django.utils import timezone

# Create your models here.


class Fund(models.Model):
    # I think that Django takes care of creating the id field under the hood
    # fund_id: models.IntegerField(default=0)
    fund_number    : models.Field = models.IntegerField(default=0)
    current_balance: models.Field = models.FloatField(  default=0)

    def __str__(self):
        return str(self.fund_number) + ", balance $" + str(self.current_balance)

# A class to describe commitments to funds
class Commitment(models.Model):
    # commitment_id: models.Field = models.IntegerField(default=0)
    # fund_id      :   models.ForeignKey(Fund, on_delete=models.CASCADE)
    fund         : models.ForeignObject = models.ForeignKey(Fund, on_delete=models.CASCADE)
    date         : models.Field         = models.DateTimeField('date of commitment')
    amount_usd   : models.Field         = models.FloatField(default=0.0)


# a class to describe investments from funds
class Investment(models.Model):
    date      : models.Field = models.DateTimeField('date of investment')
    amount_usd: models.Field = models.FloatField(default=0.0)



# a call, describes an amount of money being called from a commitment and used towards an investment
class Call(models.Model):
    amount_usd   : models.Field         = models.FloatField(default=0)
    fund_id      : models.ForeignObject = models.ForeignKey(Commitment, on_delete=models.CASCADE)
    investment_id: models.ForeignObject = models.ForeignKey(Investment, on_delete=models.CASCADE)


