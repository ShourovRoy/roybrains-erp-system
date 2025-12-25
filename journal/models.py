from django.db import models
from ledger.models import Ledger
from expense_record.models import ExpenseLedger


# Create your models here.
class JournalBook(models.Model):
    business= models.ForeignKey("business.BusinessUser", on_delete=models.CASCADE)
    total_debit = models.FloatField(default=0.00, blank=True, null=True)
    total_credit = models.FloatField(default=0.00, blank=True, null=True)

    date = models.DateTimeField()


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Journal of {self.business.business_name} - Journal id {self.id}"
    

class JournalTransaction(models.Model):
    business= models.ForeignKey("business.BusinessUser", on_delete=models.CASCADE)
    journal = models.ForeignKey(JournalBook, on_delete=models.CASCADE)
    date = models.DateTimeField()
    ledger_ref = models.ForeignKey(Ledger, on_delete=models.CASCADE, blank=True, null=True)
    expense_ref = models.ForeignKey(ExpenseLedger, on_delete=models.CASCADE, blank=True, null=True)
    debit = models.FloatField(default=0.00, blank=True, null=True)
    credit = models.FloatField(default=0.00, blank=True, null=True)
    description = models.CharField(max_length=150)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.business.business_name} - journal id: {self.journal.pk} - record id :{self.pk}"
    

    def save(self, **kwargs):

        # increment journal book debit
        self.journal.total_debit += float(self.debit)
        

        # increment journal book credit
        self.journal.total_credit += float(self.credit)

        # save the journal
        self.journal.save()

        return super().save(**kwargs)