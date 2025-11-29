from django.db import models

# TODO: work on cash book
# TODO: challange, per day cashbook with previous day balance 
# Create your models here.
class CashBook(models.Model):
    business = models.ForeignKey("business.BusinessUser", on_delete=models.CASCADE)
    cash_amount = models.FloatField(default=0.0, blank=True, null=True)
    status = models.CharField(max_length=10, blank=False, null=False)
    note = models.CharField(max_length=255, blank=True, null=True)

    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, **kwargs):

        if self.cash_amount > 0.0:
            self.note = f"You have {self.cash_amount} cash available now."


        return super().save(**kwargs)
    
class CashTransaction(models.Model):
    business = models.ForeignKey("business.BusinessUser", on_delete=models.CASCADE)
    cashbook = models.ForeignKey(CashBook, on_delete=models.CASCADE)
    description = models.TextField(max_length=255)
    debit = models.FloatField(default=0.0)
    credit = models.FloatField(default=0.0)


    date = models.DateField()
