from django.forms import ModelForm, DateTimeInput
from .models import ExpenseLedger


class ExpenseLedgerForm(ModelForm):
    class Meta:
        model = ExpenseLedger
        exclude = ['business', 'amount']

        widgets = {
            'date': DateTimeInput(attrs={'type': 'datetime-local'})
        } 
