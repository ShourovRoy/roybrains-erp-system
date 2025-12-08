from django.db import models

# Create your models here.
class Capital(models.Model):
    business = models.ForeignKey('business.BusinessUser', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    balance = models.FloatField(default=0.0, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}: {self.balance}"
    
    def save(self, **kwargs):

        self.name = self.business.owner_name + " Capital"

        return super().save(**kwargs)


    
class CapitalTransaction(models.Model):
    business = models.ForeignKey('business.BusinessUser', on_delete=models.CASCADE, blank=True, null=True)
    capital = models.ForeignKey(Capital, on_delete=models.CASCADE)
    balance = models.FloatField(default=0.0, blank=True, null=True)
    debit = models.FloatField(default=0.0, blank=True, null=True)
    credit = models.FloatField(default=0.0, blank=True, null=True)
    status = models.CharField(max_length=50, choices=[('debit', 'Debit'), ('credit', 'Credit')], blank=True, null=True)  # e.g., 'debit', 'credit'
    description = models.TextField(max_length=500, blank=True, null=True)
    date = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.business.owner_name} of {self.balance} on {self.date}"
    
    def save(self, **kwargs):


        capital_entries = CapitalTransaction.objects.filter(
            business=self.business,
            capital=self.capital
        ).order_by('date', 'id').exclude(pk=self.pk)

        last_capital_transaction_balance = capital_entries.last().balance if capital_entries.exists() else 0.00;

        self.balance = last_capital_transaction_balance + (self.debit - self.credit)


        # update the balance of capital
        self.capital.balance = self.balance
        self.capital.save()

        if self.balance < 0:
            self.status = 'debit'
        elif self.balance > 0:
            self.status = 'credit'
        else:
            self.status = 'balanced'

        return super().save(**kwargs)