from django.db import models


EXPENSE_LEDGER_TRANSACTION_STATUS_CHOICES = [
    ('Dr', 'Debit'),
    ('Cr', 'Credit'),
    ('Balanced', 'Balanced')
]

# Create your models here.
# Expense type model
class ExpenseLedger(models.Model):
    business = models.ForeignKey('business.BusinessUser', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=False)
    description = models.TextField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.business.owner_name}"
    
    def save(self, **kwargs):

        self.name = self.name.capitalize()

        return super().save(**kwargs)
    

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['business', 'name'],
                name='unique_expense_ledger_per_business'
            )
        ]


# Expense ledger transaction model
class ExpenseLedgerTransaction(models.Model):
    business=models.ForeignKey("business.BusinessUser", on_delete=models.CASCADE)
    expense_ledger = models.ForeignKey(ExpenseLedger, on_delete=models.CASCADE)
    description = models.CharField(max_length=255, blank=False, null=False)
    debit = models.FloatField(default=0.00, blank=True, null=True)
    credit = models.FloatField(default=0.00, blank=True, null=True)
    balance = models.FloatField(default=0.00, blank=True, null=True)
    status = models.CharField(max_length=255, choices=EXPENSE_LEDGER_TRANSACTION_STATUS_CHOICES, default="Balanced", blank=True, null=True)

    def __str__(self):
        return f"{self.expense_ledger.name} - {self.business.owner_name}"
