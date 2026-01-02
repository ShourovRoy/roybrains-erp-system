from django.db import models

# Create your models here.
class CashBook(models.Model):
    business = models.ForeignKey("business.BusinessUser", on_delete=models.CASCADE)
    cash_amount = models.FloatField(default=0.0, blank=True, null=True)
    bank_amount = models.FloatField(default=0.0, blank=True, null=True)
    status = models.CharField(max_length=10, blank=False, null=False)
    note = models.CharField(max_length=255, blank=True, null=True)

    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id.__str__()


    def save(self, **kwargs):

        if self.cash_amount > 0.0:
            self.note = f"You have {self.cash_amount} cash available now."


        return super().save(**kwargs)
    
class CashTransaction(models.Model):
    business = models.ForeignKey("business.BusinessUser", on_delete=models.CASCADE)
    cashbook = models.ForeignKey(CashBook, on_delete=models.CASCADE)
    description = models.TextField(max_length=255)
    is_bank = models.BooleanField(default=False, blank=True, null=True)
    debit = models.FloatField(default=0.0)
    credit = models.FloatField(default=0.0)
    date = models.DateTimeField()


    def __str__(self):
        return str(self.debit)
    
