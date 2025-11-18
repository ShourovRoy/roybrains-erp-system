from django.db import models

ACCOUNT_TYPE_CHOICES = [
    ('Bank', 'Bank'),
    ('Vendor', 'Vendor'),
    ('Customer', 'Customer')
]

ACCOUNT_STATUS_CHOICES = [
    ('Dr', 'Debit'),
    ('Cr', 'Credit'),
    ('Balanced', 'Balanced')
]

# Create your models here.
class Ledger(models.Model):
    business = models.ForeignKey(to="business.BusinessUser", on_delete=models.CASCADE)
    account_name = models.CharField(max_length=255)
    address = models.TextField(max_length=400, blank=True, null=True)
    phone_number = models.CharField(max_length=14, blank=True, null=True)
    account_type = models.CharField(max_length=100, choices=ACCOUNT_TYPE_CHOICES, default="Customer")
    balance = models.FloatField(default=0.00)
    status = models.CharField(max_length=50, choices=ACCOUNT_STATUS_CHOICES, default="Balanced")
    note = models.TextField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['business', 'account_name', 'account_type'],
                name='unique_account_name_per_type_per_business'
            )
        ]

    def __str__(self):
        return f"{self.account_name} - {self.account_type} - {self.balance}"
    

class Transaction(models.Model):
    business = models.ForeignKey("business.BusinessUser", on_delete=models.CASCADE)
    ledger = models.ForeignKey("ledger.Ledger", on_delete=models.CASCADE)
    sell_voucher = models.ForeignKey("delivery_order.DeliveryOrder", on_delete=models.CASCADE, blank=True, null=True, unique=False)
    purchase_voucher = models.ForeignKey("purchase_record.PurchaseVoucher", on_delete=models.CASCADE, blank=True, null=True, unique=False)
    description = models.TextField(max_length=500, blank=True, null=True)
    debit = models.FloatField(default=0.00)
    credit = models.FloatField(default=0.00)
    balance = models.FloatField(default=0.00, blank=True, null=True)
    status = models.CharField(max_length=50, choices=ACCOUNT_STATUS_CHOICES, default="Balanced", blank=True, null=True)
    date = models.DateTimeField()

    

    def __str__(self):
        return f"{self.ledger.account_name} - {self.ledger.account_type} - Debit: {self.debit} Credit: {self.credit} Balance: {self.balance}"
    

    def save(self, **kwargs):

        ledger_entries = Transaction.objects.filter(ledger=self.ledger, business=self.business,).order_by('date', 'id').exclude(pk=self.pk)

        last_balance = ledger_entries.last().balance if ledger_entries.exists() else 0.00
        self.balance = last_balance + (self.debit - self.credit)
       
        self.status = "Dr" if self.balance > 0 else "Cr" if self.balance < 0 else "Balanced"

        note = self.ledger.note
        status = self.ledger.status

        if self.balance < 0 and self.ledger.account_type == "Vendor":
            note = "Payable"
            status = "Cr"
        elif self.balance > 0 and self.ledger.account_type == "Vendor":
            note = "Receivable"
            status = "Dr"
        elif self.balance < 0 and self.ledger.account_type == "Customer":
            note = "Payable"
            status = "Cr"
        elif self.balance > 0 and self.ledger.account_type == "Customer":
            note = "Receivable"
            status = "Dr"
        else:
            note = "Balanced"
            status = "Balanced"

        Ledger.objects.filter(pk=self.ledger.pk).update(balance=self.balance, note=note, status=status)

        # Update subsequent ledger transactions
        return super().save(**kwargs)
    
