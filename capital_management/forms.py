from django.forms import ModelForm, formset_factory
from .models import CapitalTransaction, Capital



# capital transaction form
class CapitalTransactionForm(ModelForm):
    class Meta:
        model = CapitalTransaction
        fields = ['transaction_type', 'transaction_account', 'amount', 'description', 'date']


