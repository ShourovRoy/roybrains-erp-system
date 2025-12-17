from django.db import models


EXPENSE_TRANSACTION_STATUS_CHOICES = [
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.business.owner_name}"
    

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['business', 'name'],
                name='unique_expense_ledger_per_business'
            )
        ]
