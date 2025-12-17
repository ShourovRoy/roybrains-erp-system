from django.forms import ModelForm
from .models import ExpenseLedger


class ExpenseLedgerForm(ModelForm):
    class Meta:
        model = ExpenseLedger
        exclude = ['business', 'amount']
