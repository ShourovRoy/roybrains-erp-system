from django.forms import ModelForm, TextInput, Select
from .models import Ledger, ACCOUNT_TYPE_CHOICES

class LedgerForm(ModelForm):
    class Meta():
        model = Ledger
        fields = ["account_name", "account_type", "phone_number", "address", "branch", "bank_account_number"]
        widgets = {
            "account_name": TextInput(attrs={'class': 'form-control'}),
            "account_type": Select(attrs={'class': 'form-select'}, choices=ACCOUNT_TYPE_CHOICES),
            "phone_number": TextInput(attrs={'class': 'form-control'}),
            "address": TextInput(attrs={'class': 'form-control'}),
            "branch": TextInput(attrs={'class': 'form-control'}),   
            "bank_account_number": TextInput(attrs={'class': 'form-control'})
        }