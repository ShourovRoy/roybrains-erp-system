from django.forms import ModelForm
from .models import ExpenseType


class ExpenseTypeForm(ModelForm):
    class Meta:
        model = ExpenseType
        exclude = ['business', 'amount']
