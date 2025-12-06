from django.db import models

# Create your models here.
class Capital(models.Model):
    business = models.ForeignKey('business.BusinessUser', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}: {self.amount}"


    
class CapitalTransaction(models.Model):
    capital = models.ForeignKey(Capital, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=50, choices=[('addition', 'Addition'), ('withdrawal', 'Withdrawal')])  # e.g., 'addition', 'withdrawal'
    transaction_account = models.CharField(max_length=100, choices=[('cash', 'Cash'), ('bank', 'Bank')])  # e.g., 'cash', 'bank', 'mobile_banking'
    amount = models.FloatField()
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} on {self.date}"
    
    def save(self, **kwargs):

        if self.transaction_type == 'addition':
            self.capital.amount += self.amount
        elif self.transaction_type == 'withdrawal':
            self.capital.amount -= self.amount

        self.capital.save()
        return super().save(**kwargs)